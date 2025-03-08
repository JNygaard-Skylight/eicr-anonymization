"""Get random Star Wars themed data."""

import re
import string
from random import choice, randint

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
    pattern = re.compile(r"\d")
    new_value = pattern.sub(lambda x: str(_get_random_int(1)), old_value)

    # change direction
    pattern = re.compile(r"(?<=\s)([NESW]|NE|SE|SW|NW)(?=\.?\s)")
    new_value = pattern.sub(lambda _: choice(["N", "NE", "E", "SE", "S", "SW", "NW"]), new_value)

    pattern = re.compile(
        r"((?P<house_number>\d+)\s)((?P<pre_direction>([NESW]|NE|SE|SW|NW)\.?)\s)?((?P<street_name>([A-Za-z]{3,}|\s)+)|(?P<numeric_street_name>\d+(st|nd|rd|th)))\s+(?P<street_type>[A-Za-z]+)(?P<post_direction>\s(([NESW]|NE|SE|SW|NW)\.?)\s)?(?P<unit>.*$)",
        re.IGNORECASE,
    )
    match = pattern.match(new_value)

    if match.group("street_name"):
        new_street_name = choice(_street_names)
    elif match.group("numeric_street_name"):
        new_street_name = choice(_numeric_street_names)

    if match.group("street_type"):
        new_street_type = choice(_street_types)

    new_value = " ".join(
        filter(
            lambda x: x,
            [
                match.group("house_number"),
                match.group("pre_direction"),
                new_street_name,
                new_street_type,
                match.group("post_direction"),
                match.group("unit").lstrip(),
            ],
        )
    )

    return new_value
