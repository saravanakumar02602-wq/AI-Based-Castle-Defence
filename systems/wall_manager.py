class WallManager:
    """
    Manages player-created defensive walls.

    Walls are represented as blocked cells in the battlefield.
    When a wall is placed, the AI Commander can detect the
    changed battlefield and A* can calculate a new route.
    """

    def __init__(self, game):
        self.game = game

        # Cost for one wall
        self.wall_cost = 50

    # ---------------------------------------------------------
    # PLACE WALL
    # ---------------------------------------------------------

    def place_wall(self, row, col):
        """
        Attempt to place a wall at the selected grid cell.
        """

        cell = self.game.grid.get_cell(row, col)

        if cell is None:
            return False

        # Cannot build on castle
        if cell.is_castle:
            return False

        # Cannot build on spawn point
        if cell.is_spawn:
            return False

        # Cannot build on existing obstacle
        if cell.blocked:
            return False

        # Cannot build on a tower
        if cell.has_tower:
            return False

        # Cannot build directly on an enemy
        if self.is_enemy_on_cell(row, col):
            return False

        # Check gold
        if not self.game.resource_manager.can_afford(
            self.wall_cost
        ):
            return False

        if not cell.place_wall():
            return False

        astar = self.game.commander.astar
        astar.grid = self.game.grid
        routes_remain = any(
            astar.find_path(spawn, self.game.castle.position)
            for spawn in self.game.grid.spawn_points
        )
        enemy_routes_remain = all(
            astar.find_path(enemy.position, self.game.castle.position)
            for enemy in self.game.enemies
            if enemy.alive and enemy.state == "ADVANCING"
        )
        cell.remove_wall()

        if not routes_remain or not enemy_routes_remain:
            return False

        # Spend gold
        if not self.game.resource_manager.spend_gold(
            self.wall_cost
        ):
            return False

        if not cell.place_wall():
            self.game.resource_manager.add_gold(self.wall_cost)
            return False

        print(
            f"Wall placed at ({row}, {col})"
        )

        return True

    # ---------------------------------------------------------
    # REMOVE WALL
    # ---------------------------------------------------------

    def remove_wall(self, row, col):
        """
        Remove a player-created wall.
        """

        cell = self.game.grid.get_cell(row, col)

        if cell is None:
            return False

        if not cell.has_wall:
            return False

        if cell.remove_wall():

            # Give back half the wall cost
            refund = self.wall_cost // 2

            self.game.resource_manager.add_gold(
                refund
            )

            print(
                f"Wall removed at ({row}, {col})"
            )

            return True

        return False

    # ---------------------------------------------------------
    # ENEMY CHECK
    # ---------------------------------------------------------

    def is_enemy_on_cell(self, row, col):

        for enemy in self.game.enemies:

            if not enemy.alive:
                continue

            if enemy.position == (row, col):
                return True

        return False

    # ---------------------------------------------------------
    # CAN PLACE WALL
    # ---------------------------------------------------------

    def can_place_wall(self, row, col):

        cell = self.game.grid.get_cell(row, col)

        if cell is None:
            return False

        if cell.is_castle:
            return False

        if cell.is_spawn:
            return False

        if cell.blocked:
            return False

        if cell.has_tower:
            return False

        if self.is_enemy_on_cell(row, col):
            return False

        if not self.game.resource_manager.can_afford(
            self.wall_cost
        ):
            return False

        return True

    # ---------------------------------------------------------
    # GET WALL COUNT
    # ---------------------------------------------------------

    def get_wall_count(self):

        count = 0

        for row in range(self.game.grid.rows):

            for col in range(self.game.grid.cols):

                cell = self.game.grid.get_cell(
                    row,
                    col
                )

                if cell.has_wall:
                    count += 1

        return count

    # ---------------------------------------------------------
    # GET WALL POSITIONS
    # ---------------------------------------------------------

    def get_wall_positions(self):

        positions = []

        for row in range(self.game.grid.rows):

            for col in range(self.game.grid.cols):

                cell = self.game.grid.get_cell(
                    row,
                    col
                )

                if cell.has_wall:

                    positions.append(
                        (row, col)
                    )

        return positions