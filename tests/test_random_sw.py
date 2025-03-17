"""Tests for the random_sw module."""

import random
import string

import pytest
from tabulate import tabulate

from random_sw.main import (
    _family_names,
    _get_leading_trailing_whitespace,
    _given_names,
    _map_values_to_formatted_replacement,
    _match_case,
    _match_punctuation,
    _match_whitespace,
    _name_suffixes,
    _street_types,
    get_random_family_name_mapping,
    get_random_given_name_mapping,
    get_random_name_suffix_mapping,
    get_random_postal_code_mapping,
    get_random_street_address_mapping,
)


def _normalize(text):
    return text.lower().strip().replace(".", "")


def _validate_mapping(
    orginal_values: set[str],
    actual: dict[str, str],
    num_normalized_results: int = 1,
    possible_values: set[str] | None = None,
):
    """Validate the name mapping."""
    normalized_results = {_normalize(value) for value in actual.values()}
    assert len(actual) == len(orginal_values)
    assert len(normalized_results) == num_normalized_results

    for orginal, actual_key, actual_value in zip(
        orginal_values, actual.keys(), actual.values(), strict=False
    ):
        print(
            tabulate(
                [[orginal, actual_key, actual_value]],
                headers=["Original", "Normalized", "Replacement"],
            )
        )
        assert orginal == actual_key
        if possible_values is not None:
            assert normalized_results <= {_normalize(value) for value in possible_values}
        assert orginal.islower() == actual_value.islower()
        assert orginal.isupper() == actual_value.isupper()
        assert sum(c.isdigit() for c in orginal) == sum(c.isdigit() for c in actual_value)
        period_in_orginal = "." in orginal
        period_in_actual = "." in actual_value
        assert period_in_orginal == period_in_actual


class TestUtils:
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

    @pytest.mark.parametrize(
        ("orginal_value", "new_value", "expected"),
        [
            ("test", "test", "test"),
            ("test", "test.", "test"),
            ("test.", "test", "test."),
            ("test.", "test.", "test."),
            ("t.e.s.t.", "test", "test."),
            ("t.e.s.t.", "test.", "test."),
        ],
    )
    def test_match_punctuation(self, orginal_value, new_value, expected):
        """Test the _match_punctuation function."""
        assert _match_punctuation(orginal_value, new_value) == expected

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


class TestGetRandomValue:
    """Tests for the random_sw module."""

    @pytest.fixture
    def set_random_seed(self, request):
        """Set up a random seed for reproducibility.

        This fixture ensures that the random seed is set to a fixed value for the first iteration of
        each test function. This ensures that we get deterministic results regardless of the order
        in which the tests are run.
        """
        callspec = getattr(request.node, "callspec", None)
        repeat_iteration = callspec.params.get("__pytest_repeat_step_number", 0) if callspec else 0
        if repeat_iteration == 0:
            random.seed(1)

    @pytest.mark.repeat(4)
    def test_get_random_family_name_mapping(self, set_random_seed):
        """Test the get_random_family_name_mapping function with multiple values."""
        orginal_values = {"Bloggs"}

        actual = get_random_family_name_mapping(orginal_values)
        _validate_mapping(orginal_values, actual, possible_values=_family_names)

    @pytest.mark.parametrize(
        ("orginal_values", "normalized_value", "num_normalized_results", "possible_values"),
        [({"Smith"}, "smith", 1, _given_names), ("T", "t", 1, string.ascii_lowercase)],
    )
    @pytest.mark.repeat(7)
    def test_get_random_given_name_mapping(
        self,
        set_random_seed,
        orginal_values,
        normalized_value,
        num_normalized_results,
        possible_values,
    ):
        """Test the get_random_given_name_mapping function."""
        actual = get_random_given_name_mapping(
            orginal_values, normalized_value, num_normalized_results
        )
        _validate_mapping(orginal_values, actual, num_normalized_results, possible_values)

    @pytest.mark.parametrize(
        ("orginal_values", "possible_values", "qualifier"),
        [
            ({"MD"}, [x["value"] for x in _name_suffixes], None),
            (
                {"DO", " DO"},
                [x["value"] for x in _name_suffixes if "qualifier" in x and x["qualifier"] == "AC"],
                "AC",
            ),
        ],
    )
    @pytest.mark.repeat(2)
    def test_get_random_name_suffix_mapping(
        self, set_random_seed, orginal_values, possible_values, qualifier
    ):
        """Test the get_random_name_suffix_mapping function."""
        # This function is not implemented in the provided code, so we can't test it.
        actual = get_random_name_suffix_mapping(orginal_values, attributes={"qualifier": qualifier})
        _validate_mapping(orginal_values, actual, possible_values=possible_values)

    @pytest.mark.parametrize(
        ("orginal_values", "num_normalized_results"),
        [
            ({"1 Wright Street"}, 1),
            ({"9906 ACHORAGE RTE #8272"}, 1),
            ({"297 N New Castle Aly", "297 N. New Castle Alley"}, 2),
        ],
    )
    @pytest.mark.repeat(5)
    def test_get_random_street_address_mapping(
        self, set_random_seed, orginal_values, num_normalized_results
    ):
        actual = get_random_street_address_mapping(orginal_values)

        normalized_results = {_normalize(value) for value in actual.values()}
        assert len(actual) == len(orginal_values)
        assert len(normalized_results) == num_normalized_results

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

    @pytest.mark.parametrize(
        ("orginal_values", "normalized_value", "num_normalized_results"),
        [({"96972"}, "96972", 1), ({"89513-9129", "89513"}, "89513", 2)],
    )
    @pytest.mark.repeat(4)
    def test_get_random_postal_code_mapping(
        self, set_random_seed, orginal_values, normalized_value, num_normalized_results
    ):
        """Test the get_random_postal_code_mapping function."""
        # This function is not implemented in the provided code, so we can't test it.
        actual = get_random_postal_code_mapping(orginal_values, normalized_value)
        _validate_mapping(orginal_values, actual, num_normalized_results)
