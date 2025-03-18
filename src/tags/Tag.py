"""Tag Class."""

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


def _read_yaml(file_path: str) -> list[ReplacementType]:
    """Read a YAML file and return its contents as a list of strings."""
    with open(file_path) as file:
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

    registry: ClassVar[dict[str, "Tag"]] = {}

    def __init_subclass__(cls, **kwargs) -> None:
        """Register the subclass in the registry if it has a name."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, 'name') and cls.name:
            instance = cls()
            Tag.registry[cls.name] = instance


    def __init__(self, name: str, replacement_filepath: str | None = None):
        """Initialize the tag class."""
        self._name = name
        if replacement_filepath:
            self.replacements = _read_yaml(replacement_filepath)

    @property
    def name(self) -> str:
        """Get the name of the tag."""
        return self._name

    @property
    def replacements(self) -> set[ReplacementType]:
        """Get the replacements."""
        return self.replacements

    def _get_replacement_values(
        self,
    ) -> list[str]:
        return [x["value"] for x in self.replacements]

    def normalize(self, value: str) -> str:
        """Normalize a string."""
        return value.lower().strip().replace(".", "")

    def is_equal(self, a: str, b: str) -> bool:
        """Check if two strings are equal."""
        return self.normalize(a) == self.normalize(b)

    def get_replacement_mapping(
        self,
        raw_values: set[str],
        normalized_value: str | None = None,
        attributes: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """Get a replacement mapping."""
        replacement = choice(self._get_replacement_values())
        return _map_values_to_formatted_replacement(raw_values, replacement)


class FamilyTag(Tag):
    """Family tag class."""

    def __init__(self):
        """Initialize the Family tag class."""
        super().__init__("family", "data/family_replacements.yaml")


class GivenTag(Tag):
    """Given tag class."""

    def __init__(self):
        """Initialize the Given tag class."""
        super().__init__("given", "data/given_replacements.yaml")

    def get_replacement_mapping(self, raw_values, normalized_value=None, attributes=None):
        """Get a replacement mapping."""
        if len(normalized_value) == 1:
            replacement = choice(ascii_uppercase)
        else:
            replacement = choice(self.replacements)["value"]
        return _map_values_to_formatted_replacement(raw_values, replacement)


class PrefixTag(Tag):
    """Name prefix tag class."""

    def __init__(self):
        """Initialize the Name prefix tag class."""
        super().__init__("prefix", "data/name_prefix_replacements.yaml")

    def get_replacement_mapping(self, raw_values, normalized_value=None, attributes=None):
        """Get a random Star Wars themed name prefix."""
        replacement = choice(self.replacements)["value"]

        is_abbreviation_list = [True for x in raw_values if x.endswith(".") or len(x) <= 4]
        num_abbreviations = len([is_abbreviation_list for x in is_abbreviation_list if x])
        has_full_name = len(is_abbreviation_list) != len(raw_values)

        if has_full_name and num_abbreviations >= 1:
            # if it is a mix of a full prefix and an abbreviation, we can pick any prefix that is
            # not abbreviation only
            replacement = choice(
                [
                    x
                    for x in self.replacements
                    if x["abbreviations"] and "abbreviation_only" not in x
                ]
            )
            replacement_name = replacement["value"]
            replacement_abbreviation = choice(replacement["abbreviations"])
        elif has_full_name:
            # if it has only full names, we can pick any prefix that is not abbreviation only
            replacement_name = choice(
                [x for x in self.replacements if "abbreviation_only" not in x]
            )["value"]
        else:
            # if we got here we can assume it is only a single abbreviation
            replacement_abbreviation = [
                x["value"] for x in self.replacements if "abbreviation_only" in x
            ]
            for prefix in self.replacements:
                if "abbreviation" in prefix:
                    replacement_abbreviation.append(choice(prefix["abbreviations"]))
            replacement_abbreviation = choice(replacement_abbreviation)

        mappings = {}
        for raw_value, is_abbreviation in zip_longest(raw_values, is_abbreviation_list):
            replacement = replacement_abbreviation if is_abbreviation else replacement_name
            mappings[raw_value] = _match_case(
                raw_value, _match_whitespace(raw_value, _match_punctuation(raw_value, replacement))
            )
        return mappings


class SuffixTag(Tag):
    """Name suffix tag class."""

    def __init__(self):
        """Initialize the Name suffix tag class."""
        super().__init__("suffix", "data/name_suffix_replacements.yaml")

    def get_replacement_mapping(self, raw_values, normalized_value=None, attributes=None):
        """Get a replacement mapping."""
        if attributes and attributes.get("qualifier") == "AC":
            replacement = choice(
                [suffix for suffix in self.replacements if suffix.get("qualifier") == "AC"]
            )["value"]
        else:
            replacement = choice(self.replacements)["value"]

        return _map_values_to_formatted_replacement(raw_values, replacement)


class StreetAddressTag(Tag):
    """Street address tag class."""

    _street_names = _read_yaml("data/street_names.yaml")
    _street_types = _read_yaml("data/street_types.yaml")

    def __init__(self):
        """Initialize the Street address tag class."""
        super().__init__("streetAddressLine")

    def get_replacement_mapping(
        self,
        raw_values: set[str],
        normalized_value: str | None = None,
        attributes: dict[str, str] | None = None,
    ):
        """Get a random Star Wars themed street address. for the set of simliar addresses.

        I want to do something like this:
        1) Parse the first address in the set, we can be confident that all addresses in the set
        refer to the same address
        3) Get a random value for each found address component
        4) Build the new address as we did in get_random_street_address_line, but this time using
        the preselected values
        """
        # Parse the first address in the set, we can be confident that all addresses in the set
        # refer to the same address
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
            new_street_name = choice(self._street_names)["value"]
        if "StreetNamePostType" in tagged_address:
            # If there is more than one unique street type, we can assume an abbreviations was used.
            # so pick a type with enough abbreviations.
            if num_street_types >= 2:
                possible_street_types = [
                    street_type
                    for street_type in self._street_types
                    if len(street_type.get("abbreviations", [])) >= num_street_types - 1
                ]
                new_street_type = choice(possible_street_types)
            else:
                new_street_type = choice(self._street_types)
        if "OccupancyIdentifier" in tagged_address:
            pattern = re.compile(r"\d")
            new_occupancy_identifier = pattern.sub(
                lambda x: str(_get_random_int(1)), tagged_address["OccupancyIdentifier"]
            )

        new_value_mapping = {}
        used_street_type_name = False
        for raw_value, old_address in zip_longest(raw_values, tagged_addresses):
            parsed_address = usaddress.parse(raw_value)

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
                        new_street_type_x = choice(new_street_type["abbreviations"]) + "."
                    elif not used_street_type_name:
                        new_street_type_x = new_street_type["name"]
                        used_street_type_name = True
                    else:
                        new_street_type_x = choice(new_street_type["abbreviations"])

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


class CityTag(Tag):
    """City tag class."""

    def __init__(self):
        """Initialize the City tag class."""
        super().__init__("city", "data/city_replacements.yaml")


class CountyTag(Tag):
    """County tag class."""

    def __init__(self):
        """Initialize the County tag class."""
        super().__init__("county", "data/county_replacements.yaml")


class StateTag(Tag):
    """State tag class."""

    def __init__(self):
        """Initialize the State tag class."""
        super().__init__("state", "data/state_replacements.yaml")

    def get_replacement_mapping(self, raw_values, normalized_value=None, attributes=None):
        """Get a replacement mapping."""
        replacement = choice(choice(self.replacements)["abbreviations"])
        return _map_values_to_formatted_replacement(raw_values, replacement)


class CountryTag(Tag):
    """Country tag class."""

    def __init__(self):
        """Initialize the Country tag class."""
        super().__init__("country", "data/country_replacements.yaml")


class PostalCodeTag(Tag):
    """Postal code tag class."""

    def __init__(self):
        """Initialize the Postal code tag class."""
        super().__init__("postalCode")

    def get_replacement_mapping(self, raw_values, normalized_value=None, attributes=None):
        """Get a random Star Wars themed postal code for the set of simliar postal codes."""
        all_parts = set()
        mappings_1 = {}
        for raw_value in raw_values:
            parts = re.split(r"\s|-", raw_value)
            mappings_1[raw_value] = parts
            all_parts.update(parts)

        mappings = {}
        for parts in all_parts:
            # replace all digits with a random digit
            replacement = re.sub(r"\d", lambda x: str(randint(0, 9)), normalized_value)
            # replace all lowealphabetic characters with a random lowercase letter
            replacement = re.sub(r"[a-z]", lambda x: choice(ascii_lowercase), replacement)
            # replace all uppercase alphabetic characters with a random uppercase letter
            replacement = re.sub(r"[A-Z]", lambda x: choice(ascii_lowercase), replacement)
            mappings[parts] = replacement

        # Rebuild the original values with the new parts
        for mappings_1_key, mappings_1_value in mappings_1.items():
            new_parts = []
            for part in mappings_1_value:
                if part in mappings:
                    new_parts.append(mappings[part])
                else:
                    new_parts.append(part)
            if " " in mappings_1_key:
                new_value = " ".join(new_parts)
            elif "-" in mappings_1_key:
                new_value = "-".join(new_parts)
            else:
                new_value = "".join(new_parts)
            mappings_1[mappings_1_key] = _match_formatting(mappings_1_key, new_value)
        return mappings

    def normalize(self, value: str) -> str:
        """Normalize a zip code."""
        base_zip_code_length = 5
        if len(value) == base_zip_code_length:
            return value
        else:
            return value[:base_zip_code_length]
