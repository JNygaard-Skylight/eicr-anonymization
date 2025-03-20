"""Data Cache Module."""

from collections.abc import Callable

from tags.Tag import Tag


class NormalizedEntry:
    """A normalized entry in the data cache."""

    values: set[str]
    attributes: dict[str, str] | None

    def __init__(self, values: set[str], attributes: dict[str, str] | None):
        """Initialize the normalized entry."""
        self.values = values
        self.attributes = attributes

    def add(self, value: str):
        """Add a value to the normalized entry."""
        self.values.add(value)


class TagCache:
    """A tag cache in the data cache."""

    _tag_cache: dict[str, NormalizedEntry]
    tag: Tag
    is_equal: Callable[[str, str], bool]

    def __init__(
        self, tag: str, value: str | None = None, attributes: dict[str, str] | None = None
    ):
        """Initialize the tag cache."""
        self.tag = Tag.from_name(tag)
        self._tag_cache = {}
        if value:
            self._add_new_key(value, attributes)

    def __getitem__(self, key: str) -> set[str]:
        """Get the item in the tag cache."""
        return self._tag_cache[self.get_key(key)]

    def __iter__(self):
        """Iterate over the tag cache."""
        return iter(self._tag_cache.keys())

    def __len__(self) -> int:
        """Get the length of the tag cache."""
        return len(self._tag_cache)

    def get_key(self, input: str) -> str:
        """Get the normalized key for a given key. If it does not exist, create a new key."""
        normalized_input = _normalize(input)

        key = None
        if normalized_input not in self._tag_cache:
            for _key in self._tag_cache:
                if self.tag.is_equal(normalized_input, _key):
                    key = _key
                    break
        else:
            key = normalized_input

        return key

    def add_attributes(self, key: str, attributes: list[dict[str, str]]):
        """Add an attribute to an existing item in the cache."""
        self._tag_cache[key].attributes = attributes

    def _add_new_key(self, raw_value: str, attributes: dict[str, str] | None = None):
        """Add a new item to the cache."""
        self._tag_cache[_normalize(raw_value)] = NormalizedEntry({raw_value}, attributes)

    def add(self, raw_value: str, attributes: dict[str, str] | None = None):
        """Add to an existing item in the cache."""
        key = self.get_key(raw_value)
        if key is None:
            self._add_new_key(raw_value)
        else:
            self._tag_cache[key].add(raw_value)

    def items(self):
        """Get the items in the tag cache."""
        return self._tag_cache.items()

CacheType = dict[str, TagCache]


class DataCache:
    """A simple data cache class."""

    def __init__(self):
        """Initialize the data cache."""
        self._cache: CacheType = {}
        for tag in Tag.get_registry().values():
            self._cache[tag.name] = TagCache(tag.name)

    def __len__(self) -> int:
        """Get the length of the data cache."""
        return len(self._cache)

    def __getitem__(self, key: str) -> TagCache:
        """Get an item from the data cache."""
        if key not in self._cache:
            raise KeyError(f"Tag {key} not found in cache.")
        return self._cache[key]

    def __iter__(self):
        """Iterate over the data cache."""
        return iter(self._cache.keys())

    def add(
        self,
        tag: str,
        value: str,
        attributes: dict[str, str] | None = None,
    ):
        """Add a value to the data cache."""
        if tag not in self._cache:
            raise KeyError(f"Unknown Tag: {tag}")
        else:
            self._cache[tag].add(value, attributes)

    def items(self):
        """Get the items in the data cache."""
        return self._cache.items()


def _normalize(text: str) -> str:
    """Normalize the text."""
    return text.lower().replace(".", "").strip()
