"""Test the normalization function."""

from main import normalize_text


class TestNormalization:
    """Tests for the normalization function."""

    def test_simple_name(self):
        """Test the normalize_text function with a simple name."""
        orginal_value = "Joe Bloggs"
        orginal_value_upper = "JOE BLOGGS"
        assert normalize_text(orginal_value) == normalize_text(orginal_value_upper)

    def test_with_address_period(self):
        """Test the normalize_text function with an address with a period."""
        orginal_value = "123 Main St"
        original_value_period = "123 Main St."
        assert normalize_text(orginal_value) == normalize_text(original_value_period)

    def test_with_address_abbrevation(self):
        """Test the normalize_text function with an address with an abbreviation."""
        orginal_value = "123 Main St"
        original_value_abbrev = "123 Main Street"
        assert normalize_text(orginal_value) == normalize_text(original_value_abbrev)

