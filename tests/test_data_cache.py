"""Test test_data_cache.py."""

import pytest

from DataCache import NormalizedTagGroups
from tags.Tag import FamilyTag


class TestDataCache:
    """Test the DataCache class."""

    def test_init(cls):
        """Test the initialization of the NormalizedTagGroups class."""
        data_cache = NormalizedTagGroups()
        assert len(data_cache) == 0

    def test_add(cls):
        """Test the add method of the NormalizedTagGroups class."""
        data_cache = NormalizedTagGroups()
        tag = FamilyTag("Bloggs")

        data_cache.add(tag)

        assert len(data_cache) == 1
        assert len(data_cache[tag.normalized_hash]) == 1

    def test_add_multiple(cls):
        """Test the add method of the NormalizedTagGroups class with multiple tags."""
        data_cache = NormalizedTagGroups()
        tag1 = FamilyTag("Bloggs")
        tag2 = FamilyTag("Smith")

        data_cache.add(tag1)
        data_cache.add(tag2)

        assert len(data_cache) == 2
        assert len(data_cache[tag1.normalized_hash]) == 1
        assert len(data_cache[tag2.normalized_hash]) == 1


    def test_add_same(cls):
        """Test the add method of the NormalizedTagGroups class with the same tag."""
        data_cache = NormalizedTagGroups()
        tag = FamilyTag("Bloggs")

        data_cache.add(tag)
        data_cache.add(tag)

        assert len(data_cache) == 1
        assert len(data_cache[tag.normalized_hash]) == 1

    def test_add_similiar(cls):
        """Test the add method of the NormalizedTagGroups class with similar tags."""
        data_cache = NormalizedTagGroups()
        tag1 = FamilyTag("Bloggs")
        tag2 = FamilyTag("BLOGGS")

        data_cache.add(tag1)
        data_cache.add(tag2)

        assert len(data_cache) == 1
        assert len(data_cache[tag1.normalized_hash]) == 2
