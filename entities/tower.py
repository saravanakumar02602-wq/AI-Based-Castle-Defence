import pygame

from settings import (
    CELL_SIZE,
    BATTLEFIELD_TOP,
    BATTLEFIELD_LEFT,
    TOWER_COLOR,
)


class Tower:

    def __init__(
        self,
        position,
        damage=20,
        attack_range=3,
        tower_type="ARCHER"
    ):
        self.row = position[0]
        self.col = position[1]

        self.level = 1

        self.damage = damage
        self.attack_range = attack_range
        self.tower_type = tower_type
        self.attack_cooldown = {
            "ARCHER": 1,
            "MAGE": 3,
            "CANNON": 4,
        }.get(tower_type, 2)

        self.cooldown = 0

        self.upgrade_cost = 150
        self.max_level = 3

    @property
    def position(self):
        return self.row, self.col

    # --------------------------------------------------
    # UPGRADE
    # --------------------------------------------------

    def can_upgrade(self):
        return self.level < self.max_level

    def upgrade(self):

        if not self.can_upgrade():
            return False

        self.level += 1

        # Stronger attack.
        self.damage += 15

        # Larger attack range.
        self.attack_range += 1

        # Reset attack cooldown.
        self.cooldown = 0

        # Make future upgrades progressively more expensive.
        self.upgrade_cost += 100

        return True

    # --------------------------------------------------
    # COMBAT
    # --------------------------------------------------

    def is_enemy_in_range(self, enemy_position):

        enemy_row, enemy_col = enemy_position

        distance = (
            abs(self.row - enemy_row)
            + abs(self.col - enemy_col)
        )

        return distance <= self.attack_range

    # --------------------------------------------------
    # DRAW
    # --------------------------------------------------

    def draw_range(self, screen):
        x = BATTLEFIELD_LEFT + self.col * CELL_SIZE + CELL_SIZE // 2
        y = BATTLEFIELD_TOP + self.row * CELL_SIZE + CELL_SIZE // 2
        radius = self.attack_range * CELL_SIZE
        vertices = [
            (x, y - radius),
            (x + radius, y),
            (x, y + radius),
            (x - radius, y),
        ]
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(
            overlay,
            (57, 133, 255, 13),
            vertices
        )
        pygame.draw.polygon(
            overlay,
            (86, 154, 255, 42),
            vertices,
            1
        )
        screen.blit(overlay, (0, 0))

    def draw(self, screen, target_position=None):

        x = BATTLEFIELD_LEFT + self.col * CELL_SIZE

        y = (
            BATTLEFIELD_TOP
            + self.row * CELL_SIZE
        )

        if self.tower_type == "ARCHER":
            self.draw_archer(screen, x, y, target_position)
        elif self.tower_type == "MAGE":
            self.draw_mage(screen, x, y, target_position)
        else:
            self.draw_cannon(screen, x, y, target_position)

        level_font = pygame.font.SysFont("segoeui", 10, bold=True)
        level_text = level_font.render(
            f"L{self.level}",
            True,
            (248, 250, 255)
        )
        screen.blit(level_text, (x + 4, y + 4))

    def draw_archer(self, screen, x, y, target_position=None):
        tower_rect = pygame.Rect(x + 10, y + 14, CELL_SIZE - 20, CELL_SIZE - 24)
        pygame.draw.ellipse(
            screen, (24, 38, 42),
            pygame.Rect(x + 8, y + 42, CELL_SIZE - 16, 15)
        )
        pygame.draw.rect(
            screen, (34, 56, 67), tower_rect.inflate(4, 4), border_radius=9
        )
        pygame.draw.rect(
            screen, TOWER_COLOR, tower_rect, border_radius=7
        )
        pygame.draw.rect(
            screen, (143, 196, 224), tower_rect, 2, border_radius=7
        )

        center = (
            x + CELL_SIZE // 2,
            y + CELL_SIZE // 2
        )

        pygame.draw.circle(screen, (31, 52, 63), center, 13)
        pygame.draw.circle(screen, (198, 208, 205), center, 8)
        pygame.draw.circle(screen, (110, 181, 216), center, 4)
        self.draw_aiming_barrel(screen, center, target_position, (225, 231, 218), 3)

    def draw_mage(self, screen, x, y, target_position=None):
        center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        pygame.draw.circle(screen, (59, 43, 101), center, 19)
        pygame.draw.circle(screen, (144, 104, 236), center, 15, 3)
        pygame.draw.circle(screen, (211, 191, 255), center, 8)
        pygame.draw.circle(screen, (255, 244, 205), center, 3)
        if target_position is not None:
            self.draw_aiming_barrel(
                screen, center, target_position, (204, 175, 255), 2
            )
        for dx, dy in ((0, -22), (19, 10), (-19, 10)):
            pygame.draw.circle(
                screen, (190, 163, 255), (center[0] + dx, center[1] + dy), 2
            )

    def draw_cannon(self, screen, x, y, target_position=None):
        center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        base = pygame.Rect(x + 10, y + 16, CELL_SIZE - 20, CELL_SIZE - 25)
        pygame.draw.rect(screen, (74, 43, 43), base, border_radius=8)
        pygame.draw.rect(screen, (203, 83, 89), base, 2, border_radius=8)
        pygame.draw.circle(screen, (61, 68, 81), center, 12)
        pygame.draw.circle(screen, (177, 190, 205), center, 8)
        pygame.draw.circle(screen, (48, 57, 70), center, 4)
        self.draw_aiming_barrel(screen, center, target_position, (216, 223, 230), 7)

    def draw_aiming_barrel(
        self,
        screen,
        center,
        target_position,
        color,
        width
    ):
        if target_position is None:
            direction = pygame.Vector2(1, -1).normalize()
        else:
            target_row, target_col = target_position
            direction = pygame.Vector2(
                target_col - self.col,
                target_row - self.row
            )
            if direction.length_squared() == 0:
                direction = pygame.Vector2(1, -1).normalize()
            else:
                direction = direction.normalize()

        tip = (
            round(center[0] + direction.x * 14),
            round(center[1] + direction.y * 14)
        )
        pygame.draw.line(screen, (39, 45, 51), center, tip, width + 3)
        pygame.draw.line(screen, color, center, tip, width)
        pygame.draw.circle(screen, (31, 38, 44), tip, max(2, width // 2 + 1))

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    def get_status(self):

        return {
            "position": self.position,
            "tower_type": self.tower_type,
            "level": self.level,
            "damage": self.damage,
            "attack_range": self.attack_range,
            "upgrade_cost": self.upgrade_cost,
            "max_level": self.max_level,
        }