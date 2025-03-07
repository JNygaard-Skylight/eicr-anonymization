"""Get random Star Wars themed data."""

from random import choice, randint

import yaml

_family_name_list_file = "src/random_sw/data/family_names.yaml"

with open(_family_name_list_file) as f:
    _family_names = yaml.safe_load(f)

_given_name_list_file = "src/random_sw/data/given_names.yaml"

with open(_given_name_list_file) as f:
    _given_names = yaml.safe_load(f)

_name_prefix_list_file = "src/random_sw/data/name_prefixes.yaml"

with open(_name_prefix_list_file) as f:
    _name_prefixes = yaml.safe_load(f)

_name_suffix_list_file = "src/random_sw/data/name_suffixes.yaml"

with open(_name_suffix_list_file) as f:
    _name_suffixes = yaml.safe_load(f)

_street_name_list_file = "src/random_sw/data/street_names.yaml"

with open(_street_name_list_file) as f:
    _street_names = yaml.safe_load(f)

_street_type_list_file = "src/random_sw/data/street_types.yaml"

with open(_street_type_list_file) as f:
    _street_types = yaml.safe_load(f)


def get_random_family_name():
    """Get a random Star Wars themed family name."""
    return choice(_family_names)

def get_random_given_name():
    """Get a random Star Wars themed given name."""
    return choice(_given_names)

def get_random_name_prefix():
    """Get a random Star Wars themed name prefix."""
    return choice(_name_prefixes)


def get_random_name_suffix():
    """Get a random Star Wars themed name suffix."""
    return choice(_name_suffixes)


def get_random_street_address():
    """Get a random Star Wars themed street address."""
    return f"{randint(1, 9999)} {choice(_street_names)} {choice(_street_types)}"
