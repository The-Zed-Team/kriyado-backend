def get_nested_attr(obj, attr_path):
    """
    Get nested attribute using Django-style '__' notation.
    Example: 'default_branch__country__name'
    """
    try:
        for part in attr_path.split("__"):
            obj = getattr(obj, part)
    except AttributeError:
        return None
    return obj
