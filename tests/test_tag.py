"""Test the Tag class."""
import pytest

from tags.Tag import FamilyTag


def test_immutable_name():
    """Test that the name of the tag is immutable."""
    tag = FamilyTag()
    with pytest.raises(AttributeError):
        tag.name = "new_name"

def test_immutable_attributes():
    """Test that the attributes of the tag are immutable."""
    tag = FamilyTag()
    with pytest.raises(AttributeError):
        tag.sensitive_attr = "new_value"

def test_immutable_replacement_values():
    """Test that the replacement values of the tag are immutable."""
    tag = FamilyTag()
    with pytest.raises(AttributeError):
        tag.replacement_values = "new_value"


def test_equality_empty():
    """Test the equality of two tags."""
    tag1 = FamilyTag()
    tag2 = FamilyTag()
    # Assert both tags are the same class
    assert tag1 == tag2

def test_equality_same_text():
    """Test the equality of two tags."""
    tag1 = FamilyTag("Bloggs")
    tag2 = FamilyTag("Bloggs")
    # Assert both tags are the same class
    assert tag1 == tag2

def test_equality_same_attr():
    """Test the equality of two tags."""
    tag1 = FamilyTag(attributes={"test": "value"})
    tag2 = FamilyTag(attributes={"test": "value"})
    # Assert both tags are the same class
    assert tag1 == tag2

def test_equality_different_names():
    """Test the equality of two tags."""
    tag1 = FamilyTag("Bloggs")
    tag2 = FamilyTag("Smith")
    # Assert both tags are the same class
    assert tag1 != tag2

def test_equality_different_attributes():
    """Test the equality of two tags."""
    tag1 = FamilyTag(attributes={"test": "value"})
    tag2 = FamilyTag(attributes={"test": "other_value"})
    # Assert both tags are the same class
    assert tag1 != tag2


def test_hash():
    """Test the hash of the tag."""
    tag1 = FamilyTag("Bloggs")
    tag2 = FamilyTag("Bloggs")
    # Assert both tags are the same class
    test_set = {tag1, tag2}
    assert len(test_set) == 1

def test_hash_different_names():
    """Test the hash of the tag."""
    tag1 = FamilyTag("Bloggs")
    tag2 = FamilyTag("Smith")
    # Assert both tags are the same class
    test_set = {tag1, tag2}
    assert len(test_set) == 2

def test_hash_same_attributes():
    """Test the hash of the tag."""
    tag1 = FamilyTag(attributes={"test": "value"})
    tag2 = FamilyTag(attributes={"test": "value"})
    # Assert both tags are the same class
    test_set = {tag1, tag2}
    assert len(test_set) == 1

def test_hash_different_attributes():
    """Test the hash of the tag."""
    tag1 = FamilyTag(attributes={"test": "value"})
    tag2 = FamilyTag(attributes={"test": "other_value"})
    # Assert both tags are the same class
    test_set = {tag1, tag2}
    assert len(test_set) == 2


def test_hash_potentially_normalized():
    """Test the normalized hash of the tag."""
    tag1 = FamilyTag("Bloggs")
    tag2 = FamilyTag("BLOGGS")
    # Assert both tags are the same class
    test_set = {tag1, tag2}
    assert len(test_set) == 2


def test_normalized_hash():
    """Test the normalized hash of the tag."""
    tag1 = FamilyTag("Bloggs")
    tag2 = FamilyTag("BLOGGS")
    # Assert both tags are the same class
    assert tag1.normalized_hash == tag2.normalized_hash


class TestFamilyTag:
    """Test the FamilyTag class."""

    def test_get_replacement_mapping():
        """Test the get_replacement_mapping method."""
        tag1 = FamilyTag("Bloggs")
        # Assert both tags are the same class
        mappings = tag1.get_replacement_mapping({tag1})
        assert len(mappings) == 1
        assert next(iter(mappings.values())).text == "REMOVED"
