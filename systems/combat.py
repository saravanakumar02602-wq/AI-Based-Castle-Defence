import math
from dataclasses import dataclass

import pygame

from entities.enemy import Enemy
from settings import BATTLEFIELD_LEFT, BATTLEFIELD_TOP, CELL_SIZE


@dataclass
class TowerProjectile:
    start: pygame.Vector2
    target_position: pygame.Vector2
    target_enemy: Enemy
    tower_type: str
    damage: int
    travel_time: float
    elapsed: float = 0.0

    @property
    def progress(self):
        return min(1.0, self.elapsed / self.travel_time)

    @property
    def position(self):
        progress = self.progress
        point = self.start.lerp(self.target_position, progress)
        if self.tower_type == "ARCHER":
            point.y -= math.sin(math.pi * progress) * 14
        return point


class CombatSystem:
    """
    Handles combat between:
    - Player towers
    - Enemy units
    - Castle

    The enemy's strategic behaviour is controlled by
    AICommander.
    """

    def __init__(self, game):
        self.game = game

        # Combat timing
        self.attack_interval = 0.5
        self.attack_timer = 0.0

        # Prevent duplicate rewards
        self.previous_enemy_states = {}

        # Enemy tower attack settings
        self.enemy_tower_attack_range = 1
        self.enemy_tower_damage = 15
        self.projectiles = []

    # ============================================================
    # MAIN UPDATE
    # ============================================================

    def update(self, delta_time=0.0):

        if not self.game.castle.alive:
            return

        self.update_projectiles(delta_time)

        self.attack_timer += delta_time

        if self.attack_timer < self.attack_interval:
            return

        self.attack_timer = 0.0

        # Player towers attack enemies.
        self.towers_attack_enemies()

        # Enemies make strategic combat decisions.
        self.enemies_take_action()

        # Remove defeated enemies / reward player.
        self.remove_dead_enemies()

    # ============================================================
    # DISTANCE
    # ============================================================

    def distance(self, position_a, position_b):
        row_a, col_a = position_a
        row_b, col_b = position_b

        return abs(row_a - row_b) + abs(col_a - col_b)

    # ============================================================
    # PLAYER TOWER COMBAT
    # ============================================================

    def towers_attack_enemies(self):

        for tower in self.game.towers:

            if tower.cooldown > 0:
                tower.cooldown -= 1
                continue

            target = self.find_nearest_enemy(tower)

            if target is None:
                continue

            source = pygame.Vector2(
                BATTLEFIELD_LEFT + tower.col * CELL_SIZE + CELL_SIZE // 2,
                BATTLEFIELD_TOP + tower.row * CELL_SIZE + CELL_SIZE // 2
            )
            destination = pygame.Vector2(
                *self.game.enemy_screen_position(target)
            )
            projectile_speed = {
                "ARCHER": 560,
                "MAGE": 360,
                "CANNON": 280,
            }.get(tower.tower_type, 450)
            distance = source.distance_to(destination)
            self.projectiles.append(
                TowerProjectile(
                    start=source,
                    target_position=destination,
                    target_enemy=target,
                    tower_type=tower.tower_type,
                    damage=tower.damage,
                    travel_time=max(0.12, distance / projectile_speed)
                )
            )

            tower.cooldown = tower.attack_cooldown
            self.game.spawn_particles(
                (round(source.x), round(source.y)),
                {
                    "ARCHER": (255, 222, 157),
                    "MAGE": (196, 162, 255),
                    "CANNON": (255, 162, 88),
                }.get(tower.tower_type, (229, 232, 235)),
                3
            )
            self.game.play_sound("shoot")

            print(
                f"Tower at {tower.position} "
                f"fired at enemy at {target.position}."
            )

    def update_projectiles(self, delta_time):
        remaining = []
        for projectile in self.projectiles:
            if projectile.target_enemy.alive:
                projectile.target_position.update(
                    self.game.enemy_screen_position(projectile.target_enemy)
                )
            projectile.elapsed += delta_time
            if projectile.elapsed < projectile.travel_time:
                remaining.append(projectile)
                continue

            self.resolve_projectile_impact(projectile)

        self.projectiles = remaining

    def resolve_projectile_impact(self, projectile):
        impact_x, impact_y = (
            round(projectile.target_position.x),
            round(projectile.target_position.y)
        )
        if projectile.tower_type == "CANNON":
            if projectile.target_enemy.alive:
                impact_x, impact_y = self.game.enemy_screen_position(
                    projectile.target_enemy
                )
            self.game.impact_craters.append((impact_x, impact_y, 34))
            self.game.screen_shake = max(self.game.screen_shake, 0.1)
            self.game.play_sound("explosion")
            impact_radius = 48
            for enemy in self.game.enemies:
                if not enemy.alive:
                    continue
                if self.game_screen_position_distance(
                    enemy, projectile.target_position
                ) <= impact_radius:
                    enemy.take_damage(projectile.damage)
                    self.game.spawn_particles(
                        self.game.enemy_screen_position(enemy),
                        (255, 157, 75),
                        8
                    )
            return

        target = projectile.target_enemy
        if not target.alive:
            return

        target.take_damage(projectile.damage)
        impact_color = (
            (200, 160, 255)
            if projectile.tower_type == "MAGE"
            else (183, 212, 255)
        )
        self.game.spawn_particles(
            self.game.enemy_screen_position(target),
            impact_color,
            7
        )
        self.game.play_sound("hit")

        if projectile.tower_type == "MAGE" and target.alive:
            target.apply_slow(2.5)

    def game_screen_position_distance(self, enemy, point):
        enemy_position = pygame.Vector2(
            *self.game.enemy_screen_position(enemy)
        )
        return enemy_position.distance_to(point)

    def draw_projectiles(self, screen):
        for projectile in self.projectiles:
            position = projectile.position
            direction = projectile.target_position - projectile.start
            if direction.length_squared() > 0:
                direction = direction.normalize()
            tail = position - direction * 12

            if projectile.tower_type == "ARCHER":
                tail_point = (round(tail.x), round(tail.y))
                position_point = (round(position.x), round(position.y))
                pygame.draw.line(
                    screen, (71, 48, 31), tail_point, position_point, 5
                )
                pygame.draw.line(
                    screen, (244, 221, 174), tail_point, position_point, 2
                )
                pygame.draw.circle(
                    screen, (255, 235, 177),
                    position_point, 3
                )
            elif projectile.tower_type == "MAGE":
                center = (round(position.x), round(position.y))
                pygame.draw.circle(screen, (107, 71, 168), center, 8)
                pygame.draw.circle(screen, (229, 203, 255), center, 5)
                pygame.draw.circle(screen, (255, 247, 218), center, 2)
            else:
                center = (round(position.x), round(position.y))
                pygame.draw.line(
                    screen, (255, 137, 65),
                    (round(tail.x), round(tail.y)),
                    center,
                    7
                )
                pygame.draw.circle(screen, (61, 56, 53), center, 6)
                pygame.draw.circle(screen, (228, 199, 159), center, 3)

    def find_nearest_enemy(self, tower):

        nearest_enemy = None
        nearest_distance = float("inf")

        for enemy in self.game.enemies:

            if not enemy.alive:
                continue

            distance = self.distance(
                tower.position,
                enemy.position
            )

            if (
                distance <= tower.attack_range
                and distance < nearest_distance
            ):
                nearest_distance = distance
                nearest_enemy = enemy

        return nearest_enemy

    # ============================================================
    # ENEMY STRATEGIC COMBAT
    # ============================================================

    def enemies_take_action(self):

        commander = self.game.commander

        for enemy in self.game.enemies:

            if not enemy.alive:
                continue

            if enemy.state == "RETREATING":
                continue

            if enemy.state == "ATTACKING" or self.distance(
                enemy.position,
                self.game.castle.position
            ) <= 1:
                enemy.state = "ATTACKING"
                enemy.clear_path()
                if enemy.attack_cooldown <= 0:
                    self.enemy_attack_castle(enemy)
                    enemy.attack_cooldown = 1.6
                continue

            action = commander.choose_strategic_action(
                self.game,
                enemy
            )

            # ----------------------------------------------------
            # ATTACK CASTLE
            # ----------------------------------------------------

            if action == "ATTACK_CASTLE":

                if self.distance(
                    enemy.position,
                    self.game.castle.position
                ) == 0:

                    self.enemy_attack_castle(enemy)

            # ----------------------------------------------------
            # ATTACK TOWER
            # ----------------------------------------------------

            elif action == "ATTACK_TOWER":

                self.enemy_attack_tower(enemy)

            # ----------------------------------------------------
            # RETREAT
            # ----------------------------------------------------

            elif action == "RETREAT":

                self.enemy_retreat(enemy)

            # ----------------------------------------------------
            # CHANGE ROUTE
            # ----------------------------------------------------

            elif action == "CHANGE_ROUTE":

                commander.command_enemy(
                    self.game,
                    enemy
                )

    # ============================================================
    # ENEMY ATTACKS CASTLE
    # ============================================================

    def enemy_attack_castle(self, enemy):

        damage = enemy.damage
        if enemy.enemy_type == "CAPTAIN":
            damage = round(damage * 1.5)

        self.game.castle.take_damage(damage)
        self.game.play_sound("gate")
        self.game.screen_shake = max(
            self.game.screen_shake,
            0.18
        )
        self.game.spawn_particles(
            self.game.castle_screen_position(),
            (255, 98, 90),
            10
        )

        print(
            f"Enemy attacked castle "
            f"for {damage} damage."
        )
        enemy.state = "ATTACKING"

    # ============================================================
    # ENEMY ATTACKS TOWER
    # ============================================================

    def enemy_attack_tower(self, enemy):

        nearest_tower = self.find_nearest_tower(enemy)

        if nearest_tower is None:
            return

        distance = self.distance(
            enemy.position,
            nearest_tower.position
        )

        if distance <= self.enemy_tower_attack_range:

            # Towers do not currently have health,
            # so destroying a tower removes it.
            self.destroy_tower(nearest_tower)

            print(
                f"Enemy at {enemy.position} "
                f"destroyed tower at "
                f"{nearest_tower.position}."
            )

            return

        # If the tower is not close enough,
        # command the enemy to move toward it.
        enemy_path = self.game.commander.calculate_path(
            enemy.position,
            nearest_tower.position
        )

        if enemy_path:
            enemy.set_path(enemy_path)

    def find_nearest_tower(self, enemy):

        nearest_tower = None
        nearest_distance = float("inf")

        for tower in self.game.towers:

            distance = self.distance(
                enemy.position,
                tower.position
            )

            if distance < nearest_distance:

                nearest_distance = distance
                nearest_tower = tower

        return nearest_tower

    def destroy_tower(self, tower):

        if tower not in self.game.towers:
            return

        position = tower.position

        self.game.towers.remove(tower)

        cell = self.game.grid.get_cell(
            position[0],
            position[1]
        )

        if cell is not None:
            cell.has_tower = False

    # ============================================================
    # RETREAT
    # ============================================================

    def enemy_retreat(self, enemy):

        commander = self.game.commander
        enemy.state = "RETREATING"

        target = commander.select_retreat_target(
            self.game,
            enemy
        )

        path = commander.calculate_path(
            enemy.position,
            target
        )

        if path:

            enemy.set_path(path)
            enemy.state = "RETREATING"

            commander.current_action = "RETREAT"
            commander.current_target = target
            commander.current_path = path

    # ============================================================
    # RESET ENEMY AFTER CASTLE ATTACK
    # ============================================================

    def reset_enemy(self, enemy):

        spawn_points = self.game.grid.spawn_points

        if not spawn_points:
            return

        spawn = min(
            spawn_points,
            key=lambda point: self.distance(
                enemy.position,
                point
            )
        )

        enemy.row = float(spawn[0])
        enemy.col = float(spawn[1])

        enemy.clear_path()

        print(
            f"Enemy returned to spawn point {spawn}."
        )

    # ============================================================
    # REMOVE DEAD ENEMIES
    # ============================================================

    def remove_dead_enemies(self):

        for enemy in self.game.enemies:

            if not enemy.alive:

                self.reward_player(enemy)

    def reward_player(self, enemy):

        enemy_id = id(enemy)

        if enemy.escaped:
            self.previous_enemy_states[enemy_id] = False
            return

        if self.previous_enemy_states.get(
            enemy_id,
            True
        ) is False:
            return

        self.previous_enemy_states[enemy_id] = False

        self.game.resource_manager.reward_enemy_defeat(
            enemy.gold_reward
        )
        self.game.score += enemy.score_reward

        print(
            f"Enemy defeated! "
            f"+{enemy.gold_reward} gold."
        )

    # ============================================================
    # CLEANUP
    # ============================================================

    def cleanup_dead_enemies(self):

        self.game.enemies = [
            enemy
            for enemy in self.game.enemies
            if enemy.alive
        ]

    # ============================================================
    # STATUS
    # ============================================================

    def get_alive_enemy_count(self):

        return sum(
            1
            for enemy in self.game.enemies
            if enemy.alive
        )

    def get_tower_count(self):

        return len(self.game.towers)

    def get_status(self):

        return {
            "alive_enemies": self.get_alive_enemy_count(),
            "towers": self.get_tower_count(),
            "castle_health": self.game.castle.health,
            "castle_alive": self.game.castle.alive,
        }