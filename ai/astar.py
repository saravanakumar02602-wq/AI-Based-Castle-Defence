import heapq

from ai.heuristic import heuristic


class AStar:
    """
    Classical A* Search algorithm for enemy pathfinding.

    The algorithm finds a low-cost path from a start cell
    to a goal cell while avoiding blocked cells.
    """

    def __init__(self, grid):
        self.grid = grid

    def find_path(self, start, goal):
        """
        Find a path from start to goal.

        start and goal can be:
            (row, col)

        Returns:
            List of positions from start to goal.
            Returns [] if no path exists.
        """

        start_cell = self.grid.get_cell(
            start[0],
            start[1]
        )

        goal_cell = self.grid.get_cell(
            goal[0],
            goal[1]
        )

        if start_cell is None or goal_cell is None:
            return []

        if not start_cell.walkable:
            return []

        if not goal_cell.walkable:
            return []

        open_set = []

        heapq.heappush(
            open_set,
            (
                0,
                start
            )
        )

        came_from = {}

        g_score = {
            start: 0
        }

        f_score = {
            start: heuristic(
                start,
                goal
            )
        }

        while open_set:

            _, current = heapq.heappop(
                open_set
            )

            if current == goal:
                return self.reconstruct_path(
                    came_from,
                    current
                )

            current_cell = self.grid.get_cell(
                current[0],
                current[1]
            )

            neighbors = self.grid.get_neighbors(current_cell)
            if (
                goal_cell.has_tower
                and abs(current[0] - goal[0])
                + abs(current[1] - goal[1]) == 1
                and goal_cell not in neighbors
            ):
                neighbors.append(goal_cell)

            for neighbor_cell in neighbors:
                neighbor = (
                    neighbor_cell.row,
                    neighbor_cell.col
                )

                movement_cost = self.get_movement_cost(
                    neighbor_cell
                )

                tentative_g_score = (
                    g_score[current]
                    + movement_cost
                )

                if tentative_g_score < g_score.get(
                    neighbor,
                    float("inf")
                ):
                    came_from[neighbor] = current

                    g_score[neighbor] = (
                        tentative_g_score
                    )

                    f_score[neighbor] = (
                        tentative_g_score
                        + heuristic(
                            neighbor,
                            goal
                        )
                    )

                    heapq.heappush(
                        open_set,
                        (
                            f_score[neighbor],
                            neighbor
                        )
                    )

        return []

    def get_movement_cost(self, cell):
        """
        Cost of moving through a cell.

        Normal cells have a cost of 1.
        """

        if cell.blocked:
            return float("inf")

        return 1

    def reconstruct_path(
        self,
        came_from,
        current
    ):
        """
        Reconstruct the final path after A*
        reaches the goal.
        """

        path = [current]

        while current in came_from:
            current = came_from[current]
            path.append(current)

        path.reverse()

        return path


def find_path(grid, start, goal):
    """
    Convenience function for using A* without
    manually creating an AStar object.
    """

    astar = AStar(grid)

    return astar.find_path(
        start,
        goal
    )