"""Tag Class."""

from random import choice, randint
from typing import ClassVar, Literal, NotRequired, TypedDict

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
        return yaml.safe_load(file)


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


def _map_values_to_formatted_replacement(
    raw_values: set["Tag"], replacement: str
) -> dict["Tag", "Tag"]:
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

    default_replace_value = "REMOVED"

    _registry: ClassVar[dict[str, "Tag"]] = {}

    def __init_subclass__(cls, **kwargs) -> None:
        """Register the tag class."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "name") and cls.name:
            Tag._registry[cls.name] = cls

    def __init__(self, text: str | None = None, attributes: dict[str, str] | None = None):
        """Initialize the tag."""
        self._text = text
        self._attributes = attributes or {}

    def __repr__(self) -> str:
        """Get a string representation of the tag."""
        repr = f"<{self.name}"
        for attribute in self.attributes:
            repr += f' {attribute}="{self.attributes[attribute]}"'

        if self.text:
            repr += f">{self.text}</{self.name}>"
        else:
            repr += " />"

        return repr

    def __setattr__(self, name, value):
        """Make name, sensitive_attr, and replacements read-only."""
        if name in ("name", "sensitive_attr", "replacement_values"):
            raise AttributeError(f"{name} is read-only")
        super().__setattr__(name, value)

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
        raw_values: set["Tag"],
    ) -> dict[str, str]:
        """Get a replacement mapping."""
        if hasattr(cls, "replacement_values") and cls.replacement_values:
            replacement = choice(cls.replacement_values)["value"]
        else:
            replacement = cls.default_replace_value

        sensitive_attr_replacements = None
        if hasattr(cls, "sensitive_attr"):
            sensitive_attr_replacements = {}
            for attr in cls.sensitive_attr:
                sensitive_attr_replacements[attr] = replacement

        mapping = {}
        for tag in raw_values:
            attribute_replacements = tag.attributes.copy() if tag.attributes else None
            if sensitive_attr_replacements:
                for attr, value in sensitive_attr_replacements.items():
                    if attr in attribute_replacements:
                        attribute_replacements[attr] = value

            replacement_text = None
            if tag.text:
                replacement_text = _match_formatting(tag.text, replacement)
            mapping[tag] = tag.__class__(text=replacement_text, attributes=attribute_replacements)

        return mapping

    @classmethod
    def normalize(cls, value: str | None) -> str:
        """Normalize a string."""
        if value is None:
            return None
        else:
            return value.lower().strip().replace(".", "")

    @classmethod
    def is_equal(cls, a: str, b: str) -> bool:
        """Check if two strings are equal."""
        return cls.normalize(a) == cls.normalize(b)

    @property
    def text(self) -> str:
        """Get the text of the tag."""
        return self._text

    @property
    def normalized_text(self) -> str:
        """Get the normalized text of the tag."""
        return self.normalize(self._text)

    @property
    def attributes(self) -> dict[str, str]:
        """Get the attributes of the tag."""
        return self._attributes

    def __eq__(self, other: object) -> bool:
        """Check if two tags are equal.

        Two tags are equal if:
        - They have the same name
        - They have the same sensitive attributes (if any)
        - They have the same text when normalized.
        - They have the same attributes and the same values for those attributes
        """
        return (
            isinstance(other, self.__class__)
            and self.name == other.name
            and getattr(self, "sensitive_attr", None) == getattr(other, "sensitive_attr", None)
            and self.normalized_text == other.normalized_text
            and self.attributes == other.attributes
        )

    def __hash__(self) -> int:
        """Get the hash of the tag."""
        return hash(
            (
                self.name,
                self.text,
                self._tuple_attributes(),
                getattr(self, "sensitive_attr", None),
            )
        )

    def _tuple_attributes(self) -> int:
        """Get the tuples of the attributes."""
        return tuple(sorted(self.attributes.items()))

    def _normalize_attributes(self) -> tuple[str, str]:
        """Get the hash of the attributes."""
        return tuple(
            [(key, self.normalize(value)) for key, value in sorted(self.attributes.items())]
        )

    @property
    def normalized_hash(self) -> int:
        """Get the hash of the normalized text."""
        return hash(
            (
                self.name,
                self.normalized_text,
                self._normalize_attributes(),
                getattr(self, "sensitive_attr", None),
            )
        )


class FamilyTag(Tag):
    """Family tag class."""

    name = "family"
    replacement_values = _read_yaml("family_names.yaml")


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
    sensitive_attr = ("value",)


class NameTag(Tag):
    """Name tag class."""

    name = "name"


class TimeTag(Tag):
    """Time tag class."""

    name = "time"
    sensitive_attr = ("value",)


class LowTag(Tag):
    """Low tag class."""

    name = "low"
    sensitive_attr = ("value",)


class HighTag(Tag):
    """High tag class."""

    name = "high"
    sensitive_attr = ("value",)


class IdTag(Tag):
    """ID tag class."""

    name = "id"
    sensitive_attr = ("extension", "root")


class EffectiveTimeTag(Tag):
    """Effective time tag class."""

    name = "effectiveTime"
    sensitive_attr = ("value",)
