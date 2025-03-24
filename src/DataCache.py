"""Data Cache Module."""

from tags.Tag import Tag


class NormalizedTagGroup:
    """A simple data cache class."""

    def __init__(self, tag: Tag):
        """Initialize the data cache."""
        self._group: set[Tag] = {tag}
        self._type = tag.__class__
        self._normalized_tag = tag.__class__(text=tag.normalized_text, attributes=tag.attributes)
        self._replace_mapping = None

    def __len__(self):
        """Return the number of items in the cache."""
        return len(self._group)

    def __iter__(self):
        """Iterate over the cache."""
        yield from self._group

    @property
    def type(self):
        """Return the type of the tag."""
        return self._type

    def add(self, tag: Tag):
        """Add a tag to the cache."""
        if tag.__class__ == self._type:
            self._group.add(tag)
        else:
            raise TypeError(f"Tag type {tag.__class__} does not match group type {self._type}.")

    def get_replacement_mapping(self):
        """Get the replacement mapping for the group."""
        return self._type.get_replacement_mapping(self._normalized_tag, self._group)


class NormalizedTagGroups:
    """A simple data cache class."""

    def __init__(self):
        """Initialize the data cache."""
        self._groups: dict[int, set[Tag]] = {}

    def __len__(self):
        """Return the number of items in the cache."""
        return len(self._groups)

    def add(self, tag: Tag):
        """Add a tag to the cache."""
        tag_hash = tag.normalized_hash
        if tag_hash not in self._groups:
            self._groups[tag_hash] = NormalizedTagGroup(tag)
        self._groups[tag_hash].add(tag)

    def __iter__(self):
        """Iterate over the cache."""
        yield from self._groups.values()
