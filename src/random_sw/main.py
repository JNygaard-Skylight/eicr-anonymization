"""Get random Star Wars themed data."""

import re
import string
from itertools import zip_longest
from random import choice, randint

import usaddress
import yaml


def _read_yaml(file_path: str) -> list[str]:
    """Read a YAML file and return its contents as a list of strings."""
    with open(file_path) as file:
        return yaml.safe_load(file)


_family_names = _read_yaml("src/random_sw/data/family_names.yaml")
_given_names = _read_yaml("src/random_sw/data/given_names.yaml")
_name_prefixes = _read_yaml("src/random_sw/data/name_prefixes.yaml")
_name_suffixes = _read_yaml("src/random_sw/data/name_suffixes.yaml")
_street_names = _read_yaml("src/random_sw/data/street_names.yaml")
_numeric_street_names = _read_yaml("src/random_sw/data/numeric_street_names.yaml")
_street_types = _read_yaml("src/random_sw/data/street_types.yaml")


def _get_leading_trailing_whitespace(value: str) -> tuple[str, str]:
    """Get the leading and trailing whitespace from a string."""
    leading_whitespace = value[: -len(value.lstrip())]
    trailing_whitespace = value[len(value.rstrip()) :]

    return leading_whitespace, trailing_whitespace


def _match_whitespace(old_value: str, new_value: str) -> str:
    """Match the whitespace of the old value to the new value."""
    leading_whitespace, trailing_whitespace = _get_leading_trailing_whitespace(old_value)
    return leading_whitespace + new_value + trailing_whitespace


def _match_case(value: str, new_value: str):
    """Match the case of the new value to the original value."""
    if value.isupper():
        return new_value.upper()
    elif value.islower():
        return new_value.lower()
    # elif value.istitle():
    #     return new_value.title()
    else:
        return new_value


def _match_punctuation(value: str, new_value: str):
    """Match the punctuation of the old value to the new value."""
    if value.endswith(".") and not new_value.endswith("."):
        return new_value + "."
    else:
        return new_value


def _map_values_to_formatted_replacement(raw_values: str, replacement: str) -> dict[str, str]:
    """Map raw values to a replacement value and match the whitespace and case."""
    mappings = {}
    for raw_value in raw_values:
        mappings[raw_value] = _match_case(
            raw_value, _match_whitespace(raw_value, _match_punctuation(raw_value, replacement))
        )
    return mappings


def get_random_family_name_mapping(raw_values: set[str]):
    """Get a random Star Wars themed family name for the set of simliar names."""
    # Get the first value in the set
    replacement = choice(_family_names)
    return _map_values_to_formatted_replacement(raw_values, replacement)


def get_random_given_name_mapping(raw_values: set[str], normalized_value: str):
    """Get a random Star Wars themed given name."""
    # Get the first value in the set
    if len(normalized_value) == 1:
        replacement = choice(string.ascii_uppercase)
    else:
        replacement = choice(_given_names)
    return _map_values_to_formatted_replacement(raw_values, replacement)


def get_random_name_prefix_mapping(raw_values: set[str]):
    """Get a random Star Wars themed name prefix."""
    replacement = choice(_name_prefixes)

    is_abbreviation_list = [True for x in raw_values if x.endswith(".") or len(x) <= 4]
    num_abbreviations = len([is_abbreviation_list for x in is_abbreviation_list if x])
    has_full_name = len(is_abbreviation_list) != len(raw_values)

    if has_full_name and num_abbreviations >= 1:
        # if it is a mix of a full prefix and an abbreviation, we can pick any prefix that is not abbreviation only
        replacement = choice(
            [x for x in _name_prefixes if x["abbreviation"] and "abbreviation_only" not in x]
        )
        replacement_name = replacement["name"]
        replacement_abbreviation = replacement["abbreviation"]
    elif has_full_name:
        # if it has only full names, we can pick any prefix that is not abbreviation only
        replacement_name = choice([x for x in _name_prefixes if "abbreviation_only" not in x])[
            "name"
        ]
    else:
        # if we got here we can assume it is only a single abbreviation
        replacement_abbreviation = [x["name"] for x in _name_prefixes if "abbreviation_only" in x]
        for prefix in _name_prefixes:
            if "abbreviation" in prefix:
                replacement_abbreviation.append(prefix["abbreviation"])
        replacement_abbreviation = choice(replacement_abbreviation)

    mappings = {}
    for raw_value, is_abbreviation in zip_longest(raw_values, is_abbreviation_list):
        replacement = replacement_abbreviation if is_abbreviation else replacement_name
        mappings[raw_value] = _match_case(
            raw_value, _match_whitespace(raw_value, _match_punctuation(raw_value, replacement))
        )
    return mappings


def get_random_name_suffix_mapping(raw_values: set[str], attributes: dict[str, str] | None = None):
    """Get a random Star Wars themed name suffix."""
    if attributes and attributes.get("qualifier") == "AC":
        replacement = choice(
            [suffix["value"] for suffix in _name_suffixes if suffix.get("qualifier") == "AC"]
        )
    else:
        replacement = choice(_name_suffixes)["value"]

    return _map_values_to_formatted_replacement(raw_values, replacement)


def _get_random_int(digits: int):
    """Get a random integer with the specified number of digits."""
    return randint(10 ** (digits - 1), 10**digits - 1)


def get_random_street_address_mapping(raw_values: set[str]):
    """Get a random Star Wars themed street address. for the set of simliar addresses.

    I want to do something like this:
    1) Parse the first address in the set, we can be confident that all addresses in the set refer to
    the same address
    3) Get a random value for each found address component
    4) Build the new address as we did in get_random_street_address_line, but this time using the
    preselected values
    """
    # Parse the first address in the set, we can be confident that all addresses in the set refer to
    # the same address
    tagged_address = usaddress.tag(next(iter(raw_values)))[0]
    tagged_addresses = [usaddress.tag(x)[0] for x in raw_values]
    street_types = {x["StreetNamePostType"] for x in tagged_addresses}
    num_street_types = len(street_types)

    if "AddressNumber" in tagged_address:
        value = tagged_address["AddressNumber"]
        digits = len(value)
        new_house_number = str(_get_random_int(digits))
    if (
        "StreetNamePreDirectional" in tagged_address
        or "StreetNamePostDirectional" in tagged_address
    ):
        new_direction = choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])
    if "StreetName" in tagged_address:
        new_street_name = choice(_street_names)
    if "StreetNamePostType" in tagged_address:
        # If there is more than one unique street type, we can assume an abbrevations was used.
        # so pick a type with enough abbrevations.
        if num_street_types > 2:
            new_street_type = choice(
                [
                    street_type
                    for street_type in _street_types
                    if len(street_type.get("abbreviations", [])) > num_street_types - 1
                ]
            )
        else:
            new_street_type = choice(_street_types)
    if "OccupancyIdentifier" in tagged_address:
        pattern = re.compile(r"\d")
        new_occupancy_identifier = pattern.sub(
            lambda x: str(_get_random_int(1)), tagged_address["OccupancyIdentifier"]
        )

    new_value_mapping = {}
    for raw_value, old_address in zip_longest(raw_values, tagged_addresses):
        parsed_address = usaddress.parse(raw_value)
        used_street_type_name = False
        new_parts = []
        for key, value in old_address.items():
            if key == "AddressNumber":
                new_parts.append(new_house_number)
            elif key == "StreetNamePreDirectional":
                old_direction = old_address["StreetNamePreDirectional"]
                num_periods = old_direction.count(".")
                if num_periods == 1:
                    new_direction_x = new_direction + "."
                elif num_periods == 2:
                    new_direction_x = new_direction[0] + "." + new_direction[1] + "."
                else:
                    new_direction_x = new_direction

                new_parts.append(_match_case(old_direction, new_direction_x))
            elif key == "StreetName":
                new_parts.append(_match_case(old_address["StreetName"], new_street_name))
            elif key == "StreetNamePostType":
                old_street_type = old_address["StreetNamePostType"]
                if old_street_type.endswith("."):
                    new_street_type_x = choice(new_street_type["abbrevations"]) + "."
                elif not used_street_type_name:
                    new_street_type_x = new_street_type["name"]
                    used_street_type_name = True
                else:
                    new_street_type_x = choice(new_street_type["abbrevations"])

                new_parts.append(_match_case(old_street_type, new_street_type_x))
            elif key == "StreetNamePostDirectional":
                old_direction = old_address["StreetNamePreDirectional"]
                num_periods = old_direction.count(".")
                if num_periods == 1:
                    new_direction += "."
                elif num_periods == 2:
                    new_direction = new_direction[0] + "." + new_direction[1] + "."
                new_parts.append(_match_case(old_direction, new_direction))
            elif key == "OccupancyIdentifier":
                new_parts.append(new_occupancy_identifier)
            else:
                new_parts.append(value)
        new_value = " ".join(new_parts)

        occupancy_identifiers = [
            key[0] for key in parsed_address if key[1] == "OccupancyIdentifier"
        ]
        if len(occupancy_identifiers) == 2:
            first_occ_ident = occupancy_identifiers[0]
            start_of_occ_ident = raw_value.find(first_occ_ident)
            length_of_occ_ident = len(first_occ_ident)
            if raw_value[start_of_occ_ident + length_of_occ_ident] == " ":
                pass
            else:
                start_of_occ_ident = new_value.find(first_occ_ident)
                new_value = (
                    new_value[: start_of_occ_ident + length_of_occ_ident]
                    + new_value[start_of_occ_ident + length_of_occ_ident + 1 :]
                )

        new_value_mapping[raw_value] = new_value
    return new_value_mapping
