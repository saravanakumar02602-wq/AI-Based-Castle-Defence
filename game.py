import array
import math
import random

import pygame

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    GAME_TITLE,
    BACKGROUND_COLOR,
    BATTLEFIELD_TOP,
    BATTLEFIELD_LEFT,
    BATTLEFIELD_HEIGHT,
    GRID_COLS,
    GRID_ROWS,
    CELL_SIZE,
    STARTING_CASTLE_HEALTH,
)

from battlefield.grid import Grid

from entities.castle import Castle

from ai.commander import AICommander

from systems.wave_manager import WaveManager
from systems.combat import CombatSystem
from systems.resource_manager import ResourceManager
from systems.game_state import GameStateManager
from systems.tower_manager import TowerManager
from systems.wall_manager import WallManager

from ui.hud import HUD
from ui.menu import Menu


class Game:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        pygame.display.set_caption(GAME_TITLE)

        self.clock = pygame.time.Clock()

        self.running = True
        self.paused = False

        self.initialize_game()

    # ==================================================
    # INITIALIZE GAME
    # ==================================================

    def initialize_game(self):

        # Battlefield.
        self.grid = Grid()

        # Castle.
        self.castle = Castle(
            self.grid.castle_position,
            health=STARTING_CASTLE_HEALTH
        )

        # Dynamic game objects.
        self.enemies = []
        self.towers = []
        self.selected_tower_type = "ARCHER"
        self.score = 0

        # Classical AI Commander.
        self.commander = AICommander(self)

        # Game systems.
        self.resource_manager = ResourceManager(
            starting_gold=500
        )

        self.tower_manager = TowerManager(self)

        self.wall_manager = WallManager(self)

        self.wave_manager = WaveManager(self)

        self.combat_system = CombatSystem(self)

        self.game_state = GameStateManager(self)

        self.tower_damage_multiplier = 1.0
        self.meteor_cooldown = 0.0
        self.meteor_targeting = False
        self.impact_craters = []
        self.particles = []
        self.screen_shake = 0.0
        self.notice = ""
        self.notice_timer = 0.0
        self.bonus_rects = {
            "gold": pygame.Rect(176, 315, 290, 190),
            "repair": pygame.Rect(495, 315, 290, 190),
            "damage": pygame.Rect(814, 315, 290, 190),
        }
        self.sounds = {}
        self.initialize_sounds()

        # User interface.
        self.hud = HUD(self)

        self.menu = Menu(self)

    # ==================================================
    # MAIN LOOP
    # ==================================================

    def run(self):

        while self.running:

            delta_time = (
                self.clock.tick(FPS) / 1000.0
            )

            for event in pygame.event.get():
                self.handle_event(event)

            self.update(delta_time)

            self.draw()

        pygame.quit()

    # ==================================================
    # EVENT HANDLING
    # ==================================================

    def handle_event(self, event):

        # ------------------------------
        # Menu
        # ------------------------------

        if not self.menu.is_playing():

            if event.type == pygame.QUIT:
                self.running = False
                return

            self.menu.handle_event(event)
            return

        # ------------------------------
        # Window close
        # ------------------------------

        if event.type == pygame.QUIT:

            self.running = False
            return

        if self.wave_manager.bonus_pending:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                self.handle_bonus_click(event.pos)
            return

        # ------------------------------
        # Keyboard
        # ------------------------------

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE and self.meteor_targeting:
                self.meteor_targeting = False
                self.show_notice("Meteor targeting cancelled.")
                return

            # Escape = quit.
            if event.key == pygame.K_ESCAPE:

                self.running = False
                return

            # P = pause.
            if event.key == pygame.K_p:

                self.paused = not self.paused

                self.show_notice(
                    "Game paused."
                    if self.paused
                    else "Game resumed."
                )

                return

            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.selected_tower_type = {
                    pygame.K_1: "ARCHER",
                    pygame.K_2: "MAGE",
                    pygame.K_3: "CANNON",
                }[event.key]
                self.meteor_targeting = False
                return

            if event.key == pygame.K_m:
                self.select_meteor()
                return

            # R = restart.
            if event.key == pygame.K_r:

                self.restart()
                return

        # ------------------------------
        # Mouse
        # ------------------------------

        if event.type == pygame.MOUSEBUTTONDOWN:

            if self.paused:
                return

            mouse_position = event.pos

            # Left mouse button.
            if event.button == 1:
                if self.wave_manager.bonus_pending:
                    self.handle_bonus_click(mouse_position)
                    return

                tower_type = self.hud.tower_card_at(mouse_position)
                if tower_type is not None:
                    self.selected_tower_type = tower_type
                    self.meteor_targeting = False
                    return

                if self.hud.restart_at(mouse_position):
                    self.restart()
                    return

                if self.hud.meteor_at(mouse_position):
                    self.select_meteor()
                    return

                if self.meteor_targeting:
                    self.cast_meteor(mouse_position)
                    return

                self.handle_tower_click(
                    mouse_position
                )

            # Right mouse button.
            elif event.button == 3:

                self.handle_wall_click(
                    mouse_position
                )

    # ==================================================
    # GAME UPDATE
    # ==================================================

    def update(self, delta_time):

        if not self.menu.is_playing():
            return

        if not self.game_state.is_playing():
            return

        if self.paused:
            return

        if self.wave_manager.bonus_pending:
            self.update_visual_effects(delta_time)
            self.castle.update(delta_time)
            return

        self.castle.update(delta_time)
        self.resource_manager.update(delta_time)
        self.meteor_cooldown = max(
            0.0,
            self.meteor_cooldown - delta_time
        )
        self.screen_shake = max(
            0.0,
            self.screen_shake - delta_time
        )
        self.notice_timer = max(
            0.0,
            self.notice_timer - delta_time
        )

        # ---------------------------------------------
        # 1. Classical AI Commander
        # ---------------------------------------------

        self.commander.update(self)

        # ---------------------------------------------
        # 2. Enemy movement
        # ---------------------------------------------

        for enemy in self.enemies:

            if enemy.alive:

                enemy.update(delta_time)

        # ---------------------------------------------
        # 3. Spawn / wave management
        # ---------------------------------------------

        self.wave_manager.update(
            delta_time
        )

        # ---------------------------------------------
        # 4. Combat
        # ---------------------------------------------

        self.combat_system.update(
            delta_time
        )

        self.update_enemy_states()
        self.update_visual_effects(delta_time)

        # ---------------------------------------------
        # 5. Game state
        # ---------------------------------------------

        self.game_state.update()

    def start_wave(self):
        if self.wave_manager.start_wave():
            self.meteor_targeting = False
            self.show_notice(
                f"Wave {self.wave_manager.current_wave} has begun. Defend the keep."
            )

    def handle_bonus_click(self, position):
        for bonus, rect in self.bonus_rects.items():
            if rect.collidepoint(position):
                self.choose_wave_bonus(bonus)
                return

    def choose_wave_bonus(self, bonus):
        if not self.wave_manager.bonus_pending:
            return

        if bonus == "gold":
            self.resource_manager.add_gold(150)
            message = "Supply cache secured: 150 gold added to your reserves."
        elif bonus == "repair":
            repaired = min(
                self.castle.max_health * 0.25,
                self.castle.max_health - self.castle.health
            )
            self.castle.health += repaired
            self.castle.alive = self.castle.health > 0
            message = f"Gate reinforced: integrity restored by {round(repaired)} points."
        elif bonus == "damage":
            self.tower_damage_multiplier *= 1.2
            for tower in self.towers:
                tower.damage = max(1, round(tower.damage * 1.2))
            message = "Arsenal upgraded: tower damage increased by 20%."
        else:
            return

        self.wave_manager.start_next_wave()
        self.show_notice(message)

    def select_meteor(self):
        if self.meteor_cooldown > 0:
            self.show_notice(
                f"Meteor Strike recharging: {self.meteor_cooldown:.1f} seconds."
            )
            return

        self.meteor_targeting = not self.meteor_targeting
        self.show_notice(
            "Select an impact point on the battlefield."
            if self.meteor_targeting
            else "Meteor targeting cancelled."
        )

    def cast_meteor(self, mouse_position):
        if self.screen_to_grid(mouse_position) is None:
            self.show_notice("Select a valid battlefield tile for the strike.")
            return

        impact_x, impact_y = mouse_position
        impact = pygame.Vector2(impact_x, impact_y)
        self.impact_craters.append((impact_x, impact_y, 110))
        self.screen_shake = max(self.screen_shake, 0.42)
        self.play_sound("explosion")
        self.spawn_particles((impact_x, impact_y), (255, 119, 39), 42)
        self.spawn_particles((impact_x, impact_y), (255, 222, 127), 24)

        for enemy in self.enemies:
            if not enemy.alive:
                continue
            enemy_position = pygame.Vector2(
                *self.enemy_screen_position(enemy)
            )
            distance = impact.distance_to(enemy_position)
            if distance <= 110:
                damage = max(30, round(150 * (1 - distance / 220)))
                enemy.take_damage(damage)
                self.spawn_particles(
                    self.enemy_screen_position(enemy),
                    (255, 186, 91),
                    12
                )

        self.combat_system.remove_dead_enemies()
        self.combat_system.cleanup_dead_enemies()
        self.meteor_targeting = False
        self.meteor_cooldown = 5.0
        self.show_notice("Meteor impact confirmed. Hostile units in range have been struck.")

    def enemy_screen_position(self, enemy):
        return (
            round(BATTLEFIELD_LEFT + (enemy.col + 0.5) * CELL_SIZE),
            round(BATTLEFIELD_TOP + (enemy.row + 0.5) * CELL_SIZE),
        )

    def castle_screen_position(self):
        return (
            BATTLEFIELD_LEFT + GRID_COLS * CELL_SIZE + 45,
            BATTLEFIELD_TOP + GRID_ROWS * CELL_SIZE // 2,
        )

    def spawn_particles(self, position, color, count=10):
        x, y = position
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(35, 180)
            lifetime = random.uniform(0.22, 0.65)
            self.particles.append({
                "x": float(x),
                "y": float(y),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": lifetime,
                "max_life": lifetime,
                "radius": random.randint(2, 5),
                "color": color,
            })

    def update_visual_effects(self, delta_time):
        remaining = []
        for particle in self.particles:
            particle["life"] -= delta_time
            if particle["life"] <= 0:
                continue
            particle["x"] += particle["vx"] * delta_time
            particle["y"] += particle["vy"] * delta_time
            particle["vx"] *= max(0.0, 1 - delta_time * 2.2)
            particle["vy"] *= max(0.0, 1 - delta_time * 2.2)
            remaining.append(particle)
        self.particles = remaining

    def update_enemy_states(self):
        for enemy in self.enemies:
            if (
                not enemy.alive
                or enemy.state != "ADVANCING"
                or enemy.health / max(1, enemy.max_health) >= 0.35
            ):
                continue

            target = self.commander.select_retreat_target(self, enemy)
            path = self.commander.calculate_path(
                enemy.position,
                target
            )
            if not path:
                continue
            enemy.set_path(path)
            enemy.state = "RETREATING"

    def initialize_sounds(self):
        mixer_settings = pygame.mixer.get_init()
        if mixer_settings is None:
            return

        sample_rate = mixer_settings[0]
        channels = mixer_settings[2]
        presets = {
            "shoot": (620, 260, 0.075),
            "hit": (220, 85, 0.11),
            "explosion": (130, 32, 0.32),
            "build": (420, 760, 0.12),
            "gate": (160, 72, 0.2),
        }
        for name, (start_frequency, end_frequency, duration) in presets.items():
            sample_count = max(1, int(sample_rate * duration))
            samples = array.array("h")
            for index in range(sample_count):
                progress = index / sample_count
                frequency = start_frequency + (
                    end_frequency - start_frequency
                ) * progress
                envelope = (1 - progress) ** 2
                sample = math.sin(
                    math.tau * frequency * index / sample_rate
                )
                value = int(sample * envelope * 10000)
                for _ in range(channels):
                    samples.append(value)
            sound = pygame.mixer.Sound(buffer=samples.tobytes())
            sound.set_volume(0.35)
            self.sounds[name] = sound

    def play_sound(self, name):
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

    def show_notice(self, message):
        self.notice = message
        self.notice_timer = 2.5

    # ==================================================
    # MOUSE -> GRID
    # ==================================================

    def screen_to_grid(self, mouse_position):

        mouse_x, mouse_y = mouse_position

        # Ignore HUD area.
        if mouse_y < BATTLEFIELD_TOP:
            return None

        battlefield_y = (
            mouse_y - BATTLEFIELD_TOP
        )

        col = (mouse_x - BATTLEFIELD_LEFT) // CELL_SIZE
        row = battlefield_y // CELL_SIZE

        if not (
            mouse_x >= BATTLEFIELD_LEFT
            and
            0 <= row < GRID_ROWS
            and
            0 <= col < GRID_COLS
        ):
            return None

        return int(row), int(col)

    # ==================================================
    # TOWER CLICK
    # ==================================================

    def handle_tower_click(self, mouse_position):

        grid_position = self.screen_to_grid(
            mouse_position
        )

        if grid_position is None:
            return

        row, col = grid_position

        # ---------------------------------------------
        # If a tower already exists:
        # upgrade it.
        # ---------------------------------------------

        existing_tower = (
            self.tower_manager.get_tower_at(
                row,
                col
            )
        )

        if existing_tower is not None:

            upgraded = (
                self.tower_manager.upgrade_tower(
                    row,
                    col
                )
            )

            if upgraded:

                print(
                    f"Tower upgraded at "
                    f"({row}, {col})"
                )
                self.show_notice(
                    f"Tower upgraded to Level {existing_tower.level}."
                )
            else:
                self.show_notice("Upgrade unavailable. Check the tower level and your gold reserves.")

            return

        # ---------------------------------------------
        # Otherwise place a new tower.
        # ---------------------------------------------

        placed = (
            self.tower_manager.place_tower(
                row,
                col
            )
        )

        if placed:

            self.play_sound("build")
            print(
                f"Tower built at "
                f"({row}, {col})"
            )
            self.show_notice("Tower deployed. Select it again to upgrade.")
        else:
            self.show_notice("Placement unavailable. Check tile access, route clearance, and gold.")

    # ==================================================
    # WALL CLICK
    # ==================================================

    def handle_wall_click(self, mouse_position):

        grid_position = self.screen_to_grid(
            mouse_position
        )

        if grid_position is None:
            return

        row, col = grid_position

        cell = self.grid.get_cell(
            row,
            col
        )

        if cell is None:
            return

        # ---------------------------------------------
        # If wall already exists:
        # remove it and receive refund.
        # ---------------------------------------------

        if cell.has_wall:

            removed = (
                self.wall_manager.remove_wall(
                    row,
                    col
                )
            )

            if removed:

                print(
                    f"Wall removed at "
                    f"({row}, {col})"
                )

            return

        # ---------------------------------------------
        # Otherwise build a wall.
        # ---------------------------------------------

        placed = (
            self.wall_manager.place_wall(
                row,
                col
            )
        )

        if placed:

            print(
                f"Wall built at "
                f"({row}, {col})"
            )
            self.show_notice("Defensive wall constructed.")
        else:
            self.show_notice("Wall placement unavailable. Check the tile and available gold.")

    # ==================================================
    # RESTART
    # ==================================================

    def restart(self):

        print("Restarting game...")

        self.paused = False

        self.initialize_game()

        # Return to gameplay rather than the menu.
        self.menu.screen_state = (
            self.menu.PLAYING
        )

    # ==================================================
    # DRAW
    # ==================================================

    def draw(self):

        # ---------------------------------------------
        # Menu
        # ---------------------------------------------

        if not self.menu.is_playing():

            self.menu.draw(
                self.screen
            )

            pygame.display.flip()

            return

        self.screen.fill(BACKGROUND_COLOR)
        battlefield = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA
        )
        self.grid.draw(battlefield)
        self.draw_impact_craters(battlefield)
        hovered_cell = self.screen_to_grid(pygame.mouse.get_pos())
        for tower in self.towers:
            if tower.position == hovered_cell:
                tower.draw_range(battlefield)
            target = self.combat_system.find_nearest_enemy(tower)
            tower.draw(
                battlefield,
                target.position if target is not None else None
            )

        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(battlefield)

        self.combat_system.draw_projectiles(battlefield)
        self.castle.draw(battlefield)
        self.draw_particles(battlefield)
        self.draw_meteor_target(battlefield)

        if self.screen_shake > 0:
            strength = max(1, round(self.screen_shake * 18))
            offset = (
                random.randint(-strength, strength),
                random.randint(-strength, strength)
            )
        else:
            offset = (0, 0)
        self.screen.blit(battlefield, offset)

        self.hud.draw(self.screen)

        if self.notice_timer > 0:
            self.draw_notice()

        if self.wave_manager.bonus_pending:
            self.draw_wave_bonus_overlay()

        # ---------------------------------------------
        # Pause overlay
        # ---------------------------------------------

        if self.paused:

            self.draw_pause_overlay()

        # ---------------------------------------------
        # End screen
        # ---------------------------------------------

        if (
            self.game_state.is_game_over()
            or
            self.game_state.is_victory()
        ):

            self.menu.show_end_screen()

            self.menu.draw(
                self.screen
            )

        pygame.display.flip()

    def draw_impact_craters(self, surface):
        for x, y, radius in self.impact_craters:
            crater = pygame.Rect(
                x - radius // 2,
                y - radius // 3,
                radius,
                max(12, radius // 2)
            )
            pygame.draw.ellipse(surface, (25, 17, 14), crater)
            pygame.draw.ellipse(
                surface, (101, 58, 34), crater, 4
            )
            pygame.draw.arc(
                surface,
                (191, 119, 65),
                crater.inflate(-8, -5),
                0.15,
                2.65,
                2
            )

    def draw_particles(self, surface):
        for particle in self.particles:
            alpha = max(
                0,
                min(
                    255,
                    int(255 * particle["life"] / particle["max_life"])
                )
            )
            particle_surface = pygame.Surface(
                (particle["radius"] * 2, particle["radius"] * 2),
                pygame.SRCALPHA
            )
            color = (*particle["color"], alpha)
            pygame.draw.circle(
                particle_surface,
                color,
                (particle["radius"], particle["radius"]),
                particle["radius"]
            )
            surface.blit(
                particle_surface,
                (
                    round(particle["x"] - particle["radius"]),
                    round(particle["y"] - particle["radius"])
                )
            )

    def draw_meteor_target(self, surface):
        if not self.meteor_targeting:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.screen_to_grid((mouse_x, mouse_y)) is None:
            return

        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA
        )
        pygame.draw.circle(
            overlay,
            (255, 112, 38, 35),
            (mouse_x, mouse_y),
            110
        )
        pygame.draw.circle(
            overlay,
            (255, 176, 95, 190),
            (mouse_x, mouse_y),
            110,
            2
        )
        pygame.draw.line(
            overlay,
            (255, 224, 164, 220),
            (mouse_x - 9, mouse_y),
            (mouse_x + 9, mouse_y),
            2
        )
        pygame.draw.line(
            overlay,
            (255, 224, 164, 220),
            (mouse_x, mouse_y - 9),
            (mouse_x, mouse_y + 9),
            2
        )
        surface.blit(overlay, (0, 0))

    def draw_wave_bonus_overlay(self):
        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((4, 8, 15, 205))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(165, 185, 950, 340)
        pygame.draw.rect(
            self.screen,
            (17, 28, 44),
            panel,
            border_radius=20
        )
        pygame.draw.rect(
            self.screen,
            (91, 116, 145),
            panel,
            2,
            border_radius=20
        )

        title_font = pygame.font.SysFont("segoeui", 34, bold=True)
        body_font = pygame.font.SysFont("segoeui", 17)
        card_title_font = pygame.font.SysFont("segoeui", 19, bold=True)
        card_body_font = pygame.font.SysFont("segoeui", 14)
        title = title_font.render(
            "WAVE COMPLETED!",
            True,
            (255, 218, 127)
        )
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 225))
        gift_rect = pygame.Rect(title_rect.left - 34, title_rect.centery - 12, 24, 22)
        pygame.draw.rect(self.screen, (246, 185, 53), gift_rect, border_radius=3)
        pygame.draw.rect(
            self.screen,
            (190, 58, 58),
            pygame.Rect(gift_rect.centerx - 3, gift_rect.y, 6, gift_rect.height)
        )
        pygame.draw.rect(
            self.screen,
            (190, 58, 58),
            pygame.Rect(gift_rect.x, gift_rect.y + 7, gift_rect.width, 5)
        )
        pygame.draw.arc(
            self.screen,
            (255, 219, 128),
            pygame.Rect(gift_rect.centerx - 9, gift_rect.y - 8, 10, 10),
            0.2,
            3.0,
            3
        )
        pygame.draw.arc(
            self.screen,
            (255, 219, 128),
            pygame.Rect(gift_rect.centerx - 1, gift_rect.y - 8, 10, 10),
            0.2,
            3.0,
            3
        )
        self.screen.blit(title, title_rect)
        body = body_font.render(
            "Choose your tactical Wave Bonus to upgrade your fortress defense:",
            True,
            (190, 204, 224)
        )
        self.screen.blit(body, body.get_rect(center=(WINDOW_WIDTH // 2, 272)))

        choices = (
            (
                "gold",
                "Gold Bounty",
                "Receive +150 gold reserves\ninstantly to buy defenses.",
                (255, 196, 66),
                "$"
            ),
            (
                "repair",
                "Reinforce Gate",
                "Restore & bolster your Gate\nIntegrity by +25% HP.",
                (84, 210, 163),
                "+"
            ),
            (
                "damage",
                "Power Calibrations",
                "Increase damage of all towers\nglobally by +20% permanently.",
                (184, 137, 255),
                "damage"
            ),
        )
        for bonus, title_text, detail, accent, icon in choices:
            rect = self.bonus_rects[bonus]
            hover = rect.collidepoint(pygame.mouse.get_pos())
            fill = (34, 48, 67) if hover else (26, 39, 57)
            pygame.draw.rect(
                self.screen,
                fill,
                rect,
                border_radius=14
            )
            pygame.draw.rect(
                self.screen,
                accent,
                rect,
                2 if hover else 1,
                border_radius=14
            )
            icon_center = (rect.centerx, rect.y + 43)
            pygame.draw.circle(
                self.screen,
                (19, 31, 47),
                icon_center,
                27
            )
            if icon == "$":
                pygame.draw.ellipse(
                    self.screen,
                    (221, 145, 47),
                    pygame.Rect(icon_center[0] - 16, icon_center[1] - 15, 32, 32)
                )
                pygame.draw.rect(
                    self.screen,
                    (255, 206, 88),
                    pygame.Rect(icon_center[0] - 5, icon_center[1] - 20, 10, 8)
                )
                pygame.draw.line(
                    self.screen,
                    (255, 223, 139),
                    (icon_center[0] - 8, icon_center[1] - 4),
                    (icon_center[0] + 8, icon_center[1] - 4),
                    2
                )
                pygame.draw.line(
                    self.screen,
                    (255, 223, 139),
                    (icon_center[0] - 8, icon_center[1] + 7),
                    (icon_center[0] + 8, icon_center[1] + 7),
                    2
                )
                value_font = pygame.font.SysFont("segoeui", 19, bold=True)
                value = value_font.render("$", True, (255, 244, 204))
                self.screen.blit(value, value.get_rect(center=icon_center))
            elif icon == "+":
                pygame.draw.line(
                    self.screen, (222, 211, 188),
                    (icon_center[0] - 12, icon_center[1] + 12),
                    (icon_center[0] + 12, icon_center[1] - 12), 7
                )
                pygame.draw.line(
                    self.screen, (157, 104, 66),
                    (icon_center[0] - 12, icon_center[1] + 12),
                    (icon_center[0] - 2, icon_center[1] + 2), 5
                )
                pygame.draw.line(
                    self.screen, (105, 130, 154),
                    (icon_center[0] + 1, icon_center[1] - 1),
                    (icon_center[0] + 13, icon_center[1] - 13), 5
                )
                pygame.draw.line(
                    self.screen, (222, 211, 188),
                    (icon_center[0] - 12, icon_center[1] - 12),
                    (icon_center[0] + 12, icon_center[1] + 12), 5
                )
                pygame.draw.line(
                    self.screen, (157, 104, 66),
                    (icon_center[0] + 2, icon_center[1] + 2),
                    (icon_center[0] + 12, icon_center[1] + 12), 4
                )
                pygame.draw.line(
                    self.screen, (105, 130, 154),
                    (icon_center[0] - 2, icon_center[1] - 2),
                    (icon_center[0] - 12, icon_center[1] - 12), 4
                )
            else:
                pygame.draw.polygon(
                    self.screen,
                    (255, 178, 58),
                    [
                        (icon_center[0] + 3, icon_center[1] - 21),
                        (icon_center[0] - 11, icon_center[1] + 1),
                        (icon_center[0] - 1, icon_center[1] + 1),
                        (icon_center[0] - 5, icon_center[1] + 20),
                        (icon_center[0] + 13, icon_center[1] - 5),
                        (icon_center[0] + 4, icon_center[1] - 5),
                    ]
                )
            heading = card_title_font.render(
                title_text,
                True,
                accent
            )
            detail_lines = detail.split("\n")
            detail_surface = card_body_font.render(
                detail_lines[0],
                True,
                (208, 218, 232)
            )
            second_detail = card_body_font.render(
                detail_lines[1],
                True,
                (208, 218, 232)
            )
            self.screen.blit(
                heading,
                heading.get_rect(center=(rect.centerx, rect.y + 91))
            )
            self.screen.blit(
                detail_surface,
                detail_surface.get_rect(center=(rect.centerx, rect.y + 126))
            )
            self.screen.blit(
                second_detail,
                second_detail.get_rect(center=(rect.centerx, rect.y + 147))
            )

    def draw_notice(self):
        notice_rect = pygame.Rect(
            310, WINDOW_HEIGHT - 52, 660, 34
        )
        panel = pygame.Surface(notice_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            panel, (13, 21, 28, 236),
            panel.get_rect(), border_radius=10
        )
        self.screen.blit(panel, notice_rect)
        pygame.draw.rect(
            self.screen, (111, 164, 156),
            notice_rect, 1, border_radius=10
        )

        font = pygame.font.SysFont("segoeui", 14, bold=True)
        text = font.render(self.notice, True, (232, 239, 232))
        self.screen.blit(
            text,
            text.get_rect(center=notice_rect.center)
        )

    # ==================================================
    # PAUSE OVERLAY
    # ==================================================

    def draw_pause_overlay(self):

        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 150)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        font = pygame.font.Font(
            None,
            48
        )

        text = font.render(
            "GAME PAUSED",
            True,
            (255, 255, 255)
        )

        text_rect = text.get_rect(
            center=(
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2
            )
        )

        self.screen.blit(
            text,
            text_rect
        )


if __name__ == "__main__":

    game = Game()

    game.run()