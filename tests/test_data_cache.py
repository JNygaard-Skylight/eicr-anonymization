"""Test test_data_cache.py."""

import pytest

from DataCache import DataCache
from tags.Tag import Tag


class TestDataCache:
    """Test the DataCache class."""

    def test_init(self):
        """Test the empty cache.

        When the cache is first created it should have an entry for each tag
        that is registered in the Tag registry and the cache for each Tag should be empty.
        """
        registry = Tag.get_registry()
        data_cache = DataCache()
        assert len(data_cache) == len(registry)
        for tag in registry:
            assert tag in data_cache
            assert len(data_cache[tag]) == 0


    def test_add_unknown_tag(self):
        """Test adding a value with an unknown tag.

        The cache should raise a KeyError if the tag is not in the registry.
        """
        data_cache = DataCache()
        tag = "test_tag"
        value = "test_value"
        with pytest.raises(KeyError):
            data_cache.add(tag, value)

    def test_add_known_tag(self):
        """Test adding a value to the cache.

        The cache should be able to add a value to the cache and return the correct key.
        """
        data_cache = DataCache()
        tag = "family"
        value = "test_value"
        data_cache.add(tag, value)
        assert len(data_cache[tag]) == 1 # There should only be one entry under the family tag
        assert value in data_cache[tag] # That entry should have a key equal to the test value
        assert len(data_cache[tag][value].values) == 1 # There should only be one value in the entry
        assert value in data_cache[tag][value].values # That value should be the same as the test value

    def test_add_multiple_values_similiar(self):
        """Test adding multiple values to the cache.

        The two values only have case differences and should be added to the same cache entry.
        """
        data_cache = DataCache()
        tag = "family"
        value1 = "test_value"
        value2 = "TEST_VALUE"
        data_cache.add(tag, value1)
        data_cache.add(tag, value2)
        assert len(data_cache[tag]) == 1 # There should only be one entry under the family tag
        assert value1 in data_cache[tag] # That entry should have a key equal to the test value
        assert len(data_cache[tag][value1].values) == 2 # There should be 2 values in the entry
        assert {value1, value2} == data_cache[tag][value2].values # Both the test values should be in the entry


    def test_add_multiple_values_different(self):
        """Test adding multiple values to the cache.

        The two values are different and should be added to different cache entries.
        """
        data_cache = DataCache()
        tag = "family"
        value1 = "test_value"
        value2 = "another_value"
        data_cache.add(tag, value1)
        data_cache.add(tag, value2)
        assert len(data_cache[tag]) == 2
        # There should be 2 entries under the family tag
        assert value1 in data_cache[tag] # The first entry should have a key equal to the test value
        assert len(data_cache[tag][value1].values) == 1 # The first entry should only have one value
        assert value1 in data_cache[tag][value1].values # The first entry should have the test value
        assert value2 in data_cache[tag] # The second entry should have a key equal to the test value
        assert len(data_cache[tag][value2].values) == 1 # The second entry should only have one value
        assert value2 in data_cache[tag][value2].values # The second entry should have the test value