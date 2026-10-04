def manhattan_distance(start, goal):
    """
    Manhattan distance for a 4-direction grid.

    This is the main heuristic used by A*.
    """

    row1, col1 = start
    row2, col2 = goal

    return abs(row1 - row2) + abs(col1 - col2)


def euclidean_distance(start, goal):
    """
    Euclidean distance between two grid positions.
    """

    row1, col1 = start
    row2, col2 = goal

    return (
        (row2 - row1) ** 2
        + (col2 - col1) ** 2
    ) ** 0.5


def heuristic(start, goal, method="manhattan"):
    """
    Select the heuristic method.
    """

    if method == "euclidean":
        return euclidean_distance(
            start,
            goal
        )

    return manhattan_distance(
        start,
        goal
    )