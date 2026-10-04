class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col

        self.walkable = True
        self.blocked = False

        self.is_castle = False
        self.is_spawn = False

        self.has_tower = False
        self.has_wall = False

        # A* data
        self.g_cost = float("inf")
        self.h_cost = 0
        self.f_cost = float("inf")
        self.parent = None

    def reset_path_data(self):
        self.g_cost = float("inf")
        self.h_cost = 0
        self.f_cost = float("inf")
        self.parent = None

    # ------------------------------------------------------------
    # STATIC MAP OBSTACLE
    # ------------------------------------------------------------

    def make_blocked(self):
        self.blocked = True
        self.walkable = False

        # Important:
        # Static obstacles are NOT player walls.
        self.has_wall = False

    # ------------------------------------------------------------
    # MAKE WALKABLE
    # ------------------------------------------------------------

    def make_walkable(self):
        self.blocked = False
        self.walkable = True
        self.has_wall = False

    # ------------------------------------------------------------
    # PLAYER BUILT WALL
    # ------------------------------------------------------------

    def place_wall(self):
        if self.is_castle or self.is_spawn:
            return False

        if self.blocked:
            return False

        self.blocked = True
        self.walkable = False
        self.has_wall = True

        return True

    # ------------------------------------------------------------
    # REMOVE PLAYER WALL
    # ------------------------------------------------------------

    def remove_wall(self):
        if not self.has_wall:
            return False

        self.blocked = False
        self.walkable = True
        self.has_wall = False

        return True

    def __repr__(self):
        return (
            f"Cell("
            f"row={self.row}, "
            f"col={self.col}, "
            f"walkable={self.walkable}, "
            f"blocked={self.blocked}, "
            f"has_wall={self.has_wall}"
            f")"
        )