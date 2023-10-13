def is_valid_field_name(name: str) -> bool:
    return not name.startswith("_")
