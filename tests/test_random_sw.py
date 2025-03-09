"""Tests for the random_sw module."""

import random

import pytest

from random_sw.main import (
    get_random_family_name,
    get_random_given_name,
    get_random_name_prefix,
    get_random_name_suffix,
    get_random_street_address_line,
)


@pytest.fixture(autouse=True)
def set_random_seed():
    """Set up a random seed for reproducibility."""
    print("Setting random seed")
    random.seed(1)


class TestGetRandomValue:
    """Tests for the random_sw module."""

    def test_get_random_family_name(self):
        """Test if the returned family name is in the list of family names."""
        expected = "Averross"
        actual = get_random_family_name()
        assert actual == expected

    def test_get_random_given_name(self):
        """Test if the returned family name is in the list of family names."""
        # random.seed(42)
        expected = "Han"
        actual = get_random_given_name("Sally")
        assert actual == expected

    def test_get_random_name_prefix(self):
        """Test if the returned family name is in the list of family names."""
        expected = "Captain"
        actual = get_random_name_prefix()
        assert actual == expected

    class TestGetRandomNameSuffix:
        """Tests for the get_random_name_suffix function."""

        def test_get_random_name_suffix(self):
            """Test if the returned family name is in the list of family names."""
            expected = "IV"
            actual = get_random_name_suffix()
            assert actual == expected

        def test_get_random_name_suffix_with_qualifier(self):
            """Test if the returned family name is in the list of family names."""
            expected = "DO"
            actual = get_random_name_suffix(attributes={"qualifier": "AC"})
            assert actual == expected


class TestGetRandomStreetAddressLine:
    """Tests for the get_random_street_address_line function."""

    def test_get_random_street_address_line_simple(self):
        """Test the get_random_street_address_line function for a simple street address."""
        orginal_value = "7 Maplewood Drive"
        expected = "3 Spire Blvd"
        actual = get_random_street_address_line(orginal_value)
        assert actual == expected

    def test_get_random_street_address_line_with_multi_word_name(self):
        """Test the get_random_street_address_line function for an address with a multi-word name."""
        orginal_value = "12 Cedar Ridge Court"
        expected = "27 Spire Blvd"
        actual = get_random_street_address_line(orginal_value)
        assert actual == expected

    def test_get_random_street_address_line_pre_direction(self):
        """Test the get_random_street_address_line function for an address with a pre-direction."""
        orginal_value = "320 NE Maple Drive"
        expected = "237 NE Harbor District Cir"
        actual = get_random_street_address_line(orginal_value)
        assert actual == expected

    def test_get_random_street_address_line_post_direction(self):
        """Test the get_random_street_address_line function for an address with a post-direction."""
        orginal_value = "7820 Oakwood Drive SE"
        expected = "3201 Spire Blvd SE"
        actual = get_random_street_address_line(orginal_value)
        assert actual == expected
