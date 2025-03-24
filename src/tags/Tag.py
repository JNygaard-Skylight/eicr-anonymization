"""Tag Class."""

from datetime import datetime, timedelta
from random import choice, randint, random
import re
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
        cls._used_replacements: set[str] = set()

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
        normalized_tag: "Tag",
        raw_values: set["Tag"],
    ) -> dict[str, str]:
        """Get a replacement mapping."""
        replacement = cls.get_replacement_value(raw_values)

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
    def get_replacement_value(cls, raw_values: set["Tag"]) -> str:
        """Get a replacement value."""
        if hasattr(cls, "replacement_values") and cls.replacement_values:
            replacements = cls.replacement_values
            replacements = [r for r in replacements if r["value"] not in cls._used_replacements]
            if not replacements:
                cls._used_replacements.clear()
                replacements = cls.replacement_values
            replacement = choice(replacements)["value"]
            cls._used_replacements.add(replacement)
        else:
            replacement = cls.default_replace_value
        return replacement

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

    @property
    def normalized_attributes(self) -> tuple[str, str]:
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
                self.normalized_attributes,
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
    replacement_values = _read_yaml("given_names.yaml")


class PrefixTag(Tag):
    """Name prefix tag class."""

    name = "prefix"
    replacement_values = _read_yaml("name_prefixes.yaml")


class SuffixTag(Tag):
    """Name suffix tag class."""

    name = "suffix"
    replacement_values = _read_yaml("name_suffixes.yaml")


class StreetAddressTag(Tag):
    """Street address tag class."""

    name = "streetAddressLine"
    _street_names = _read_yaml("street_names.yaml")
    _street_types = _read_yaml("street_types.yaml")

    @classmethod
    def get_replacement_value(
        cls,
        raw_values: set["Tag"],
    ) -> dict[str, str]:
        """Get a replacement mapping.

        Simple replacement:
         Random number
         random choice between pre-direction, post-direction, or direction.
         Random street name
         random street type
        """
        number = _get_random_int(4)
        pre_direction = ""
        post_direction = ""
        direction_type = random()
        if direction_type < 0.33:
            pre_direction = choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])
        elif direction_type < 0.66:
            post_direction = choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])

        street_name = choice(cls._street_names)["value"]
        street_type = choice(cls._street_types)["value"]
        replacement = " ".join(
            filter(
                None,
                [
                    str(number),
                    pre_direction,
                    street_name,
                    street_type,
                    post_direction,
                ],
            )
        ).strip()

        return replacement


class CityTag(Tag):
    """City tag class."""

    name = "city"
    replacement_values = _read_yaml("city_names.yaml")


class CountyTag(Tag):
    """County tag class."""

    name = "county"
    replacement_values = _read_yaml("county_names.yaml")


class StateTag(Tag):
    """State tag class."""

    name = "state"
    replacement_values = _read_yaml("state_names.yaml")


class CountryTag(Tag):
    """Country tag class."""

    name = "country"
    replacement_values = _read_yaml("country_names.yaml")


class PostalCodeTag(Tag):
    """Postal code tag class."""

    name = "postalCode"

    @classmethod
    def get_replacement_value(
        cls,
        raw_values: set[Tag],
    ) -> dict[str, str]:
        """Get a replacement value."""
        replacement = str(_get_random_int(5))
        if random() < 0.5:
            replacement += f"-{_get_random_int(4)!s}"

        return replacement


class TelecomTag(Tag):
    """Telecom tag class."""

    name = "telecom"
    sensitive_attr = ("value",)

    @classmethod
    def get_replacement_value(
        cls,
        raw_values: set["Tag"],
    ) -> dict[str, str]:
        """Get a replacement value."""
        replacement = ""

        if random() < 0.5:
            replacement = f"tel:{randint(0, 9)}-555-{randint(0, 999)}-{randint(0, 9999)}"
        else:
            replacement = f"mailto:email{randint(0, 999)}@example.com"

        return replacement


class NameTag(Tag):
    """Name tag class."""

    name = "name"

    @classmethod
    def get_replacement_value(
        cls,
        raw_values: set["Tag"],
    ) -> dict[str, str]:
        """Get a replacement value."""
        type = ["Medical Center", "Hospital", "Clinic", "Laboratory", "Pharmacy", "Lab"]
        names = [
            _read_yaml("family_names.yaml"),
            _read_yaml("city_names.yaml"),
            _read_yaml("county_names.yaml"),
            _read_yaml("state_names.yaml"),
            _read_yaml("country_names.yaml"),
        ]

        replacement = " ".join(
            [
                choice(choice(names))["value"],
                choice(type),
            ]
        )

        return replacement


class TemporalTag(Tag):
    """Temporal tag class."""

    sensitive_attr = ("value",)
    SECONDS_IN_100_YEARS = int(100 * 60 * 60 * 24 * 365.25)
    # The main offset is a random number of seconds between 0 and 100 years
    main_offset = randint(0, SECONDS_IN_100_YEARS)

    @classmethod
    def get_replacement_mapping(
        cls,
        normalized_tag: Tag,
        raw_values: set["Tag"],
    ) -> dict[str, str]:
        """Get a replacement value."""
        # Convert the value into a datetime object
        # Indfering datetime format is hard. So far I have seen 3 formats:
        # 1. YYYYMMDDHHMMSS
        # 2. YYYYMMDDHHMMSS+/-HHMM
        # 3. YYYYMMDD
        known_formats = [
            "%Y%m%d%H%M%S",
            "%Y%m%d%H%M%S%z",
            "%Y%m%d",
        ]
        # Check if the value is in one of the known formats
        for fmt in known_formats:
            try:
                date_time = datetime.strptime(normalized_tag.attributes["value"], fmt)
                break
            except ValueError:
                continue

        date_time = date_time - timedelta(seconds=cls.main_offset)

        mapping = {}
        for tag in raw_values:
            attribute_replacements = tag.attributes.copy() if tag.attributes else None
            attribute_replacements["value"] = date_time.strftime(fmt)

            mapping[tag] = tag.__class__(text=tag.text, attributes=attribute_replacements)

        return mapping


class TimeTag(TemporalTag):
    """Time tag class."""

    name = "time"


class LowTag(TemporalTag):
    """Low tag class."""

    name = "low"


class HighTag(TemporalTag):
    """High tag class."""

    name = "high"


class EffectiveTimeTag(Tag):
    """Effective time tag class."""

    name = "effectiveTime"


class IdTag(Tag):
    """ID tag class."""

    name = "id"
    sensitive_attr = ("extension", "root")
    oid_pattern = re.compile(r"^[0-2](\.(0|[1-9][0-9]*))+$")
    _root_oids = {}
    _extension_oids = {}

    def __init__(self, text=None, attributes=None):
        """Initialize the ID tag."""
        super().__init__(text, attributes)

        if self.__class__.oid_pattern.match(self.attributes.get("root")):
            segments = self.attributes["root"].split(".")
            for i, segment in enumerate(segments):
                if segment not in self._root_oids:
                    self.__class__._root_oids.setdefault(i, {})[segment] = _get_random_int(
                        len(segment)
                    )
        if self.attributes.get("extension") and self.__class__.oid_pattern.match(
            self.attributes["extension"]
        ):
            segments = self.attributes["extension"].split(".")
            for i, segment in enumerate(segments):
                if segment not in self._extension_oids:
                    self.__class__._extension_oids.setdefault(i, {})[segment] = _get_random_int(
                        len(segment)
                    )

    @classmethod
    def normalize(cls, value: str | None) -> str:
        """Normalize a string."""
        if value is None:
            return None
        else:
            return value.lower().strip()

    @classmethod
    def get_replacement_mapping(
        cls,
        normalized_tag: Tag,
        raw_values: set[Tag],
    ) -> dict[str, str]:
        """Get a replacement mapping."""
        sensitive_attr_replacements = None
        sensitive_attr_replacements = {}

        if cls.oid_pattern.match(normalized_tag.attributes["root"]):
            replacement_parts = []
            segments = normalized_tag.attributes["root"].split(".")
            for i, segment in enumerate(segments):
                if segment in cls._root_oids[i]:
                    replacement_parts.append(str(cls._root_oids[i][segment]))
                else:
                    raise ValueError(
                        f"Segment {segment} not found in root OID mapping for {normalized_tag.name}"
                    )
            if "extension" in normalized_tag.attributes:
                sensitive_attr_replacements["root"] = ".".join(replacement_parts)
                sensitive_attr_replacements["extension"] = cls.random_alpha_digits(
                    normalized_tag.attributes["extension"]
                )
        else:
            for sensitive_attr_key in cls.sensitive_attr:
                for key, value in normalized_tag.attributes.items():
                    if key == sensitive_attr_key:
                        sensitive_attr_replacements[key] = cls.random_alpha_digits(value)

        mapping = {}
        for tag in raw_values:
            attribute_replacements = tag.attributes.copy() if tag.attributes else None
            for attr, value in sensitive_attr_replacements.items():
                if attr in attribute_replacements:
                    attribute_replacements[attr] = value

        mapping[tag] = tag.__class__(text=tag.text, attributes=attribute_replacements)

        return mapping

    @staticmethod
    def random_alpha_digits(value):
        replacement = ""
        for char in value:
            if char.isdigit():
                replacement += str(randint(0, 9))
            elif char.isalpha():
                replacement += choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            else:
                replacement += char
        return replacement
