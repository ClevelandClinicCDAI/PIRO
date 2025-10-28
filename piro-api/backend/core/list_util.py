def split_list_group(lst: list, group_size: int) -> list[list]:
    """Break up a list into groups (sub-lists) of a specific group size."""

    total_len: int = len(lst)
    return [lst[i : i + group_size] for i in range(0, total_len, group_size)]  # NOQA:E203
