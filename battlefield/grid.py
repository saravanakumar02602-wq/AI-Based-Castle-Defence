import pygame

from settings import (
    GRID_ROWS,
    GRID_COLS,
    CELL_SIZE,
    BATTLEFIELD_TOP,
    BATTLEFIELD_LEFT,
    GRID_COLOR,
)

from .cell import Cell
from .map_data import (
    MAP_DATA,
    SPAWN_POINTS,
    CASTLE_POSITION,
    CASTLE_GATE_POSITIONS,
)


class Grid:
    def __init__(self):
        self.rows = GRID_ROWS
        self.cols = GRID_COLS

        self.cells = []

        self.spawn_points = []
        self.castle_position = CASTLE_POSITION
        self.castle_gate_positions = CASTLE_GATE_POSITIONS.copy()

        self.create_grid()
        self.load_map()

    # ---------------------------------------------------------
    # CREATE GRID
    # ---------------------------------------------------------

    def create_grid(self):

        for row in range(self.rows):

            row_cells = []

            for col in range(self.cols):

                row_cells.append(
                    Cell(row, col)
                )

            self.cells.append(row_cells)

    # ---------------------------------------------------------
    # LOAD MAP
    # ---------------------------------------------------------

    def load_map(self):

        for row in range(self.rows):

            for col in range(self.cols):

                value = MAP_DATA[row][col]

                cell = self.cells[row][col]

                if value == 0:

                    cell.make_walkable()

                elif value == 1:

                    cell.make_blocked()

                elif value == 2:

                    cell.make_walkable()

                    cell.is_spawn = True

                    self.spawn_points.append(
                        (row, col)
                    )

                elif value == 3:

                    cell.make_walkable()

                    cell.is_castle = True

        for row, col in self.castle_gate_positions:
            gate_cell = self.get_cell(row, col)
            gate_cell.make_walkable()
            gate_cell.is_castle = True

    # ---------------------------------------------------------
    # GET CELL
    # ---------------------------------------------------------

    def get_cell(self, row, col):

        if not self.is_inside(row, col):
            return None

        return self.cells[row][col]

    # ---------------------------------------------------------
    # CHECK POSITION
    # ---------------------------------------------------------

    def is_inside(self, row, col):

        return (
            0 <= row < self.rows
            and
            0 <= col < self.cols
        )

    # ---------------------------------------------------------
    # GET NEIGHBORS
    # ---------------------------------------------------------

    def get_neighbors(self, cell):

        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]

        neighbors = []

        for dr, dc in directions:

            nr = cell.row + dr
            nc = cell.col + dc

            if not self.is_inside(nr, nc):
                continue

            neighbor = self.get_cell(
                nr,
                nc
            )

            if neighbor.walkable and not neighbor.has_tower:

                neighbors.append(
                    neighbor
                )

        return neighbors

    # ---------------------------------------------------------
    # PLACE WALL
    # ---------------------------------------------------------

    def place_wall(self, row, col):

        cell = self.get_cell(
            row,
            col
        )

        if cell is None:
            return False

        # Cannot block castle
        if cell.is_castle:
            return False

        # Cannot block spawn
        if cell.is_spawn:
            return False

        # Already blocked
        if cell.blocked:
            return False

        # Cannot build on tower
        if cell.has_tower:
            return False

        # Cannot build on an enemy
        return_cell = self.is_enemy_on_cell(
            row,
            col
        )

        if return_cell:
            return False

        return cell.place_wall()

    # ---------------------------------------------------------
    # REMOVE WALL
    # ---------------------------------------------------------

    def remove_wall(self, row, col):

        cell = self.get_cell(
            row,
            col
        )

        if cell is None:
            return False

        return cell.remove_wall()

    # ---------------------------------------------------------
    # ENEMY CHECK
    # ---------------------------------------------------------

    def is_enemy_on_cell(self, row, col):

        # This method is intentionally kept simple.
        # Game-level enemy checking is handled by Game/TowerManager.

        return False

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------

    def draw(self, screen):

        for row in range(self.rows):

            for col in range(self.cols):

                cell = self.cells[row][col]

                x = BATTLEFIELD_LEFT + col * CELL_SIZE

                y = (
                    BATTLEFIELD_TOP
                    + row * CELL_SIZE
                )

                rect = pygame.Rect(
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                )

                if cell.blocked and cell.has_wall:
                    pygame.draw.rect(screen, (56, 48, 41), rect)
                    inset = rect.inflate(-8, -8)
                    pygame.draw.rect(
                        screen, (132, 100, 67), inset, border_radius=5
                    )
                    pygame.draw.rect(
                        screen, (203, 161, 101), inset, 2, border_radius=5
                    )
                    for brick_y in (y + 22, y + 42):
                        pygame.draw.line(
                            screen, (91, 70, 50),
                            (x + 6, brick_y), (x + CELL_SIZE - 6, brick_y), 2
                        )
                    pygame.draw.line(
                        screen, (91, 70, 50),
                        (x + CELL_SIZE // 2, y + 8),
                        (x + CELL_SIZE // 2, y + 22), 2
                    )
                    pygame.draw.line(
                        screen, (91, 70, 50),
                        (x + CELL_SIZE // 3, y + 23),
                        (x + CELL_SIZE // 3, y + 42), 2
                    )
                elif cell.blocked:
                    pygame.draw.rect(screen, (47, 57, 66), rect)
                    inset = rect.inflate(-7, -7)
                    pygame.draw.rect(
                        screen, (82, 98, 107), inset
                    )
                    pygame.draw.rect(
                        screen, (132, 151, 153), inset, 2
                    )
                    pygame.draw.line(
                        screen, (61, 77, 81),
                        (x + 15, y + 18), (x + 30, y + 29), 2
                    )
                    pygame.draw.line(
                        screen, (61, 77, 81),
                        (x + 30, y + 29), (x + 38, y + 17), 2
                    )
                else:
                    grass = (
                        (49, 91, 55)
                        if (row + col) % 2 == 0
                        else (44, 83, 51)
                    )
                    pygame.draw.rect(screen, grass, rect)
                    if (row * 7 + col * 11) % 5 == 0:
                        pygame.draw.line(
                            screen, (82, 126, 69),
                            (x + 14, y + 48), (x + 19, y + 43), 1
                        )
                        pygame.draw.line(
                            screen, (82, 126, 69),
                            (x + 19, y + 43), (x + 22, y + 49), 1
                        )
                    elif (row * 13 + col * 5) % 11 == 0:
                        pebble_x = x + 8 + (row * 3 + col * 7) % 23
                        pebble_y = y + 10 + (row * 5 + col * 2) % 21
                        pygame.draw.ellipse(
                            screen,
                            (71, 83, 62),
                            pygame.Rect(pebble_x, pebble_y, 5, 3)
                        )

                if cell.is_castle:
                    pygame.draw.rect(screen, (81, 65, 48), rect)
                    pygame.draw.rect(
                        screen, (201, 155, 82),
                        rect.inflate(-5, -5), 2, border_radius=3
                    )
                    pygame.draw.line(
                        screen, (235, 190, 112),
                        (rect.left + 7, rect.top + 7),
                        (rect.right - 7, rect.top + 7), 2
                    )

                if cell.is_spawn:
                    pygame.draw.rect(screen, (35, 76, 68), rect)
                    center = rect.center
                    pygame.draw.circle(screen, (68, 151, 119), center, 22, 2)
                    pygame.draw.circle(screen, (139, 224, 173), center, 13, 2)
                    pygame.draw.circle(screen, (30, 50, 46), center, 8)
                    pygame.draw.circle(screen, (255, 137, 83), center, 4)

                pygame.draw.rect(
                    screen,
                    (31, 57, 39),
                    rect,
                    1
                )

        battlefield = pygame.Rect(
            BATTLEFIELD_LEFT,
            BATTLEFIELD_TOP,
            self.cols * CELL_SIZE,
            self.rows * CELL_SIZE
        )
        pygame.draw.rect(screen, (178, 144, 91), battlefield, 2)