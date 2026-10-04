import pygame

from settings import (
    BATTLEFIELD_HEIGHT,
    BATTLEFIELD_LEFT,
    BATTLEFIELD_TOP,
    CASTLE_COLOR,
    CELL_SIZE,
    GRID_COLS,
    GRID_ROWS,
    WINDOW_WIDTH,
)


class Castle:
    """Castle keep and full-height gate wall on the right side."""

    def __init__(self, position, health=100):
        self.row = position[0]
        self.col = position[1]
        self.max_health = health
        self.health = health
        self.alive = True
        self.damage_flash = 0.0

    @property
    def position(self):
        return self.row, self.col

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        self.alive = self.health > 0
        self.damage_flash = 0.32

    def update(self, delta_time):
        self.damage_flash = max(0.0, self.damage_flash - delta_time)

    def draw(self, screen):
        wall_x = BATTLEFIELD_LEFT + GRID_COLS * CELL_SIZE
        wall_y = BATTLEFIELD_TOP
        wall_width = WINDOW_WIDTH - wall_x
        wall_height = min(
            BATTLEFIELD_HEIGHT,
            GRID_ROWS * CELL_SIZE
        )
        wall = pygame.Rect(wall_x, wall_y, wall_width, wall_height)
        flash = self.damage_flash > 0

        pygame.draw.rect(screen, (42, 49, 53), wall)
        pygame.draw.rect(screen, (128, 119, 97), wall, 3)

        parapet = pygame.Rect(wall_x + 5, wall_y + 12, wall_width - 10, 17)
        pygame.draw.rect(screen, (83, 87, 80), parapet)
        pygame.draw.line(
            screen, (174, 151, 111),
            (parapet.left, parapet.top),
            (parapet.right, parapet.top), 2
        )
        for merlon_x in range(parapet.left + 3, parapet.right - 12, 28):
            merlon = pygame.Rect(merlon_x, parapet.y - 7, 17, 12)
            pygame.draw.rect(screen, (105, 105, 91), merlon)
            pygame.draw.rect(screen, (174, 151, 111), merlon, 1)

        for row in range(0, wall_height, 34):
            offset = 0 if (row // 34) % 2 == 0 else 22
            pygame.draw.line(
                screen, (69, 74, 75),
                (wall_x + 2, wall_y + row),
                (wall.right - 2, wall_y + row), 1
            )
            for col in range(wall_x + 12 + offset, wall.right, 46):
                pygame.draw.line(
                    screen, (69, 74, 75),
                    (col, wall_y + row),
                    (col, min(wall.bottom, wall_y + row + 34)), 1
                )
                pygame.draw.line(
                    screen, (91, 93, 86),
                    (col + 2, wall_y + row + 2),
                    (min(wall.right - 2, col + 15), wall_y + row + 2), 1
                )

        inner_wall = wall.inflate(-12, -14)
        pygame.draw.rect(screen, (93, 99, 96), inner_wall, 2)
        pygame.draw.rect(
            screen, (55, 63, 66),
            pygame.Rect(wall_x + 8, wall_y + 22, 20, wall_height - 44)
        )

        keep_x = wall_x + wall_width // 2 - 72
        keep = pygame.Rect(
            keep_x + 12,
            wall_y + wall_height // 2 - 99,
            126,
            198
        )
        pygame.draw.rect(screen, (67, 70, 66), keep, border_radius=4)
        pygame.draw.rect(screen, (187, 157, 105), keep, 3, border_radius=4)
        pygame.draw.rect(
            screen, (91, 97, 91),
            pygame.Rect(keep.x + 9, keep.y + 27, keep.width - 18, keep.height - 36)
        )
        for offset in range(6, keep.width - 8, 21):
            pygame.draw.rect(
                screen, (194, 166, 116),
                pygame.Rect(keep.x + offset, keep.y - 10, 16, 22),
                border_radius=2
            )
        for window_y in (keep.y + 49, keep.y + 99, keep.y + 149):
            for window_x in (keep.x + 22, keep.x + 77):
                window = pygame.Rect(window_x, window_y, 23, 31)
                pygame.draw.rect(
                    screen, (35, 42, 44), window, border_radius=10
                )
                pygame.draw.rect(
                    screen, (187, 157, 105), window, 2, border_radius=10
                )
                pygame.draw.line(
                    screen, (187, 157, 105),
                    (window.centerx, window.y + 4),
                    (window.centerx, window.bottom - 3), 1
                )

        for tower_y in (wall_y + 25, wall.bottom - 91):
            tower = pygame.Rect(wall.right - 88, tower_y, 68, 76)
            pygame.draw.rect(screen, (86, 91, 88), tower, border_radius=10)
            pygame.draw.rect(
                screen, (194, 166, 116), tower, 2, border_radius=10
            )
            pygame.draw.rect(
                screen, (35, 42, 44),
                pygame.Rect(tower.x + 24, tower.y + 27, 20, 26),
                border_radius=10
            )
            for merlon_x in range(tower.x + 3, tower.right - 10, 19):
                pygame.draw.rect(
                    screen, (194, 166, 116),
                    pygame.Rect(merlon_x, tower.y - 6, 13, 12),
                    border_radius=2
                )

        gate_top = wall_y + wall_height // 2 - CELL_SIZE * 2
        gate = pygame.Rect(wall_x + 4, gate_top + CELL_SIZE // 2, 64, CELL_SIZE * 3)
        gate_color = (113, 43, 32) if flash else (65, 36, 27)
        pygame.draw.rect(screen, (190, 151, 91), gate.inflate(12, 12), border_radius=13)
        pygame.draw.rect(screen, gate_color, gate, border_radius=9)
        pygame.draw.rect(
            screen, (202, 159, 98) if not flash else (255, 103, 73),
            gate, 3, border_radius=9
        )
        for plank_x in range(gate.x + 11, gate.right - 5, 15):
            pygame.draw.line(
                screen, (148, 87, 49),
                (plank_x, gate.y + 8), (plank_x, gate.bottom - 8), 2
            )
        for bolt_y in range(gate.y + 15, gate.bottom - 8, 23):
            pygame.draw.circle(
                screen, (230, 191, 120),
                (gate.x + 7, bolt_y), 2
            )
            pygame.draw.circle(
                screen, (230, 191, 120),
                (gate.right - 7, bolt_y), 2
            )
        for band_y in (gate.y + 26, gate.centery, gate.bottom - 28):
            pygame.draw.line(
                screen, (86, 89, 87),
                (gate.x + 4, band_y),
                (gate.right - 4, band_y), 4
            )
            pygame.draw.line(
                screen, (198, 164, 106),
                (gate.x + 4, band_y - 1),
                (gate.right - 4, band_y - 1), 1
            )

        for lantern_y in (gate.y + 16, gate.bottom - 16):
            glow = pygame.Surface((48, 48), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 163, 64, 22), (24, 24), 23)
            pygame.draw.circle(glow, (255, 187, 92, 46), (24, 24), 12)
            screen.blit(glow, (wall_x + 86, lantern_y - 24))
            pygame.draw.rect(
                screen, (77, 55, 37),
                pygame.Rect(wall_x + 99, lantern_y - 10, 18, 21),
                border_radius=4
            )
            pygame.draw.rect(
                screen, (198, 130, 57),
                pygame.Rect(wall_x + 102, lantern_y - 7, 12, 14),
                border_radius=3
            )
            pygame.draw.circle(
                screen, (255, 207, 118),
                (wall_x + 108, lantern_y), 4
            )

        banner_x = wall_x + 115
        pygame.draw.line(
            screen, (220, 202, 161),
            (banner_x, wall_y + 75),
            (banner_x, wall_y + 37), 3
        )
        pygame.draw.polygon(
            screen, (167, 54, 48),
            [
                (banner_x + 2, wall_y + 39),
                (banner_x + 37, wall_y + 46),
                (banner_x + 2, wall_y + 57),
            ]
        )

        label = pygame.font.SysFont("segoeui", 14, bold=True).render(
            "THE KEEP", True, (234, 219, 181)
        )
        screen.blit(
            label,
            label.get_rect(center=(wall.right - 65, wall.bottom - 24))
        )

        bar = pygame.Rect(wall_x + 8, wall_y + 8, wall_width - 16, 7)
        pygame.draw.rect(screen, (24, 28, 34), bar, border_radius=4)
        health_bar = bar.copy()
        health_bar.width = round(
            bar.width * max(0, self.health / self.max_health)
        )
        health_color = (72, 202, 142) if not flash else (255, 93, 73)
        if self.health / self.max_health < 0.35:
            health_color = (232, 72, 66)
        pygame.draw.rect(screen, health_color, health_bar, border_radius=4)
