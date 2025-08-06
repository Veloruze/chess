def _parse_config_value(value_str):
    """
    Parses a config string that might contain a comment (e.g., 'value ; comment').
    Returns the value before the first semicolon or hash, stripped of whitespace.
    """
    if ';' in value_str:
        value_str = value_str.split(';')[0]
    if '#' in value_str:
        value_str = value_str.split('#')[0]
    return value_str.strip()