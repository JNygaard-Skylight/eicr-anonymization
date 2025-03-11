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
    _name_prefixes,
    _name_suffixes,
    get_random_family_name_mapping,
    get_random_given_name_mapping,
    get_random_name_prefix_mapping,
    get_random_name_suffix_mapping,
)


@pytest.fixture(autouse=True)
def set_random_seed():
    """Set up a random seed for reproducibility."""
    random.seed(1)


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
            ("Test Old Value", "test new value", "Test New Value"),
            ("Test Old Value", "Test New Value", "Test New Value"),
            ("Test Old Value", "TEST NEW VALUE", "Test New Value"),
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
        raw_values = ["test", " test", "test ", " test ", "   test  ", "\ttest\t", "Test", "TEST"]
        replacement = "new value"
        expected = {
            "test": "new value",
            " test": " new value",
            "test ": "new value ",
            " test ": " new value ",
            "   test  ": "   new value  ",
            "\ttest\t": "\tnew value\t",
            "Test": "New Value",
            "TEST": "NEW VALUE",
        }
        assert _map_values_to_formatted_replacement(raw_values, replacement) == expected

    def test_get_random_family_name_mapping(self):
        """Test the get_random_family_name_mapping function."""
        orginal_values = {"Bloggs"}

        actual = get_random_family_name_mapping(orginal_values)

        assert actual["Bloggs"] in _family_names

    def test_get_random_given_name_mapping(self):
        """Test the get_random_given_name_mapping function."""
        orginal_values = {"Joe"}
        normalized_value = "joe"

        actual = get_random_given_name_mapping(orginal_values, normalized_value)

        assert actual["Joe"] in _given_names

    def test_get_random_given_name_mapping_initial(self):
        """Test the get_random_given_name_mapping function with a single letter."""
        orginal_values = {"J"}
        normalized_value = "j"

        actual = get_random_given_name_mapping(orginal_values, normalized_value)

        assert actual["J"] in string.ascii_uppercase

    def test_get_random_given_name_mapping_initial_period(self):
        """Test the get_random_given_name_mapping function with a single letter and a period."""
        orginal_values = {"J."}
        normalized_value = "j"

        actual = get_random_given_name_mapping(orginal_values, normalized_value)

        assert actual["J."].endswith(".")
        assert actual["J."].removesuffix(".") in string.ascii_uppercase

    def test_get_random_name_prefix_mapping(self):
        """Test the get_random_name_prefix_mapping function."""
        orginal_values = {"Mr"}

        actual = get_random_name_prefix_mapping(orginal_values)

        prefix_abbrevations = [x["name"] for x in _name_prefixes if "abbreviation_only" in x]
        for prefix in _name_prefixes:
            print(prefix)
            if "abbreviation" in prefix:
                prefix_abbrevations.append(prefix["abbreviation"])


        assert actual["Mr"] in prefix_abbrevations

    def test_get_random_name_prefix_mapping_period(self):
        """Test the get_random_name_prefix_mapping function with a period."""
        orginal_values = {"Mr."}

        actual = get_random_name_prefix_mapping(orginal_values)

        prefix_abbrevations = [x["name"] for x in _name_prefixes if "abbreviation_only" in x]
        for prefix in _name_prefixes:
            if "abbreviation" in prefix:
                prefix_abbrevations.append(prefix["abbreviation"])

        assert actual["Mr."].endswith(".")
        assert actual["Mr."].removesuffix(".") in prefix_abbrevations

    def test_get_random_name_prefix_mapping_full(self):
        """Test the get_random_name_prefix_mapping function with a small prefix."""
        orginal_values = {"Doctor"}

        prefix_names = [x["name"] for x in _name_prefixes if "abbreviation_only" not in x]

        actual = get_random_name_prefix_mapping(orginal_values)

        assert actual["Doctor"] in prefix_names

    def test_get_random_name_suffix_mapping(self):
        """Test the get_random_name_suffix_mapping function."""
        # This function is not implemented in the provided code, so we can't test it.
        orginal_values = {"Jr"}
        actual = get_random_name_suffix_mapping(orginal_values)
        name_suffixes = [x["value"] for x in _name_suffixes]

        assert actual["Jr"] in name_suffixes
        assert not actual["Jr"].endswith(".")

    def test_get_random_name_suffix_mapping_qualifier(self):
        """Test the get_random_name_suffix_mapping function with a qualifier."""
        # This function is not implemented in the provided code, so we can't test it.
        orginal_values = {"MD"}
        actual = get_random_name_suffix_mapping(orginal_values, attributes={"qualifier": "AC"})
        name_suffixes = [x["value"] for x in _name_suffixes if "qualifier" in x and x["qualifier"] == "AC"]

        assert actual["MD"] in name_suffixes