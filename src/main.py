"""Main module for the EICR anonymization tool."""

import argparse
import glob
import logging
import os
import re

from tabulate import tabulate

from DataCache import DataCache, TagCache
from tags.Tag import Tag

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


def print_replacements(replacement_mappings: dict):
    """Print debug information for a given tag."""
    print(
        tabulate(
            replacement_mappings.items(),
            headers=["Orginal", "Replacement"],
            tablefmt="outline",
        )
    )


def simple_replacement_regex(xml_text: str, debug: bool = False) -> str:
    """Replace sensitive fields in an EICR XML file using regex."""
    data_caches = DataCache()
    for tag_name in Tag.get_registry():
        pattern = re.compile(
            rf"(<(?:\w+:)?{tag_name}\b[^>]*>)(.*?)(?:(</(?:\w+:)?{tag_name}>)|(/>))", re.DOTALL
        )
        matches = pattern.findall(xml_text)

        for match in matches:
            if match[3]:
                attributes = parse_attributes(match[0])
                if "value" in attributes:
                    inner_text = attributes["value"]
                    attributes.pop("value")
                else:
                    continue
            else:
                attributes = parse_attributes(match[0])
                inner_text = match[1]
            data_caches.add(tag_name, inner_text, attributes)

        print(
            f"Found {len(matches)} instances of {len(data_caches[tag_name])} unique <{tag_name}> values"
        )

    debug_output = []
    for tag_name, data_cache in data_caches.items():
        for normalized_value, data in data_cache.items():
            xml_text, tag_debug_output = replace(
                xml_text,
                tag_name,
                normalized_value,
                data_cache,
                Tag.from_name(tag_name).get_replacement_mapping,
            )
            debug_output.extend(tag_debug_output)
    if debug:
        print(
            tabulate(
                debug_output,
                headers=["Tag", "Normalized Value", "Original", "Replacement"],
                tablefmt="fancy_outline",
            )
        )
    return xml_text


def replace(
    xml_text: str,
    tag: str,
    normalized_value: str,
    data: TagCache,
    get_replacement_mapping: callable,
):
    """Replace the values in the XML text."""
    debug_output = []
    replacement_mappings = get_replacement_mapping(
        data[normalized_value].values, normalized_value, data[normalized_value].attributes
    )
    for raw_value, replacement in replacement_mappings.items():
        if hasattr(Tag.from_name(tag), "has_value"):
            pattern = re.compile(
                rf'(<{re.escape(tag)}\b[^>]*\bvalue="){re.escape(raw_value)}(")', re.DOTALL
            )
            matches = pattern.findall(xml_text)
            xml_text = pattern.sub(
                lambda m, replacement=replacement: f"{m.group(1)}{replacement}{m.group(2)}",
                xml_text,
            )
        else:
            pattern = re.compile(rf"(<{tag}\b[^>]*>)({raw_value})(</{tag}>)")

            xml_text = pattern.sub(
                lambda m, replacement=replacement: f"{m.group(1)}{replacement}{m.group(3)}",
                xml_text,
            )
        debug_output.append(
            [
                tag,
                normalized_value,
                f"`{raw_value}`",
                f"`{replacement}`",
            ]
        )

    return xml_text, debug_output


if __name__ == "__main__":
    main()
