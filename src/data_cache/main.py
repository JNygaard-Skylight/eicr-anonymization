"""Data Cache Module."""

from rapidfuzz import fuzz, process


class DataCache:
    """A simple data cache class."""

    def __init__(self):
        """Initialize the data cache."""
        self.data = {}
        self.attributes = {}

    def add_attributes(self, key: str, attributes: list[dict[str, str]]):
        """Add an attribute to an existing item in the cache."""
        self.attributes[key] = attributes
    def add_list(self, value: list[str]):
        """Set the data from a list of matches."""
        for item in value:
            self.add(item)

    def _add_new_key(self, raw_value: str):
        """Add a new item to the cache."""
        self.data[_normalize(raw_value)] = {raw_value}

    def add(self, raw_value: str, attributes: dict[str, str] | None = None):
        """Add to an existing item in the cache."""
        key = self.get_key(raw_value)
        if key is None:
            self._add_new_key(raw_value)
        else:
            self.data[key].add(raw_value)

        if attributes is not None:
            self.attributes[key] = attributes

    def get_key(self, input: str) -> str:
        """Get the normalized key for a given key."""
        normalized_input = _normalize(input)

        key = None
        if normalized_input not in self.data:
            score = process.extractOne(normalized_input, self.data.keys(), scorer=fuzz.ratio)
            if score and score[1] > 83:
                key = score[0]
        else:
            key = normalized_input

        return key

        return key

    def __len__(self):
        """Get the length of the data cache."""
        return len(self.data)

    def items(self):
        """Get the items in the data cache."""
        return self.data.items()

    def __getitem__(self, key: str):
        """Get the item from the data cache."""
        return self.data[self.get_key(key)]



def _normalize(text: str) -> str:
    """Normalize the text."""
    return text.lower().replace(".", "").strip()
