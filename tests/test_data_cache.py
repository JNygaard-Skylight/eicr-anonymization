"""Test test_data_cache.py."""

from data_cache.main import DataCache


class TestDataCache:
    """Test the DataCache class."""

    def test_empty(self):
        """Test the DataCache class."""
        data_cache = DataCache()
        assert len(data_cache) == 0

    def test_add_1(self):
        """Test the DataCache class."""
        tag = "test_tag"
        test_string = "test"
        data_cache = DataCache()
        data_cache.add(tag, test_string)
        assert len(data_cache) == 1
        assert len(data_cache[tag]) == 1
        assert len(data_cache[tag][test_string]) == 1

    def test_add_2_same(self):
        """Test the DataCache class."""
        tag = "test_tag"
        test_string = "test"
        data_cache = DataCache()
        data_cache.add(tag, test_string)
        data_cache.add(tag, test_string)
        assert len(data_cache) == 1
        assert len(data_cache[tag]) == 1
        assert len(data_cache[tag][test_string]) == 1

    def test_add_2_same_normalized(self):
        """Test the DataCache class."""
        tag = "test_tag"
        data_cache = DataCache()
        data_cache.add(tag, "test")
        data_cache.add(tag, "TEST")
        assert len(data_cache) == 1
        assert len(data_cache[tag]) == 1
        assert len(data_cache[tag]["test"]) == 2

    def test_add_2_similier(self):
        """Test the DataCache class. When two values are simliar they should be grouped."""
        tag = "test_tag"
        data_cache = DataCache()
        data_cache.add(tag, "123 1st Street")
        data_cache.add(tag, "123 1st St")
        assert len(data_cache) == 1
        assert len(data_cache[tag]) == 1
        assert len(data_cache[tag]["123 1st Street"]) == 2

    def test_add_2_not_similiar(self):
        """Test the DataCache class. When two values are not simliar they should not be grouped."""
        tag = "test_tag"
        data_cache = DataCache()
        data_cache.add(tag, "123 1st Street")
        data_cache.add(tag, "123 2nd Street")
        assert len(data_cache) == 1
        assert len(data_cache[tag]["123 1st Street"]) == 1
        assert len(data_cache[tag]["123 2nd Street"]) == 1

    def test_zip_4_5(self):
        """Test the DataCache class. When two values are not simliar they should not be grouped."""
        data_cache = DataCache()
        data_cache.add("70724")
        data_cache.add("70724-0504")
        assert len(data_cache) == 1
        assert len(data_cache["70724"]) == 2
