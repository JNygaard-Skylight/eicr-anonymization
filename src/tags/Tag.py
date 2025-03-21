"""Tag Class."""

import os
import re
from itertools import zip_longest
from random import choice, randint
from string import ascii_lowercase, ascii_uppercase
from typing import ClassVar, Literal, NotRequired, TypedDict

import usaddress
import yaml


class ReplacementType(TypedDict):
    """Type definition for a replacement."""

    value: str
    abbreviation_only: NotRequired[Literal[True]]
    abbreviations: NotRequired[list[str]]
    qualifier: NotRequired[str]


def _read_yaml(file_name: str) -> list[ReplacementType]:
    """Read a YAML file and return its contents as a list of strings."""
    with open("src/star-wars-data/" + file_name) as file:
        return [yaml.safe_load(file)]


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
    if "." not in value:
        return new_value.replace(".", "")
    elif value.endswith(".") and not new_value.endswith("."):
        return new_value + "."
    else:
        return new_value


def _match_formatting(old_value: str, new_value: str) -> str:
    return _match_case(
        old_value, _match_whitespace(old_value, _match_punctuation(old_value, new_value))
    )


def _map_values_to_formatted_replacement(raw_values: str, replacement: str) -> dict[str, str]:
    """Map raw values to a replacement value and match the whitespace and case."""
    mappings = {}
    for raw_value in raw_values:
        mappings[raw_value] = _match_formatting(raw_value, replacement)
    return mappings


def _get_random_int(digits: int):
    """Get a random integer with the specified number of digits."""
    return randint(10 ** (digits - 1), 10**digits - 1)


class Tag:
    """Tag class."""

    _registry: ClassVar[dict[str, "Tag"]] = {}

    def __init_subclass__(cls, **kwargs) -> None:
        """Register the tag class."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "name") and cls.name:
            instance = cls()
            Tag._registry[cls.name] = instance

    @classmethod
    def get_registry(cls) -> dict[str, "Tag"]:
        """Get a list of all registered tags."""
        return cls._registry

    @classmethod
    def from_name(cls, name: str) -> "Tag":
        """Get a tag by name."""
        return cls._registry.get(name)

    @classmethod
    def get_replacement_mapping(
        cls,
        raw_values: set[str],
        normalized_value: str | None = None,
        attributes: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """Get a replacement mapping."""
        replacement = "REMOVED"
        return _map_values_to_formatted_replacement(raw_values, replacement)

    @classmethod
    def normalize(cls, value: str) -> str:
        """Normalize a string."""
        return value.lower().strip().replace(".", "")

    @classmethod
    def is_equal(cls, a: str, b: str) -> bool:
        """Check if two strings are equal."""
        return cls.normalize(a) == cls.normalize(b)


class FamilyTag(Tag):
    """Family tag class."""

    name = "family"


class GivenTag(Tag):
    """Given tag class."""

    name = "given"


class PrefixTag(Tag):
    """Name prefix tag class."""

    name = "prefix"


class SuffixTag(Tag):
    """Name suffix tag class."""

    name = "suffix"


class StreetAddressTag(Tag):
    """Street address tag class."""

    name = "streetAddressLine"


class CityTag(Tag):
    """City tag class."""

    name = "city"


class CountyTag(Tag):
    """County tag class."""

    name = "county"


class StateTag(Tag):
    """State tag class."""

    name = "state"


class CountryTag(Tag):
    """Country tag class."""

    name = "country"


class PostalCodeTag(Tag):
    """Postal code tag class."""

    name = "postalCode"


class TelecomTag(Tag):
    """Telecom tag class."""

    name = "telecom"
    sensitive_attr = {"value"}

class NameTag(Tag):
    """Name tag class."""

    name = "name"


class TimeTag(Tag):
    """Time tag class."""

    name = "time"
    sensitive_attr = {"value"}


class LowTag(Tag):
    """Low tag class."""

    name = "low"
    sensitive_attr = {"value"}

class HighTag(Tag):
    """High tag class."""

    name = "high"
    sensitive_attr = {"value"}

class IdTag(Tag):
    """ID tag class."""

    name = "id"
    sensitive_attr = {"extension", "root"}
