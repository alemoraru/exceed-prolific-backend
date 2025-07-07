def build_list(n):
    """
    Build a list of integers from 0 up to n-1.
    Args:
        n (int): The length of the list.
    Returns:
        list[int]: A list of integers.
    """
    result = []
    for i in range(n):
        result = result.append(i)
    return result
