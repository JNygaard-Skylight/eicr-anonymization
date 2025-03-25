"""Main module for the EICR anonymization tool."""

import argparse
import glob
import logging
import os

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

    previous_output_files = glob.glob(os.path.join(args.input_location, "*.anonymized.xml"))
    for output_file in previous_output_files:
        os.remove(output_file)

    input_location = args.input_location
    xml_files = glob.glob(os.path.join(input_location, "*.xml"))

    for xml_file in xml_files:
        with open(xml_file) as file:
            tree = etree.parse(file)
        tree = find_and_replace_sensitive_fields(tree, debug=args.debug)

        tree.write(f"{xml_file}.anonymized.xml")


def _find_all_with_namespace(root: etree.Element, path):
    """Find all elements for a given path with the HL7 namepsace in an EICR XML file.

    Replaces all instances of "ns" in the path with the HL7 namespace.
    """
    return root.xpath(path, namespaces=_namespaces)


def find_and_replace_sensitive_fields(tree, debug: bool = False) -> str:
    """Replace sensitive fields in an EICR XML file."""
    root = tree.getroot()
    sensitive_tag_groups = NormalizedTagGroups()
    tag_registry = Tag.get_registry().values()

    for tag in tag_registry:
        elements = _find_all_with_namespace(root, f".//ns:{tag.name}")
        for element in elements:
            text_is_nonempty = element.text and element.text.strip()
            attr_is_sensitive = hasattr(tag, "sensitive_attr") and any(
                attr in element.attrib for attr in tag.sensitive_attr
            )
            if not (text_is_nonempty or attr_is_sensitive):
                continue

            tag_instance = tag(
                text=element.text,
                attributes=dict(element.attrib),
            )
            sensitive_tag_groups.add(tag_instance)

    debug_output = []

    for tag_group in sensitive_tag_groups:
        replacement_mapping = tag_group.get_replacement_mapping()

        for instance in tag_group:
            replacement = replacement_mapping[instance]

            xpath_parts = [f".//ns:{instance.name}"]
            if instance.text:
                xpath_parts.append(f"[text()='{instance.text}']")
            if instance.attributes:
                for attr_name, attr_value in instance.attributes.items():
                    xpath_parts.append(f'[@{attr_name}="{attr_value}"]')
            else:
                xpath_parts.append("[not(@*)]")

            xpath = "".join(xpath_parts)
            matches = _find_all_with_namespace(root, xpath)

            for match in matches:
                if instance.text:
                    match.text = replacement.text
                for attr, new_val in replacement.attributes.items():
                    if attr in match.attrib:
                        match.attrib[attr] = new_val

            debug_output.append([instance, replacement])

    if debug:
        print_debug(debug_output)

    return tree


def print_debug(debug_output):
    """Print debug information for each replacement made."""
    print(
        tabulate(
            debug_output,
            headers=["Original", "Replacement"],
            tablefmt="fancy_outline",
        )
    )


if __name__ == "__main__":
    main()
