def _normalize(text: str) -> str:
    """Normalize the text."""
    return text.lower().replace(".", "").replace("-", "").strip()


def is_same_postal_code(orginal_value: str, new_value: str) -> bool:
    """Check if two postal codes are the same.

    Two US postal codes (zip codes) are the same if:
    1) They are matching strings
    2) If one is digits long and the other starts with the same digits plus a hyphen and additional
    4 digits. We can assume they are the same
    """
    normalized_orginal = _normalize(orginal_value)
    normalized_new = _normalize(new_value)

    if normalized_orginal == normalized_new:
        return True

    orginal_first_5 = normalized_orginal[:5]
    new_first_5 = normalized_new[:5]
    if orginal_first_5 == new_first_5:
        return True
