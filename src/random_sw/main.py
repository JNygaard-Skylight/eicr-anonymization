"""Get random Star Wars themed data."""

import re
import string
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


def get_random_street_address_line(old_value: str, attributes: dict[str, str] | None = None):
    """Get a random Star Wars themed street address."""
    # Get the number of digits in the house number
    print(old_value)
    parsed_address = usaddress.tag(old_value)
    print(parsed_address)

    new_value = ""
    for  key, value in parsed_address[0].items():
        if key == "AddressNumber":
            digits = len(value)
            new_house_number = _get_random_int(digits)
            new_value += f"{new_house_number} "
        elif key == "StreetNamePreDirectional":
            new_value += choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]) + " "
        elif key == "StreetNamePostType":
            new_value += f"{choice(_street_types)} "
        elif key == "StreetName":
            new_value += f"{choice(_street_names)} "
        elif key == "OccupancyIdentifier":
            pattern = re.compile(r"\d")
            new_occupancy_identifier = pattern.sub(
                lambda x: str(_get_random_int(1)), value
            )
            new_value += f"{new_occupancy_identifier}"
        else:
            new_value += f"{value}"

    print(new_value)
    print("----------")
    return new_value.rstrip()
