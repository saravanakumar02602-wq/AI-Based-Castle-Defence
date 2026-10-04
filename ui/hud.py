import pygame

from settings import HUD_HEIGHT, WINDOW_WIDTH


class HUD:
    TOWER_CARDS = (
        ("ARCHER", "Archer Tower", "Single rapid", 100, (61, 133, 255)),
        ("MAGE", "Shadow Mage", "Freeze Area", 175, (153, 117, 255)),
        ("CANNON", "Heavy Cannon", "High Burst", 250, (255, 94, 102)),
    )

    def __init__(self, game):
        self.game = game
        self.brand_font = pygame.font.SysFont("segoeui", 13, bold=True)
        self.section_font = pygame.font.SysFont("segoeui", 10, bold=True)
        self.stat_font = pygame.font.SysFont("segoeui", 19, bold=True)
        self.card_font = pygame.font.SysFont("segoeui", 16, bold=True)
        self.detail_font = pygame.font.SysFont("segoeui", 12, bold=True)
        self.hint_font = pygame.font.SysFont("segoeui", 11, bold=True)
        self.colors = {
            "background": (10, 16, 29),
            "panel": (20, 30, 48),
            "card": (28, 40, 59),
            "card_selected": (32, 74, 135),
            "border": (71, 88, 112),
            "text": (239, 242, 248),
            "muted": (166, 180, 198),
            "gold": (255, 190, 67),
            "blue": (76, 157, 255),
            "green": (47, 211, 155),
            "red": (255, 94, 95),
        }
        self.tower_card_rects = {
            "ARCHER": pygame.Rect(18, 67, 299, 68),
            "MAGE": pygame.Rect(333, 67, 299, 68),
            "CANNON": pygame.Rect(648, 67, 299, 68),
        }
        self.restart_rect = pygame.Rect(824, 22, 438, 32)
        self.wave_rect = pygame.Rect(612, 22, 198, 32)
        self.meteor_rect = pygame.Rect(963, 67, 299, 68)

    def draw(self, screen):
        screen.fill(self.colors["background"], (0, 0, WINDOW_WIDTH, HUD_HEIGHT))

        brand = self.brand_font.render(
            "A* PATHFINDING  ·  WAVE BONUSES  ·  METEOR STRIKE ACTIVE WEAPONS",
            True,
            self.colors["green"]
        )
        screen.blit(brand, brand.get_rect(midtop=(WINDOW_WIDTH // 2, 0)))

        pygame.draw.rect(
            screen,
            (7, 12, 23),
            pygame.Rect(12, 17, WINDOW_WIDTH - 24, 42),
            border_radius=13
        )
        pygame.draw.rect(
            screen,
            (58, 76, 101),
            pygame.Rect(12, 17, WINDOW_WIDTH - 24, 42),
            2,
            border_radius=13
        )

        self.draw_stat(screen, pygame.Rect(22, 22, 120, 32), "SCORE", f"{self.game.score:,}", self.colors["blue"])
        self.draw_stat(
            screen, pygame.Rect(150, 22, 142, 32), "GOLD",
            f"{self.game.resource_manager.get_gold()}",
            self.colors["gold"]
        )
        self.draw_stat(
            screen, pygame.Rect(300, 22, 104, 32), "WAVE",
            self.game.wave_manager.get_wave(),
            (236, 105, 192)
        )
        integrity = round(
            100 * self.game.castle.health / max(1, self.game.castle.max_health)
        )
        integrity_color = self.colors["green"] if integrity > 35 else self.colors["red"]
        self.draw_stat(
            screen, pygame.Rect(412, 22, 190, 32), "GATE INTEGRITY",
            f"{integrity}%", integrity_color
        )

        self.draw_restart(screen)
        self.draw_wave_control(screen)
        self.draw_tower_cards(screen)
        self.draw_meteor_control(screen)

    def draw_stat(self, screen, rect, label, value, value_color):
        pygame.draw.rect(screen, (8, 15, 27), rect.move(0, 2), border_radius=9)
        pygame.draw.rect(screen, (17, 29, 46), rect, border_radius=9)
        pygame.draw.rect(screen, (76, 91, 112), rect, 1, border_radius=9)
        pygame.draw.line(
            screen,
            value_color,
            (rect.x + 12, rect.bottom - 4),
            (rect.right - 12, rect.bottom - 4),
            2
        )
        label_surface = self.hint_font.render(label, True, self.colors["muted"])
        value_surface = self.stat_font.render(str(value), True, value_color)
        screen.blit(label_surface, (rect.x + 8, rect.centery - label_surface.get_height() // 2))
        screen.blit(
            value_surface,
            value_surface.get_rect(midright=(rect.right - 8, rect.centery))
        )

    def draw_restart(self, screen):
        hover = self.restart_rect.collidepoint(pygame.mouse.get_pos())
        fill = (89, 69, 39) if hover else (32, 43, 59)
        pygame.draw.rect(screen, fill, self.restart_rect, border_radius=9)
        pygame.draw.rect(
            screen, (82, 98, 122), self.restart_rect, 2, border_radius=9
        )
        label = self.card_font.render("Restart", True, self.colors["text"])
        screen.blit(label, label.get_rect(center=self.restart_rect.center))

    def draw_wave_control(self, screen):
        manager = self.game.wave_manager
        if manager.bonus_pending:
            detail = "WAVE REWARD READY"
            accent = (255, 196, 91)
        elif manager.started:
            detail = "ASSAULT IN PROGRESS"
            accent = (75, 208, 161)
        else:
            detail = "PREPARING DEFENCES"
            accent = (255, 196, 91)

        fill = (15, 27, 42)
        pygame.draw.rect(screen, fill, self.wave_rect, border_radius=9)
        pygame.draw.rect(
            screen, accent,
            self.wave_rect, 2, border_radius=9
        )
        detail_surface = self.hint_font.render(detail, True, accent)
        screen.blit(
            detail_surface,
            detail_surface.get_rect(center=self.wave_rect.center)
        )
        if not manager.started and not manager.bonus_pending:
            progress = 1 - (
                manager.preparation_remaining / manager.preparation_duration
            )
            track = pygame.Rect(
                self.wave_rect.x + 8,
                self.wave_rect.bottom - 2,
                self.wave_rect.width - 16,
                2
            )
            pygame.draw.rect(screen, (43, 58, 75), track, border_radius=2)
            fill_rect = track.copy()
            fill_rect.width = round(track.width * progress)
            pygame.draw.rect(screen, accent, fill_rect, border_radius=2)

    def draw_tower_cards(self, screen):
        for tower_type, title, subtitle, cost, accent in self.TOWER_CARDS:
            rect = self.tower_card_rects[tower_type]
            selected = self.game.selected_tower_type == tower_type
            hover = rect.collidepoint(pygame.mouse.get_pos())
            fill = self.colors["card_selected"] if selected else self.colors["card"]
            if hover and not selected:
                fill = (39, 54, 75)

            pygame.draw.rect(screen, (7, 13, 23), rect.move(0, 3), border_radius=12)
            pygame.draw.rect(screen, fill, rect, border_radius=12)
            pygame.draw.rect(
                screen,
                accent if selected else self.colors["border"],
                rect,
                2 if selected else 1,
                border_radius=12
            )
            if selected:
                glow_rect = rect.inflate(8, 8)
                pygame.draw.rect(
                    screen, (*accent, 38), glow_rect, 3, border_radius=14
                )

            icon_center = (rect.x + 26, rect.centery)
            self.draw_tower_icon(screen, tower_type, icon_center, accent)
            title_surface = self.card_font.render(title.upper(), True, self.colors["text"])
            detail_surface = self.detail_font.render(
                f"${cost} ({subtitle})",
                True,
                self.colors["gold"]
            )
            screen.blit(title_surface, (rect.x + 47, rect.y + 13))
            screen.blit(detail_surface, (rect.x + 47, rect.y + 39))

    def draw_meteor_control(self, screen):
        remaining = self.game.meteor_cooldown
        if self.game.meteor_targeting:
            title = "METEOR TARGETING"
            detail = "SELECT IMPACT POINT"
        elif remaining > 0:
            title = "METEOR STRIKE"
            detail = f"ACTIVE ABILITY · RECHARGING {remaining:.0f} SEC"
        else:
            title = "METEOR STRIKE"
            detail = "ACTIVE ABILITY (READY)"

        hover = self.meteor_rect.collidepoint(pygame.mouse.get_pos())
        fill = (157, 57, 16) if hover else (128, 49, 17)
        border = (255, 123, 45)
        if self.game.meteor_targeting:
            fill = (179, 70, 16)
            border = (255, 194, 97)
        pygame.draw.rect(screen, fill, self.meteor_rect, border_radius=12)
        pygame.draw.rect(screen, border, self.meteor_rect, 2, border_radius=12)
        title_surface = self.card_font.render(
            title, True, self.colors["text"]
        )
        detail_surface = self.detail_font.render(
            detail, True, (255, 221, 160)
        )
        meteor_center = (self.meteor_rect.x + 31, self.meteor_rect.centery)
        pygame.draw.circle(screen, (78, 33, 21), meteor_center, 19)
        pygame.draw.circle(screen, border, meteor_center, 19, 2)
        pygame.draw.circle(
            screen,
            (255, 219, 146),
            (meteor_center[0] - 2, meteor_center[1] + 3),
            7
        )
        pygame.draw.polygon(
            screen,
            (255, 112, 45),
            [
                (meteor_center[0] + 3, meteor_center[1] - 2),
                (meteor_center[0] + 15, meteor_center[1] - 13),
                (meteor_center[0] + 11, meteor_center[1] + 2),
            ]
        )
        pygame.draw.line(
            screen,
            (255, 192, 104),
            (meteor_center[0] - 7, meteor_center[1] - 8),
            (meteor_center[0] - 13, meteor_center[1] - 14),
            2
        )
        screen.blit(title_surface, title_surface.get_rect(center=(self.meteor_rect.centerx, self.meteor_rect.y + 17)))
        screen.blit(detail_surface, detail_surface.get_rect(center=(self.meteor_rect.centerx, self.meteor_rect.y + 39)))

    def draw_tower_icon(self, screen, tower_type, center, accent):
        pygame.draw.circle(screen, (15, 26, 43), center, 13)
        if tower_type == "ARCHER":
            pygame.draw.line(
                screen, accent,
                (center[0] - 6, center[1] + 6),
                (center[0] + 6, center[1] - 6), 3
            )
            pygame.draw.arc(
                screen, (226, 231, 244),
                pygame.Rect(center[0] - 7, center[1] - 8, 13, 17),
                -1.5, 1.5, 2
            )
        elif tower_type == "MAGE":
            pygame.draw.circle(screen, accent, center, 6)
            pygame.draw.circle(screen, (229, 212, 255), center, 3)
            pygame.draw.circle(screen, accent, center, 10, 1)
        else:
            points = [
                (center[0], center[1] - 9),
                (center[0] + 8, center[1] + 7),
                (center[0] - 8, center[1] + 7),
            ]
            pygame.draw.polygon(screen, accent, points)
            pygame.draw.circle(screen, (255, 223, 176), center, 3)

    def tower_card_at(self, position):
        for tower_type, rect in self.tower_card_rects.items():
            if rect.collidepoint(position):
                return tower_type
        return None

    def restart_at(self, position):
        return self.restart_rect.collidepoint(position)

    def meteor_at(self, position):
        return self.meteor_rect.collidepoint(position)
