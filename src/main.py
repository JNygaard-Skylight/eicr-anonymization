"""Main module for the EICR anonymization tool."""

import argparse
import glob
import os
import re
import xml.etree.ElementTree as ET

from tqdm import tqdm

from random_sw.main import (
    get_random_family_name,
    get_random_given_name,
    get_random_name_prefix,
    get_random_name_suffix,
)

_namespace = "urn:hl7-org:v3"


def _get_args():
    parser = argparse.ArgumentParser(description="Anonymize EICR data")
    parser.add_argument("input_location", help="Location of the input EICR files")

    return parser.parse_args()


def main():
    """Anonymize EICR data."""
    args = _get_args()

    # Remove previous anonymization output files
    previous_output_files = glob.glob(os.path.join(args.input_location, "*.anonymized.xml"))
    for output_file in previous_output_files:
        os.remove(output_file)

    ET.register_namespace("", _namespace)

    # Read XML files from input location
    input_location = args.input_location
    xml_files = glob.glob(os.path.join(input_location, "*.xml"))

    for xml_file in xml_files:
    #     tree = ET.parse(xml_file)  # noqa: S314
    #     root = tree.getroot()
    #     # find_sensitive_data(root)
    #     # replace_name(root)
    #     simple_replacement(root)

        simple_replacement_regex(xml_file)

    # # Write the anonymized XML to a new file
    # output_file = f"{xml_file}.anonymized.xml"
    # tree.write(output_file, encoding="utf-8", xml_declaration=True)


def find_sensitive_data(root):
    """Find sensitive data in an EICR XML file."""
    # Find sensitive data in the XML file

    # Patient:
    # - addr
    #   - all of the different address parts
    #   - useable period
    # - telecom
    #   - value
    # - patient
    #   - Name
    #   - birthtime
    #   - guardian
    #   - birthplace

    patient_roles = find_all_with_namespace(root, ".//ns:recordTarget/ns:patientRole")

    sensitive_data = {
        "patientRole": [
            {
                "addr": [
                    {
                        "streetAddressLine": "1234 Anonymized St.",
                        "city": "Anonymized City",
                        "state": "Anonymized State",
                        "postalCode": "12345",
                    }
                ]
            }
        ]
    }

    print(f"Found {len(patient_roles)} patientRole elements")
    for patient_role in tqdm(patient_roles):
        # Build dictionary of sensitive data
        print(patient_role)

        # Get all `addr` elements
        addr_elements = find_all_with_namespace(patient_role, "ns:addr")
        print(f"Found {len(addr_elements)} addr elements")

        sensitive_address_tags = {
            "country",
            "state",
            "county",
            "city",
            "postalCode",
            "streetAddressLine",
            "houseNumber",
            "houseNumberNumeric",
            "direction",
            "streetName",
            "streetNameBase",
            "streetNameType",
            "additionalLocator",
            "unitID",
            "unitType",
            "careOf",
            "censusTract",
            "deliveryAddressLine",
            "deliveryInstallationType",
            "deliveryInstallationArea",
            "deliveryInstallationQualifier",
            "deliveryMode",
            "deliveryModeIdentifier",
            "buildingNumberSuffix",
            "postBox",
            "precinct",
            "xmlText",
        }
        sensitive_address_tags = prepend_namespace_to_tags(sensitive_address_tags)

        addresses = []
        for addr_element in addr_elements:
            sensitive_addr_fields = {}
            for addr_part in (
                element for element in addr_element if element.tag in sensitive_address_tags
            ):
                sensitive_addr_fields[addr_part.tag] = addr_part.text
            print(sensitive_addr_fields)

            usable_periods = find_all_with_namespace(addr_element, "ns:useablePeriod")
            for usable_period in usable_periods:
                for usable_period_part in usable_period:
                    if is_tag(usable_period_part, "low") and usable_period_part.attrib.get("value"):
                        sensitive_addr_fields.setdefault(f"{_namespace}:useablePeriod", {})[
                            "{urn:hl7-org:v3}low"
                        ] = usable_period_part.attrib.get("value")
                    elif is_tag(usable_period_part, "high") and usable_period_part.attrib.get(
                        "value"
                    ):
                        sensitive_addr_fields.setdefault(f"{_namespace}:useablePeriod", {})[
                            "{urn:hl7-org:v3}high"
                        ] = usable_period_part.attrib.get("value")

            addresses.append(sensitive_addr_fields)

        # Get all `telecom` elements
        telecom_elements = find_all_with_namespace(patient_role, "ns:telecom")
        print(f"Found {len(telecom_elements)} telecom elements")

        telecoms = []
        for telecom_element in telecom_elements:
            telecoms.append(telecom_element.attrib.get("value"))


def is_tag(element: ET.Element, tag_name: str):
    """Check if the tag name matches the elements tag."""
    return element.tag.lower() == f"{{{_namespace}}}{tag_name}"


def prepend_namespace_to_tags(tag_name_list: list[str]):
    """Prepend the HL7 namespace to the tag names in the sensitive address fields."""
    return {f"{{{_namespace}}}{tag}" for tag in tag_name_list}


def find_all_with_namespace(root: ET.Element, path):
    """Find all elements for a given path with the HL7 namepsace in an EICR XML file.

    Replaces all instances of "ns" in the path with the HL7 namespace.
    """
    return root.findall(path, {"ns": _namespace})


def replace_name(root):
    """Replace patient names in an EICR XML file."""
    # Patient names
    patient_name_elements = root.findall(
        ".//{_namespace}recordTarget/{_namespace}patientRole/{_namespace}patient/{_namespace}name"
    )

    data_cache = {}

    if patient_name_elements:
        print(f"Found {len(patient_name_elements)} patient names")
        for name_element in tqdm(patient_name_elements):
            for name_part in name_element:
                if data_cache.get(name_part.tag):
                    name_part.text = data_cache[name_part.tag]
                else:
                    match name_part.tag.lower():
                        case "{_namespace}family":
                            name_part.text = get_random_family_name()
                        case "{_namespace}given":
                            name_part.text = get_random_given_name()
                        case "{_namespace}prefix":
                            name_part.text = get_random_name_prefix()
                        case "{_namespace}suffix":
                            name_part.text = get_random_name_suffix()

                    data_cache[name_part.tag] = name_part.text

    # Patient addresses
    patient_address_elements = root.findall(
        ".//{_namespace}recordTarget/{_namespace}patientRole/{_namespace}addr"
    )

    if patient_address_elements:
        print(f"Found {len(patient_address_elements)} patient addresses")
        for address_element in tqdm(patient_address_elements):
            for address_part in address_element:
                match address_part.tag.lower():
                    case "{_namespace}streetAddressLine":
                        address_part.text = "1234 Anonymized St."
                    case "{_namespace}city":
                        address_part.text = "Anonymized City"
                    case "{_namespace}state":
                        address_part.text = "Anonymized State"
                    case "{_namespace}postalCode":
                        address_part.text = "12345"


def simple_replacement(root):

    sensitive_fields_paths = [
        (".//ns:name/ns:family", get_random_family_name),
        (".//ns:name/ns:given", get_random_given_name),
        (".//ns:name/ns:prefix", get_random_name_prefix),
        (".//ns:name/ns:suffix", get_random_name_suffix),
    ]

    for sensitive_fields_path, get_random_value in sensitive_fields_paths:
        sensitive_elements = find_all_with_namespace(root, sensitive_fields_path)
        print(f"Found {len(sensitive_elements)} {sensitive_fields_path} elements")
        data_cache = {}
        for sensitive_element in sensitive_elements:
            old_value = sensitive_element.text
            if data_cache.get(old_value):
                sensitive_element.text = data_cache[old_value]
            elif sensitive_element.text:
                sensitive_element.text = get_random_value()


def simple_replacement_regex(xml_file_path):
    """Replace sensitive fields in an EICR XML file using regex."""
    with open(xml_file_path) as file:
        xml_text = file.read()

    sensitive_fields = [
        ("family", get_random_family_name),
        ("given", get_random_given_name),
        ("prefix", get_random_name_prefix),
        ("suffix", get_random_name_suffix),
    ]

    for tag, get_random_value in sensitive_fields:
        data_cache = {}
        # This regex handles both normal tags with content and self-closing tags.
        pattern = re.compile(
            rf'(<(?:\w+:)?{tag}\b[^>]*>)(.*?)(?:(</(?:\w+:)?{tag}>)|(/>))',
            re.DOTALL
        )

        def repl(match):
            open_tag, inner_text, closing_tag, self_close = match.groups()
            if self_close is not None:
                return match.group(0)
            # Otherwise, process the tag with content.
            if inner_text in data_cache:
                new_value = data_cache[inner_text]
            else:
                new_value = get_random_value() if inner_text.strip() else inner_text
                data_cache[inner_text] = new_value
            return f"{open_tag}{new_value}{closing_tag}"

        xml_text = pattern.sub(repl, xml_text)

    with open(f"{xml_file_path}.anonymized.xml", "w", encoding="utf-8") as f:
        f.write(xml_text)


if __name__ == "__main__":
    main()
