def parse_numbers(data):
    """
    Parse comma-separated numbers into a list of ints.
    Args:
        data (str): A comma-separated string of numbers.
    Returns:
        list[int]: List of integers.
    """
    return [int(x) for x in data.split(',')]
