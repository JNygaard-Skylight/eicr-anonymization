"""Data Cache Module."""

from rapidfuzz import fuzz, process


class DataCache:
    """A simple data cache class."""

    def __init__(self):
        """Initialize the data cache."""
        self.data = {}

    def get(self, key: str):
        """Get the data from the cache.

        To get the data from the cache:
        1) Normalize the key.
        2) Check if the normalized key is in the data dictionary.
        2) If not, check using rapidfuzz.
        3) If a match is found, return the data.
        """
        if len(self.data) == 0:
            return None
        leading, trailing = extract_whitespace_edges(key)
        is_upper = key.isupper()
        is_lower = key.islower()

        key = _normalize(key)
        if key in self.data:
            if is_upper:
                return leading + self.data[key]["normized_replacement"].upper() + trailing
            if is_lower:
                return leading + self.data[key]["normized_replacement"].lower() + trailing
            else:
                return leading + self.data[key]["normized_replacement"] + trailing

        score = process.extractOne(key, self.data.keys(), scorer=fuzz.ratio)
        if score[1] > 90:
            if is_upper:
                return leading + self.data[score[0]]["normized_replacement"].upper() + trailing
            if is_lower:
                return leading + self.data[score[0]]["normized_replacement"].lower() + trailing
            else:
                return leading + self.data[score[0]]["normized_replacement"] + trailing
        else:
            return None

    def set_new(self, key: str, base_replacement_value: str):
        """Add a new item to the cache."""
        self.data[_normalize(key)] = {
            "normized_replacement": base_replacement_value,
            "replacements": [],
        }
        leading, trailing = extract_whitespace_edges(key)
        if key.isupper():
            return leading + base_replacement_value.upper() + trailing
        if key.islower():
            return leading + base_replacement_value.lower() + trailing
        return leading + base_replacement_value + trailing

    def set(self, key: str, replacement_value: str):
        """Add to an existing item in the cache."""
        normalized_key = _normalize(key)
        if normalized_key not in self.data:
            score = process.extractOne(normalized_key, self.data.keys(), scorer=fuzz.ratio)
            if score[1] > 90:
                normalized_key = score[0]
            else:
                raise ValueError(f"Key {normalized_key} not found in cache.")
        self.data[normalized_key]["replacements"].append((key, replacement_value))

    def contains(self, key: str) -> bool:
        """Check if the data is in the cache."""
        key = _normalize(key)
        if key in self.data:
            return True

        score = process.extractOne(key, self.data.keys(), scorer=fuzz.ratio)
        return score[1] > 90

    def __len__(self):
        """Return the length of the data cache."""
        return len(self.data)

    def items(self):
        """Return an iterator over the data cache."""
        return self.data.items()


def _normalize(text: str) -> str:
    """Normalize the text."""
    return text.lower().replace(".", "").strip()


def extract_whitespace_edges(key):
    """Extract whitespace edges from a string."""
    leading = key[: len(key) - len(key.lstrip())]
    trailing = key[len(key.rstrip()) :]
    return leading, trailing
