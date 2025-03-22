"""Main module for the EICR anonymization tool."""

import argparse
import glob
import logging
import os
import re

from lxml import etree
from tabulate import tabulate

from DataCache import NormalizedTagGroups
from tags.Tag import Tag

logger = logging.getLogger(__name__)

_namespace = "urn:hl7-org:v3"
_namespaces = {"ns": _namespace}


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
            # xml_text = file.read()
            tree = etree.parse(file)
        updated_xml = simple_replacement_regex(tree, debug=args.debug)

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


def find_all_with_namespace(root: etree.Element, path):
    """Find all elements for a given path with the HL7 namepsace in an EICR XML file.

    Replaces all instances of "ns" in the path with the HL7 namespace.
    """
    return root.xpath(path, namespaces=_namespaces)


def simple_replacement_regex(tree, debug: bool = False) -> str:
    """Replace sensitive fields in an EICR XML file using regex."""
    root = tree.getroot()
    data_caches = NormalizedTagGroups()
    for tag in Tag.get_registry().values():
        matches = find_all_with_namespace(root, f".//ns:{tag.name}")
        for element in matches:
            if (element.text and element.text.strip()) or (
                hasattr(tag, "sensitive_attr")
                and any(attr in element.attrib for attr in tag.sensitive_attr)
            ):
                # Create an instance of the tag and add it to the data cache
                tag_instance = tag(
                    text=element.text,
                    attributes=dict(element.attrib),
                )
                data_caches.add(tag_instance)
            else:
                continue

    debug_output = []

    for tag_group in data_caches:
        replacement_mapping = tag_group.get_replacement_mapping()

        for instance in tag_group:
            xpath = f".//ns:{instance.name}"
            if instance.text:
                xpath += f"[text()='{instance.text}']"
            if instance.attributes:
                for attribute in instance.attributes:
                    xpath += f'[@{attribute}="{instance.attributes[attribute]}"]'
            else:
                xpath += "[not(@*)]"
            matches = find_all_with_namespace(root, xpath)

            for match in matches:
                if instance.text:
                    match.text = replacement_mapping[instance].text
                for attribute in match.attrib:
                    if attribute in replacement_mapping[instance].attributes:
                        match.attrib[attribute] = replacement_mapping[instance].attributes[
                            attribute
                        ]

            debug_output.append(
                [
                    instance,
                    replacement_mapping[instance],
                ]
            )

    if debug:
        print(
            tabulate(
                debug_output,
                headers=["Original", "Replacement"],
                tablefmt="fancy_outline",
            )
        )
    return etree.tostring(root, encoding="unicode")


if __name__ == "__main__":
    main()
