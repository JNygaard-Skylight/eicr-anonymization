"""Tests for the random_sw module."""

import random
import string

import pytest

from random_sw.main import (
    _family_names,
    _get_leading_trailing_whitespace,
    _given_names,
    _map_values_to_formatted_replacement,
    _match_case,
    _match_whitespace,
    _name_suffixes,
    _street_types,
    get_random_family_name_mapping,
    get_random_given_name_mapping,
    get_random_name_suffix_mapping,
    get_random_street_address_mapping,
)


@pytest.fixture(autouse=True)
def set_random_seed():
    """Set up a random seed for reproducibility."""
    random.seed(1)


def _normalize(text):
    return text.lower().strip().replace(".", "")


def _validate_mapping(orginal_values: set[str], actual: dict[str, str], expected_values: set[str]):
    """Validate the name mapping."""
    normalized_results = {_normalize(value) for value in actual.values()}
    assert len(actual) == len(orginal_values)
    assert len(normalized_results) == 1

    for orginal, actual_key, actual_value in zip(
        orginal_values, actual.keys(), actual.values(), strict=False
    ):
        assert orginal == actual_key
        assert normalized_results <= {_normalize(value) for value in expected_values}
        assert orginal.islower() == actual_value.islower()
        assert orginal.isupper() == actual_value.isupper()
        assert sum(c.isdigit() for c in orginal) == sum(c.isdigit() for c in actual_value)
        period_in_orginal = "." in orginal
        period_in_actual = "." in actual_value
        assert period_in_orginal == period_in_actual


class TestGetRandomValue:
    """Tests for the random_sw module."""

    @pytest.mark.parametrize(
        ("value", "expected_leading", "expected_trailing"),
        [
            ("Test", "", ""),
            ("Test ", "", " "),
            (" Test", " ", ""),
            (" Test ", " ", " "),
            ("   Test  ", "   ", "  "),
            ("\tTest\t", "\t", "\t"),
        ],
    )
    def test_get_trailing_leading_whitespace(self, value, expected_leading, expected_trailing):
        """Test the _get_leading_trailing_whitespace function."""
        assert _get_leading_trailing_whitespace(value) == (expected_leading, expected_trailing)

    @pytest.mark.parametrize(
        ("orginal_value", "new_value", "expected"),
        [
            ("test", "test", "test"),
            (" test", "test", " test"),
            ("test ", "test", "test "),
            (" test ", "test", " test "),
            ("   test  ", "test", "   test  "),
            ("\ttest\t", "test", "\ttest\t"),
        ],
    )
    def test_match_whitespace(self, orginal_value, new_value, expected):
        """Test the _match_whitespace function."""
        assert _match_whitespace(orginal_value, new_value) == expected

    @pytest.mark.parametrize(
        ("orginal_value", "new_value", "expected"),
        [
            ("test old value", "test new value", "test new value"),
            ("test old value", "Test New Value", "test new value"),
            ("test old value", "TEST NEW VALUE", "test new value"),
            ("Test Old Value", "Test New Value", "Test New Value"),
            ("TEST OLD VALUE", "test new value", "TEST NEW VALUE"),
            ("TEST OLD VALUE", "Test New Value", "TEST NEW VALUE"),
            ("TEST OLD VALUE", "TEST NEW VALUE", "TEST NEW VALUE"),
        ],
    )
    def test_match_case(self, orginal_value, new_value, expected):
        """Test the _match_case function."""
        assert _match_case(orginal_value, new_value) == expected

    def test_map_values_to_formatted_replacement(self):
        """Test the _map_values_to_formatted_replacement function."""
        raw_values = ["test", " test", "test ", " test ", "   test  ", "\ttest\t", "TEST"]
        replacement = "new value"
        expected = {
            "test": "new value",
            " test": " new value",
            "test ": "new value ",
            " test ": " new value ",
            "   test  ": "   new value  ",
            "\ttest\t": "\tnew value\t",
            "TEST": "NEW VALUE",
        }
        assert _map_values_to_formatted_replacement(raw_values, replacement) == expected

    def test_get_random_family_name_mapping(self):
        """Test the get_random_family_name_mapping function with multiple values."""
        orginal_values = {"Bloggs"}

        actual = get_random_family_name_mapping(orginal_values)
        _validate_mapping(orginal_values, actual, _family_names)

    def test_get_random_given_name_mapping(self):
        """Test the get_random_given_name_mapping function."""
        orginal_values = {"Joe"}
        normalized_value = "joe"

        actual = get_random_given_name_mapping(orginal_values, normalized_value)
        _validate_mapping(orginal_values, actual, _given_names)

    def test_get_random_given_name_mapping_initial(self):
        """Test the get_random_given_name_mapping function with a single letter."""
        orginal_values = {"J"}
        normalized_value = "j"

        actual = get_random_given_name_mapping(orginal_values, normalized_value)

        _validate_mapping(orginal_values, actual, string.ascii_lowercase)

    def test_get_random_name_suffix_mapping(self):
        """Test the get_random_name_suffix_mapping function."""
        # This function is not implemented in the provided code, so we can't test it.
        orginal_values = {"MD", " MD"}
        actual = get_random_name_suffix_mapping(orginal_values, attributes={"qualifier": "AC"})
        expected_values = [
            x["value"] for x in _name_suffixes if "qualifier" in x and x["qualifier"] == "AC"
        ]
        _validate_mapping(orginal_values, actual, expected_values)

    def test_get_random_street_address_mapping_simple(self):
        """Test the get_random_street_address_mapping function."""
        orginal_values = {"1 Wright Street"}
        actual = get_random_street_address_mapping(orginal_values)
        expected_street_types = {_normalize(x["name"]) for x in _street_types}

        normalized_results = {_normalize(value) for value in actual.values()}
        assert len(actual) == len(orginal_values)
        assert len(normalized_results) == 1

        for orginal, actual_key, actual_value in zip(
            orginal_values, actual.keys(), actual.values(), strict=False
        ):
            assert orginal == actual_key
            assert orginal.islower() == actual_value.islower()
            assert orginal.isupper() == actual_value.isupper()
            period_in_orginal = "." in orginal
            period_in_actual = "." in actual_value
            assert period_in_orginal == period_in_actual
            assert sum(c.isdigit() for c in orginal) == sum(c.isdigit() for c in actual_value)

            assert _normalize(orginal.split()[-1]) in expected_street_types


    def test_get_random_street_address_mapping_unit(self):
        """Test the get_random_street_address_mapping function with unit number."""
        orginal_values = {"9906 ACHORAGE RTE #8272"}
        actual = get_random_street_address_mapping(orginal_values)
        expected_street_types = {_normalize(x["name"]) for x in _street_types}

        normalized_results = {_normalize(value) for value in actual.values()}
        assert len(actual) == len(orginal_values)
        assert len(normalized_results) == 1

        for orginal, actual_key, actual_value in zip(
            orginal_values, actual.keys(), actual.values(), strict=False
        ):
            assert orginal == actual_key
            assert orginal.islower() == actual_value.islower()
            assert orginal.isupper() == actual_value.isupper()
            period_in_orginal = "." in orginal
            period_in_actual = "." in actual_value
            assert period_in_orginal == period_in_actual
            assert sum(c.isdigit() for c in orginal) == sum(c.isdigit() for c in actual_value)

    def test_Get_random_street_address_mapping_direction(self):
        orginal_values = {"297 N New Castle Aly", "297 N. New Castle Alley"}
        actual = get_random_street_address_mapping(orginal_values)

        normalized_results = {_normalize(value) for value in actual.values()}
        assert len(actual) == len(orginal_values)
        assert len(normalized_results) == 2

        for orginal, actual_key, actual_value in zip(
            orginal_values, actual.keys(), actual.values(), strict=False
        ):
            assert orginal == actual_key
            assert orginal.islower() == actual_value.islower()
            assert orginal.isupper() == actual_value.isupper()
            period_in_orginal = "." in orginal
            period_in_actual = "." in actual_value
            assert period_in_orginal == period_in_actual
            assert sum(c.isdigit() for c in orginal) == sum(c.isdigit() for c in actual_value)


