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


def get_random_family_name(old_value: str | None = None, attributes: dict[str, str] | None = None):
    """Get a random Star Wars themed family name."""
    return choice(_family_names)


def get_random_given_name(old_value: str, attributes: dict[str, str] | None = None):
    """Get a random Star Wars themed given name."""
    if len(old_value) == 1:
        return choice(string.ascii_uppercase)
    return choice(_given_names)


def get_random_name_prefix(old_value: str | None = None, attributes: dict[str, str] | None = None):
    """Get a random Star Wars themed name prefix."""
    return choice(_name_prefixes)


def get_random_name_suffix(old_value: str | None = None, attributes: dict[str, str] | None = None):
    """Get a random Star Wars themed name suffix."""
    if attributes and attributes.get("qualifier") == "AC":
        return choice(
            [suffix["value"] for suffix in _name_suffixes if suffix.get("qualifier") == "AC"]
        )
    else:
        return choice(_name_suffixes)["value"]


def _get_random_int(digits: int):
    """Get a random integer with the specified number of digits."""
    return randint(10 ** (digits - 1), 10**digits - 1)


def _match_case(value: str, new_value: str):
    """Match the case of the new value to the original value."""
    if value.isupper():
        return new_value.upper()
    elif value.islower():
        return new_value.lower()
    elif value.istitle():
        return new_value.title()
    else:
        return new_value


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
                    new_direction += "."
                elif num_periods == 2:
                    new_direction = new_direction[0] + "." + new_direction[1] + "."

                new_parts.append(_match_case(old_direction, new_direction))
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


def get_random_street_address_line(old_value: str, attributes: dict[str, str] | None = None):
    """Get a random Star Wars themed street address."""
    print(old_value)
    parsed_address = usaddress.parse(old_value)
    tagged_address = usaddress.tag(old_value)

    new_parts: list[str] = []
    for key, value in tagged_address[0].items():
        if key == "AddressNumber":
            digits = len(value)
            new_house_number = _get_random_int(digits)
            new_parts.append(str(new_house_number))
        elif key == "StreetNamePreDirectional":
            new_direction = choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])
            num_periods = value.count(".")
            if num_periods == 1:
                new_direction += "."
            elif num_periods == 2:
                new_direction = new_direction[0] + "." + new_direction[1] + "."
            new_parts.append(new_direction)
        elif key == "StreetNamePostType":
            new_parts.append(
                choice(
                    [
                        street_type
                        for street_type in _street_types
                        if street_type.endswith(".") == value.endswith(".")
                    ]
                )
            )
        elif key == "StreetName":
            new_parts.append(choice(_street_names))
        elif key == "OccupancyIdentifier":
            pattern = re.compile(r"\d")
            new_occupancy_identifier = pattern.sub(lambda x: str(_get_random_int(1)), value)
            new_parts.append(new_occupancy_identifier)
        else:
            new_parts.append(value)

    new_value = " ".join(new_parts)

    occupancy_identifiers = [key[0] for key in parsed_address if key[1] == "OccupancyIdentifier"]
    if len(occupancy_identifiers) == 2:
        first_occ_ident = occupancy_identifiers[0]
        start_of_occ_ident = old_value.find(first_occ_ident)
        length_of_occ_ident = len(first_occ_ident)
        if old_value[start_of_occ_ident + length_of_occ_ident] == " ":
            pass
        else:
            start_of_occ_ident = new_value.find(first_occ_ident)
            new_value = (
                new_value[: start_of_occ_ident + length_of_occ_ident]
                + new_value[start_of_occ_ident + length_of_occ_ident + 1 :]
            )

    return new_value
