"""Tests for the random_sw module."""

import random

from random_sw.main import (
    get_random_family_name,
    get_random_given_name,
    get_random_name_prefix,
    get_random_name_suffix,
)


class TestRandomSw:
    """Tests for the random_sw module."""

    # Set the seed for the random number generator to get reproducible results.
    random.seed(1)

    def test_get_random_family_name(self):
        """Test if the returned family name is in the list of family names."""
        expected = "Averross"
        actual = get_random_family_name()
        assert actual == expected


    def test_get_random_given_name(self):
        """Test if the returned family name is in the list of family names."""
        # random.seed(42)
        expected = "Ben"
        actual = get_random_given_name()
        assert actual == expected


    def test_get_random_name_prefix(self):
        """Test if the returned family name is in the list of family names."""
        expected = "Darth"
        actual = get_random_name_prefix()
        assert actual == expected


    def test_get_random_name_suffix(self):
        """Test if the returned family name is in the list of family names."""
        expected = "II"
        actual = get_random_name_suffix()
        assert actual == expected
