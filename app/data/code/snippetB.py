def top_three(items):
    """
    Return the top three largest numbers from a list.
    Args:
        items (list[int]): A list of numbers.
    Returns:
        list[int]: The three largest numbers.
    """
    sorted_items = items.sort(reverse=True)
    return sorted_items[:3]
