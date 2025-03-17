"""Data Cache Module."""

from typing import TypedDict

from rapidfuzz import fuzz, process

"""
the_cache = {
    "family": {
        "bloggs":{
          "values": {"Bloggs", " Bloggs", " bloggs "},
          "attributes": {"lang": "en"},
        },
        "Smith": {"smith"},
    },
    "given": {
        "joe": {"Joe", "JOE"},
        "bob": {"Bob", "bob", "BOB"},
    },
}
"""


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

    _tag_cache: dict[str, NormalizedEntry] = {}
    tag: str

    def __init__(self, tag: str, values: set[str], attributes: dict[str, str] | None):
        """Initialize the tag cache."""
        self.tag = tag
        self._tag_cache = {}
        self._add_new_key(values, attributes)

    def __getitem__(self, key: str) -> set[str]:
        """Get the item in the tag cache."""
        return self._tag_cache[self.get_key(key)].values

    def __len__(self) -> int:
        """Get the length of the tag cache."""
        return len(self._tag_cache)

    def get_key(self, input: str) -> str:
        """Get the normalized key for a given key. If it does not exist, create a new key."""
        normalized_input = _normalize(input)

        key = None
        if normalized_input not in self._tag_cache:
            score = process.extractOne(normalized_input, self._tag_cache.keys(), scorer=fuzz.ratio)
            if score and score[1] > 83:
                key = score[0]
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

        if attributes is not None:
            self.add_attributes(key, attributes)


CacheType = dict[str, TagCache]


class DataCache:
    """A simple data cache class."""

    def __init__(self):
        """Initialize the data cache."""
        self._cache: CacheType = {}

    def __len__(self) -> int:
        """Get the length of the data cache."""
        return len(self._cache)

    def __getitem__(self, key: str) -> TagCache:
        """Get an item from the data cache."""
        return self._cache[key]

    def add(self, tag: str, value: str, attributes: dict[str, str] | None = None):
        """Add a value to the data cache."""
        if tag not in self._cache:
            self._cache[tag] = TagCache(tag, value, attributes)
        else:
            self._cache[tag].add(value, attributes)


def _normalize(text: str) -> str:
    """Normalize the text."""
    return text.lower().replace(".", "").strip()
