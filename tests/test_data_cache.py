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
        data_cache = DataCache()
        data_cache.add("test")
        assert len(data_cache) == 1

    def test_add_2_same(self):
        """Test the DataCache class."""
        data_cache = DataCache()
        data_cache.add("test")
        data_cache.add("test")
        assert len(data_cache) == 1
        assert len(data_cache["test"]) == 1

    def test_add_2_same_normalized(self):
        """Test the DataCache class."""
        data_cache = DataCache()
        data_cache.add("test")
        data_cache.add("TEST")
        assert len(data_cache) == 1
        assert len(data_cache["test"]) == 2

    def test_add_2_similier(self):
        """Test the DataCache class. When two values are simliar they should be grouped."""
        data_cache = DataCache()
        data_cache.add("123 1st Street")
        data_cache.add("123 1st St")
        assert len(data_cache) == 1
        assert len(data_cache["123 1st Street"]) == 2


    def test_add_2_not_similiar(self):
        """Test the DataCache class. When two values are not simliar they should not be grouped."""
        data_cache = DataCache()
        data_cache.add("123 1st Street")
        data_cache.add("123 2nd Street")
        assert len(data_cache) == 2
        assert len(data_cache["123 1st Street"]) == 1
        assert len(data_cache["123 2nd Street"]) == 1

    def test_add_list_same(self):
        """Test the DataCache class. When two values are not simliar they should not be grouped."""
        data_cache = DataCache()
        data_cache.add_list(["123 1st Street", "123 1st Street"])
        assert len(data_cache) == 1
        assert len(data_cache["123 1st Street"]) == 1

    def test_add_list_similiar(self):
        """Test the DataCache class. When two values are simliar they should be grouped."""
        data_cache = DataCache()
        data_cache.add_list(["123 1st Street", "123 1st St"])
        assert len(data_cache) == 1
        assert len(data_cache["123 1st Street"]) == 2

    def test_add_list_not_similiar(self):
        """Test the DataCache class. When two values are not simliar they should not be grouped."""
        data_cache = DataCache()
        data_cache.add_list(["123 1st Street", "123 2nd Street"])
        assert len(data_cache) == 2
        assert len(data_cache["123 1st Street"]) == 1
        assert len(data_cache["123 2nd Street"]) == 1