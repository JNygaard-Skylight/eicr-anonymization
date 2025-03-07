"""Main module for the EICR anonymization tool."""

import argparse
import glob
import os
import xml.etree.ElementTree as ET

from tqdm import tqdm

from random_sw.main import (
    get_random_family_name,
    get_random_given_name,
    get_random_name_prefix,
    get_random_name_suffix,
)


def _get_args():
    parser = argparse.ArgumentParser(description="Anonymize EICR data")
    parser.add_argument("input_location", help="Location of the input EICR files")

    return parser.parse_args()


def main():
    """Anonymize EICR data."""
    args = _get_args()

    namespace = "urn:hl7-org:v3"
    ET.register_namespace("", namespace)

    # Read XML files from input location
    input_location = args.input_location
    xml_files = glob.glob(os.path.join(input_location, "*.xml"))

    for xml_file in xml_files:
        tree = ET.parse(xml_file)  # noqa: S314
        root = tree.getroot()

        patient_name_elements = root.findall(
            ".//{urn:hl7-org:v3}recordTarget/{urn:hl7-org:v3}patientRole/{urn:hl7-org:v3}patient/{urn:hl7-org:v3}name"
        )

        if patient_name_elements:
            print(f"Found {len(patient_name_elements)} patient names")
            for name_element in tqdm(patient_name_elements):
                for name_part in name_element:
                    match name_part.tag.lower():
                        case "{urn:hl7-org:v3}family":
                            name_part.text = get_random_family_name()
                        case "{urn:hl7-org:v3}given":
                            name_part.text = get_random_given_name()
                        case "{urn:hl7-org:v3}prefix":
                            name_part.text = get_random_name_prefix()
                        case "{urn:hl7-org:v3}suffix":
                            name_part.text = get_random_name_suffix()

        # Write the anonymized XML to a new file
        output_file = f"{xml_file}.anonymized.xml"
        tree.write(output_file, encoding='utf-8', xml_declaration=True)


if __name__ == "__main__":
    main()
