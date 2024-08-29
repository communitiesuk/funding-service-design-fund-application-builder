from dataclasses import asdict
from dataclasses import is_dataclass


def convert_to_dict(obj):
    if is_dataclass(obj):
        return asdict(obj)
    elif isinstance(obj, list):
        return [asdict(item) if is_dataclass(item) else item for item in obj]
    else:
        return obj


def find_enum(enum_class, value):
    for enum in enum_class:
        if enum.value == value:
            return enum
    return None
