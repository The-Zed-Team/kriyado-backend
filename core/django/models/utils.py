# def get_nested_attr(obj, attr_path):
#     """
#     Get nested attribute using Django-style '__' notation.
#     Example: 'default_branch__country__name'
#     """
#     try:
#         for part in attr_path.split("__"):
#             obj = getattr(obj, part)
#     except AttributeError:
#         return None
#     return obj
def get_nested_attr(obj, attr_path):
    """
    Safely get nested attributes using Django-style '__' notation.
    Example: 'default_branch__profile__registered_address'

    Returns:
      - The attribute value if present.
      - None if any part of the path is missing or the final value is empty/None.
      - Boolean False and 0 are preserved.
    """
    try:
        for part in attr_path.split("__"):
            if obj is None:
                return None
            obj = getattr(obj, part, None)

        # Final value check
        if obj is None:
            return None

        if isinstance(obj, str) and not obj.strip():
            return None

        return obj

    except AttributeError:
        return None
