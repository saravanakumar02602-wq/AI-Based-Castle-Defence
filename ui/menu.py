import pygame

from settings import HUD_HEIGHT


class Menu:
    """
    Main menu and end-game menu.

    Provides:
        - Start Game
        - Instructions
        - AI Techniques
        - Restart
        - Quit
    """

    MAIN_MENU = "MAIN_MENU"
    INSTRUCTIONS = "INSTRUCTIONS"
    PLAYING = "PLAYING"
    END_SCREEN = "END_SCREEN"

    def __init__(self, game):

        self.game = game

        self.screen_state = self.MAIN_MENU
        self._backdrop_surface = None
        self._fortress_glow = None

        # --------------------------------------------------------
        # Fonts
        # --------------------------------------------------------

        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 30)
        self.button_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

        # --------------------------------------------------------
        # Colours
        # --------------------------------------------------------

        self.background_color = (10, 14, 22)
        self.panel_color = (25, 30, 40)
        self.button_color = (55, 70, 90)
        self.button_hover_color = (75, 95, 120)

        self.border_color = (110, 120, 135)

        self.text_color = (240, 240, 240)
        self.secondary_color = (180, 190, 205)

        # --------------------------------------------------------
        # Buttons
        # --------------------------------------------------------

        self.start_rect = pygame.Rect(
            490, 330, 300, 55
        )

        self.instructions_rect = pygame.Rect(
            490, 400, 300, 55
        )

        self.quit_rect = pygame.Rect(
            490, 470, 300, 55
        )

        self.back_rect = pygame.Rect(
            490, 610, 300, 50
        )

        self.restart_rect = pygame.Rect(
            490, 450, 300, 52
        )

        self.end_quit_rect = pygame.Rect(
            490, 516, 300, 52
        )

    # ============================================================
    # BUTTON
    # ============================================================

    def draw_button(
        self,
        screen,
        rect,
        text
    ):

        mouse_position = pygame.mouse.get_pos()

        if rect.collidepoint(mouse_position):

            color = self.button_hover_color

        else:

            color = self.button_color

        shadow = rect.move(0, 5)
        pygame.draw.rect(
            screen,
            (5, 9, 15),
            shadow,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            color,
            rect,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            (155, 178, 187) if rect.collidepoint(mouse_position) else self.border_color,
            rect,
            1,
            border_radius=10
        )

        surface = self.button_font.render(
            text,
            True,
            self.text_color
        )

        text_rect = surface.get_rect(
            center=rect.center
        )

        screen.blit(
            surface,
            text_rect
        )

    def draw_backdrop(self, screen):
        if (
            self._backdrop_surface is not None
            and self._backdrop_surface.get_size() == screen.get_size()
        ):
            screen.blit(self._backdrop_surface, (0, 0))
            return

        top = (12, 21, 33)
        bottom = (26, 47, 54)
        surface = pygame.Surface(screen.get_size())
        height = surface.get_height()

        for y in range(height):
            blend = y / max(1, height - 1)
            color = tuple(
                round(top[index] * (1 - blend) + bottom[index] * blend)
                for index in range(3)
            )
            pygame.draw.line(
                surface, color, (0, y), (surface.get_width(), y)
            )

        pygame.draw.polygon(
            surface,
            (20, 39, 43),
            [(0, 540), (210, 430), (420, 535), (680, 405),
             (930, 530), (1120, 420), (1280, 505), (1280, 720), (0, 720)]
        )
        pygame.draw.polygon(
            surface,
            (15, 31, 38),
            [(0, 620), (260, 520), (500, 615), (780, 490),
             (1030, 610), (1280, 520), (1280, 720), (0, 720)]
        )

        for index in range(36):
            x = (index * 173 + 41) % surface.get_width()
            y = (index * 97 + 29) % 360
            radius = 1 + (index % 3 == 0)
            pygame.draw.circle(
                surface,
                (115, 153, 159),
                (x, y),
                radius
            )

        self._backdrop_surface = surface
        screen.blit(surface, (0, 0))

    def draw_fortress(self, screen, center=(1000, 490), scale=1.0):
        cx, cy = center
        if (
            self._fortress_glow is None
            or self._fortress_glow.get_size() != screen.get_size()
        ):
            self._fortress_glow = pygame.Surface(
                screen.get_size(),
                pygame.SRCALPHA
            )
            for radius in range(190, 30, -20):
                alpha = max(3, 22 - radius // 12)
                pygame.draw.circle(
                    self._fortress_glow,
                    (207, 154, 82, alpha),
                    center,
                    int(radius * scale)
                )
        screen.blit(self._fortress_glow, (0, 0))

        base = pygame.Rect(
            cx - int(145 * scale),
            cy - int(52 * scale),
            int(290 * scale),
            int(130 * scale)
        )
        pygame.draw.rect(screen, (46, 52, 53), base, border_radius=6)
        pygame.draw.rect(screen, (130, 119, 94), base, 3, border_radius=6)

        for tower_x, tower_width, tower_height in (
            (cx - 124, 56, 152),
            (cx - 32, 64, 205),
            (cx + 68, 56, 152),
        ):
            tower = pygame.Rect(
                tower_x,
                cy - tower_height + 13,
                tower_width,
                tower_height
            )
            pygame.draw.rect(screen, (72, 77, 72), tower, border_radius=4)
            pygame.draw.rect(screen, (160, 143, 107), tower, 2, border_radius=4)
            for merlon in range(3):
                x = tower.x + 5 + merlon * (tower.width - 14) // 2
                pygame.draw.rect(
                    screen, (163, 145, 105),
                    pygame.Rect(x, tower.y - 9, 10, 13), border_radius=2
                )
            window = pygame.Rect(
                tower.centerx - 5, tower.y + 35, 10, 21
            )
            pygame.draw.rect(screen, (222, 172, 91), window, border_radius=5)

        gate = pygame.Rect(cx - 20, cy + 5, 40, 72)
        pygame.draw.rect(screen, (31, 34, 34), gate, border_radius=20)
        pygame.draw.line(
            screen, (190, 158, 103),
            (cx, cy + 8), (cx, cy + 73), 2
        )
        pygame.draw.line(
            screen, (190, 158, 103),
            (cx - 16, cy + 42), (cx + 16, cy + 42), 2
        )
        pygame.draw.line(
            screen, (205, 194, 157),
            (cx + 32, cy - 200), (cx + 32, cy - 245), 2
        )
        pygame.draw.polygon(
            screen, (166, 64, 57),
            [(cx + 34, cy - 244), (cx + 80, cy - 231), (cx + 34, cy - 218)]
        )

    # ============================================================
    # TITLE
    # ============================================================

    def draw_title(self, screen):

        title = self.title_font.render(
            "AI CASTLE DEFENCE",
            True,
            self.text_color
        )

        title_rect = title.get_rect(
            center=(640, 130)
        )

        screen.blit(
            title,
            title_rect
        )

        subtitle = self.subtitle_font.render(
            "A Strategic Tower Defence Experience",
            True,
            self.secondary_color
        )

        subtitle_rect = subtitle.get_rect(
            center=(640, 185)
        )

        screen.blit(
            subtitle,
            subtitle_rect
        )

    # ============================================================
    # MAIN MENU
    # ============================================================

    def draw_main_menu(self, screen):

        self.draw_backdrop(screen)
        self.draw_fortress(screen)

        self.draw_title(screen)

        self.draw_button(
            screen,
            self.start_rect,
            "START GAME"
        )

        self.draw_button(
            screen,
            self.instructions_rect,
            "INSTRUCTIONS"
        )

        self.draw_button(
            screen,
            self.quit_rect,
            "QUIT"
        )

        footer = self.small_font.render(
            "FORTIFY YOUR DEFENCES  ·  ADAPT YOUR STRATEGY  ·  PROTECT THE REALM",
            True,
            self.secondary_color
        )

        footer_rect = footer.get_rect(
            center=(640, 650)
        )

        screen.blit(
            footer,
            footer_rect
        )

    # ============================================================
    # INSTRUCTIONS
    # ============================================================

    def draw_instructions(self, screen):

        self.draw_backdrop(screen)

        title = self.title_font.render(
            "HOW TO PLAY",
            True,
            self.text_color
        )

        title_rect = title.get_rect(
            center=(640, 70)
        )

        screen.blit(
            title,
            title_rect
        )

        panel = pygame.Rect(
            180,
            115,
            920,
            470
        )

        pygame.draw.rect(
            screen,
            self.panel_color,
            panel,
            border_radius=14
        )

        pygame.draw.rect(
            screen,
            self.border_color,
            panel,
            2,
            border_radius=14
        )

        instructions = [
            "SELECT A DEFENCE",
            "Archer fires fast; Mage slows; Cannon splashes.",
            "DEPLOY TOWERS",
            "Choose a card, then left-click open ground.",
            "UPGRADE TOWERS",
            "Click a built tower again; upgrades reach Level 3.",
            "BUILD WALLS",
            "Right-click ground to build or remove a wall.",
            "AUTOMATIC ASSAULTS",
            "Waves start automatically and grow stronger.",
            "METEOR STRIKE",
            "Select Meteor, then click the battlefield (5s recharge).",
            "WAVE REWARDS",
            "Choose gold, gate repair, or permanent tower damage.",
            "VETERAN TROOPS",
            "From wave 16, troops have damage-absorbing shields.",
            "PAUSE / RESTART / EXIT",
            "Press P, R, or Escape respectively.",
        ]
        instruction_headings = {
            "SELECT A DEFENCE",
            "DEPLOY TOWERS",
            "UPGRADE TOWERS",
            "BUILD WALLS",
            "AUTOMATIC ASSAULTS",
            "METEOR STRIKE",
            "WAVE REWARDS",
            "VETERAN TROOPS",
            "PAUSE / RESTART / EXIT",
        }

        y = 145

        for line in instructions:
            is_heading = line in instruction_headings
            if is_heading:
                font = self.text_font
                color = self.text_color

            else:

                font = self.small_font
                color = self.secondary_color

            surface = font.render(
                line,
                True,
                color
            )

            screen.blit(
                surface,
                (220, y)
            )

            y += 27 if is_heading else 18

        # --------------------------------------------------------
        # AI SECTION
        # --------------------------------------------------------

        ai_title = self.text_font.render(
            "CLASSICAL AI SYSTEM",
            True,
            self.text_color
        )

        screen.blit(
            ai_title,
            (650, 145)
        )

        ai_lines = [
            "Knowledge Representation",
            "Rule-Based Reasoning",
            "State-Space Reasoning",
            "Minimax Search",
            "Alpha-Beta Pruning",
            "A* Pathfinding",
            "Manhattan Heuristic",
            "Dynamic Route Replanning",
        ]

        y = 190

        for line in ai_lines:

            surface = self.small_font.render(
                "• " + line,
                True,
                self.secondary_color
            )

            screen.blit(
                surface,
                (660, y)
            )

            y += 27

        power_heading = self.text_font.render(
            "BATTLE SUPPORT",
            True,
            self.text_color
        )
        screen.blit(power_heading, (650, 420))
        power_lines = [
            "Meteor Strike targets enemies across an area.",
            "Earn gold from kills and wave completion.",
            "Wave rewards supply gold, repair, or tower damage.",
        ]
        for index, line in enumerate(power_lines):
            surface = self.small_font.render(
                line,
                True,
                self.secondary_color
            )
            screen.blit(surface, (660, 454 + index * 24))

        self.draw_button(
            screen,
            self.back_rect,
            "BACK"
        )

    # ============================================================
    # END SCREEN
    # ============================================================

    def draw_end_screen(self, screen):
        game_state = self.game.game_state
        overlay = pygame.Surface(
            (screen.get_width(), screen.get_height() - HUD_HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((5, 9, 16, 132))
        screen.blit(overlay, (0, HUD_HEIGHT))

        card = pygame.Rect(300, 230, 680, 385)
        pygame.draw.rect(screen, (5, 10, 18), card.move(0, 8), border_radius=18)
        pygame.draw.rect(screen, (18, 28, 43), card, border_radius=18)
        pygame.draw.rect(screen, (119, 103, 77), card, 2, border_radius=18)

        if game_state.is_victory():
            title_text = "REALM SECURED"
            title_color = (94, 231, 170)
        else:
            title_text = "EMPIRE DEFEATED"
            title_color = (255, 91, 87)

        title = pygame.font.SysFont("segoeui", 48, bold=True).render(
            title_text,
            True,
            title_color
        )
        screen.blit(title, title.get_rect(center=(640, 292)))

        message = self.text_font.render(
            game_state.message or "The battle is over.",
            True,
            (219, 226, 235)
        )
        screen.blit(message, message.get_rect(center=(640, 335)))

        state = game_state.get_state()
        statistics = [
            ("LAST WAVE", state["wave"], (100, 174, 255)),
            ("GOLD", state["gold"], (255, 190, 67)),
            ("TOWERS", state["tower_count"], (115, 218, 179)),
            ("WALLS", state["wall_count"], (211, 178, 126)),
        ]
        for index, (label, value, accent) in enumerate(statistics):
            metric = pygame.Rect(342 + index * 150, 365, 136, 50)
            pygame.draw.rect(screen, (27, 40, 57), metric, border_radius=8)
            pygame.draw.rect(screen, accent, metric, 1, border_radius=8)
            label_surface = self.small_font.render(label, True, self.secondary_color)
            value_surface = self.text_font.render(str(value), True, accent)
            screen.blit(label_surface, label_surface.get_rect(center=(metric.centerx, metric.y + 13)))
            screen.blit(value_surface, value_surface.get_rect(center=(metric.centerx, metric.y + 33)))

        self.draw_button(screen, self.restart_rect, "RESTART BATTLE")
        self.draw_button(
            screen,
            self.end_quit_rect,
            "QUIT TO DESKTOP"
        )

    # ============================================================
    # DRAW
    # ============================================================

    def draw(self, screen):

        if self.screen_state == self.MAIN_MENU:

            self.draw_main_menu(screen)

        elif self.screen_state == self.INSTRUCTIONS:

            self.draw_instructions(screen)

        elif self.screen_state == self.END_SCREEN:

            self.draw_end_screen(screen)

    # ============================================================
    # EVENT HANDLING
    # ============================================================

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                if self.screen_state == self.INSTRUCTIONS:

                    self.screen_state = self.MAIN_MENU

                elif self.screen_state == self.MAIN_MENU:

                    self.game.running = False

                return

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if event.button != 1:
            return

        # --------------------------------------------------------
        # Main menu
        # --------------------------------------------------------

        if self.screen_state == self.MAIN_MENU:

            if self.start_rect.collidepoint(event.pos):

                self.screen_state = self.PLAYING

            elif self.instructions_rect.collidepoint(
                event.pos
            ):

                self.screen_state = self.INSTRUCTIONS

            elif self.quit_rect.collidepoint(event.pos):

                self.game.running = False

        # --------------------------------------------------------
        # Instructions
        # --------------------------------------------------------

        elif self.screen_state == self.INSTRUCTIONS:

            if self.back_rect.collidepoint(event.pos):

                self.screen_state = self.MAIN_MENU

        # --------------------------------------------------------
        # End screen
        # --------------------------------------------------------

        elif self.screen_state == self.END_SCREEN:

            if (
                self.game.hud.restart_at(event.pos)
                or self.restart_rect.collidepoint(event.pos)
            ):

                self.game.restart()

                self.game.menu.start_game()

            elif self.end_quit_rect.collidepoint(
                event.pos
            ):

                self.game.running = False

    # ============================================================
    # GAME START
    # ============================================================

    def start_game(self):

        self.screen_state = self.PLAYING

    # ============================================================
    # GAME END
    # ============================================================

    def show_end_screen(self):

        self.screen_state = self.END_SCREEN

    # ============================================================
    # MENU STATE
    # ============================================================

    def is_main_menu(self):

        return self.screen_state == self.MAIN_MENU

    def is_playing(self):

        return self.screen_state == self.PLAYING

    def is_instructions(self):

        return self.screen_state == self.INSTRUCTIONS