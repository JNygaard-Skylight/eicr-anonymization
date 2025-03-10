"""Main module for the EICR anonymization tool."""

import argparse
import glob
import logging
import os
import re

from tabulate import tabulate

from data_cache.main import DataCache
from random_sw.main import (
    get_random_family_name,
    get_random_given_name,
    get_random_name_prefix,
    get_random_name_suffix,
    get_random_street_address_line,
)

logger = logging.getLogger(__name__)


def _get_args():
    parser = argparse.ArgumentParser(description="Anonymize EICR data")
    parser.add_argument("input_location", help="Location of the input EICR files")
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Print replacement value for each field. E.g. Joe Bloggs -> Bobba Fett",
    )

    return parser.parse_args()


def main():
    """Anonymize EICR data."""
    args = _get_args()

    # Remove previous anonymization output files
    previous_output_files = glob.glob(os.path.join(args.input_location, "*.anonymized.xml"))
    for output_file in previous_output_files:
        os.remove(output_file)

    # Read XML files from input location
    input_location = args.input_location
    xml_files = glob.glob(os.path.join(input_location, "*.xml"))

    for xml_file in xml_files:
        with open(xml_file) as file:
            xml_text = file.read()
        updated_xml = simple_replacement_regex(xml_text, debug=args.debug)

        with open(f"{xml_file}.anonymized.xml", "w", encoding="utf-8") as f:
            f.write(updated_xml)


def parse_attributes(tag: str) -> dict:
    """Extract attributes from an XML tag string into a dictionary.

    For example, from:
        <prefix bar="FIZZ" other="BUZZ">
    it returns:
        {"bar": "FIZZ", "other": "BUZZ"}.
    """
    return dict(re.findall(r'([\w:.-]+)\s*=\s*["\'](.*?)["\']', tag))


def normalize_text(text: str, data_cache: dict) -> str:
    """Normalize text by removing punctuation and converting to lowercase."""
    text = text.lower().replace(".", "")
    return text


def simple_replacement_regex(xml_text: str, debug: bool = False) -> str:
    """Replace sensitive fields in an EICR XML file using regex."""
    sensitive_fields = [
        ("family", get_random_family_name),
        ("given", get_random_given_name),
        ("prefix", get_random_name_prefix),
        ("suffix", get_random_name_suffix),
        ("streetAddressLine", get_random_street_address_line),
    ]
    data_caches = {}
    for tag, get_random_value in sensitive_fields:
        data_caches[tag] = DataCache()
        pattern = re.compile(
            rf"(<(?:\w+:)?{tag}\b[^>]*>)(.*?)(?:(</(?:\w+:)?{tag}>)|(/>))", re.DOTALL
        )

        def repl(match, *, get_random_value=get_random_value, data_cache=data_caches[tag]):
            open_tag, inner_text, closing_tag, self_close = match.groups()
            if self_close is not None:
                # Leave self-closing tags unchanged.
                return match.group(0)

            attributes = parse_attributes(open_tag)

            new_value = data_cache.get(inner_text)
            if new_value is None:
                stripped_inner_text = inner_text.strip()
                base_replacement_value = get_random_value(stripped_inner_text, attributes)
                new_value = data_cache.set_new(
                    key=inner_text,
                    base_replacement_value=base_replacement_value,
                )

            data_cache.set(key=inner_text, replacement_value=new_value)
            return f"{open_tag}{new_value}{closing_tag}"

        xml_text, count = pattern.subn(repl, xml_text)
        print(f"Replaced {count} instances of {len(data_caches[tag])} unique <{tag}> values ")

    if debug:
        for tag, data_cache in data_caches.items():
            print(f"Tag: {tag}")
            for normalized_value, data in data_cache.items():
                print(f"Normalized Value:\t`{normalized_value}`")
                print(f"Norm replacement:\t`{data['normized_replacement']}`")
                print(f"Instances replaced: {len(data['replacements'])}")
                depublicated_replacements = []
                added_replacements = set()
                for replacement in data["replacements"]:
                    if replacement not in added_replacements:
                        depublicated_replacements.append(
                            (f"`{replacement[0]}`", f"`{replacement[1]}`")
                        )
                        added_replacements.add(replacement)
                    else:
                        continue

                print(
                    tabulate(
                        depublicated_replacements,
                        headers=["Orginal", "Replacement"],
                        tablefmt="outline",
                    )
                )
                print()
    return xml_text


if __name__ == "__main__":
    main()
