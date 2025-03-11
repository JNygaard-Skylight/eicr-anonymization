"""Main module for the EICR anonymization tool."""

import argparse
import glob
import logging
import os
import re

from tabulate import tabulate

from data_cache.main import DataCache
from random_sw.main import (
    get_random_family_name_mapping,
    get_random_given_name_mapping,
    get_random_name_prefix_mapping,
    get_random_name_suffix_mapping,
    get_random_street_address_mapping,
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
    sensitive_fields = [
        "family",
        "given",
        "prefix",
        "suffix",
        "streetAddressLine",
    ]
    data_caches = {}
    for tag in sensitive_fields:
        data_caches[tag] = DataCache()
        pattern = re.compile(
            rf"(<(?:\w+:)?{tag}\b[^>]*>)(.*?)(?:(</(?:\w+:)?{tag}>)|(/>))", re.DOTALL
        )
        matches = pattern.findall(xml_text)

        for match in matches:
            if match[3]:
                continue
            attributes = parse_attributes(match[0])
            inner_text = match[1]
            data_caches[tag].add(inner_text, attributes)

        print(
            f"Replaced {len(matches)} instances of {len(data_caches[tag])} unique <{tag}> values "
        )

    debug_output = []
    for tag, data_cache in data_caches.items():
        for normalized_value, data in data_cache.items():
            match tag:
                case "family":
                    replacement_mappings = get_random_family_name_mapping(data)
                    for raw_value, replacement in replacement_mappings.items():
                        xml_text = xml_text.replace(raw_value, replacement)
                        debug_output.append(
                            [
                                tag,
                                normalized_value,
                                raw_value,
                                replacement,
                            ]
                        )
                case "given":
                    replacement_mappings = get_random_given_name_mapping(data, normalized_value)
                    for raw_value, replacement in replacement_mappings.items():
                        xml_text = xml_text.replace(raw_value, replacement)
                        debug_output.append(
                            [
                                tag,
                                normalized_value,
                                raw_value,
                                replacement,
                            ]
                        )
                case "prefix":
                    replacement_mappings = get_random_name_prefix_mapping(data, normalized_value)
                    for raw_value, replacement in replacement_mappings.items():
                        xml_text = xml_text.replace(raw_value, replacement)
                        debug_output.append(
                            [
                                tag,
                                normalized_value,
                                raw_value,
                                replacement,
                            ]
                        )
                case "suffix":
                    replacement_mappings = get_random_name_suffix_mapping(
                        data, attributes=data_cache.attributes.get(normalized_value)
                    )
                    for raw_value, replacement in replacement_mappings.items():
                        xml_text = xml_text.replace(raw_value, replacement)
                        debug_output.append(
                            [
                                tag,
                                normalized_value,
                                raw_value,
                                replacement,
                            ]
                        )
                case "streetAddressLine":
                    replacement_mappings = get_random_street_address_mapping(data)
                    for raw_value, replacement in replacement_mappings.items():
                        xml_text = xml_text.replace(raw_value, replacement)
                        debug_output.append(
                            [
                                tag,
                                normalized_value,
                                raw_value,
                                replacement,
                            ]
                        )

    if debug:
        print(
            tabulate(
                debug_output,
                headers=["Tag", "Normalized Value", "Original", "Replacement"],
                tablefmt="fancy_outline",
            )
        )
    return xml_text


if __name__ == "__main__":
    main()
