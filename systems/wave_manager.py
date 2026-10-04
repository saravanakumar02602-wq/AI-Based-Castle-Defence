from entities.enemy import Enemy


class WaveManager:
    def __init__(self, game):
        self.game = game

        self.current_wave = 1
        self.enemies_per_wave = 6

        self.spawned_this_wave = 0
        self.defeated_this_wave = 0

        self.spawn_timer = 0.0
        self.spawn_delay = 1.7
        self.preparation_duration = self.get_preparation_duration()
        self.preparation_remaining = self.preparation_duration

        self.wave_complete = False
        self.started = False
        self.bonus_pending = False

    def update(self, delta_time):
        if not self.game.castle.alive:
            return

        if not self.started or self.bonus_pending:
            if self.bonus_pending:
                return

            self.preparation_remaining = max(
                0.0,
                self.preparation_remaining - delta_time
            )
            if self.preparation_remaining <= 0:
                self.start_wave()
            return

        # Spawn enemies
        if self.spawned_this_wave < self.enemies_per_wave:
            self.spawn_timer += delta_time

            if self.spawn_timer >= self.spawn_delay:
                self.spawn_enemy()
                self.spawn_timer = 0.0

        self.check_wave_complete()

    def start_wave(self):
        if self.started or self.bonus_pending or self.wave_complete:
            return False

        self.started = True
        self.preparation_remaining = 0.0
        self.spawn_timer = 0.0
        return True

    def spawn_enemy(self):
        spawn_points = self.game.grid.spawn_points

        if not spawn_points:
            return

        early_wave = min(self.current_wave, 8)
        is_captain = (
            self.current_wave >= 3
            and self.spawned_this_wave > 0
            and self.spawned_this_wave % (
                5 if self.current_wave <= 8
                else 3 if self.current_wave > 15
                else 4
            ) == 0
        )
        enemy_type = "CAPTAIN" if is_captain else "REGULAR"
        late_wave_levels = max(0, self.current_wave - 8)
        veteran_wave_levels = max(0, self.current_wave - 15)
        if is_captain:
            health = (
                82 + early_wave * 3
                + late_wave_levels * 14
                + veteran_wave_levels * 12
            )
        else:
            health = (
                42 + early_wave * 3
                + late_wave_levels * 10
                + veteran_wave_levels * 8
            )

        spawn_position = self.game.commander.choose_spawn_point(
            self.game,
            health
        )

        if spawn_position is None:
            self.game.show_notice("No viable route to the keep remains.")
            return

        enemy = Enemy(
            spawn_position,
            health=health,
            enemy_type=enemy_type
        )
        enemy.ward_strength = min(0.45, veteran_wave_levels * 0.12)

        enemy.damage = (
            8 + early_wave // 4 + late_wave_levels + veteran_wave_levels
            if is_captain
            else 4 + early_wave // 4 + late_wave_levels + veteran_wave_levels
        )
        enemy.speed = (
            1.1 + early_wave * 0.025 + late_wave_levels * 0.035
            + veteran_wave_levels * 0.03
            if is_captain
            else 1.25 + early_wave * 0.025 + late_wave_levels * 0.04
            + veteran_wave_levels * 0.025
        )

        self.game.enemies.append(enemy)

        self.spawned_this_wave += 1

        # Let the AI Commander make the first decision.
        self.game.commander.command_enemy(
            self.game,
            enemy
        )

        # Give the enemy the path selected by the commander.
        enemy.set_path(
            self.game.commander.get_current_path()
        )

    def check_wave_complete(self):
        if self.wave_complete:
            return

        if self.spawned_this_wave < self.enemies_per_wave:
            return

        living_enemies = sum(
            1
            for enemy in self.game.enemies
            if enemy.alive
        )

        if living_enemies == 0:
            self.wave_complete = True
            self.started = False
            self.bonus_pending = True
            self.game.resource_manager.reward_wave_completion()
            self.game.score += 250

    def start_next_wave(self):
        if not self.bonus_pending:
            return False

        self.current_wave += 1

        self.spawned_this_wave = 0
        self.defeated_this_wave = 0

        self.spawn_timer = 0.0

        self.wave_complete = False
        self.bonus_pending = False
        self.started = False
        self.preparation_duration = max(
            6.0,
            12.0 - (self.current_wave - 1) * 0.5
        )
        self.preparation_remaining = self.preparation_duration

        early_wave_count = 6 + min(self.current_wave - 1, 7)
        late_wave_count = max(0, self.current_wave - 8) * 2
        veteran_wave_levels = max(0, self.current_wave - 15)
        self.enemies_per_wave = (
            early_wave_count + late_wave_count
            + veteran_wave_levels * 3
        )

        early_spawn_delay = 1.7 - min(self.current_wave - 1, 7) * 0.035
        late_spawn_delay = max(0, self.current_wave - 8) * 0.04
        veteran_spawn_reduction = veteran_wave_levels * 0.06
        self.spawn_delay = max(
            0.65,
            early_spawn_delay - late_spawn_delay - veteran_spawn_reduction
        )
        self.preparation_duration = self.get_preparation_duration()
        self.preparation_remaining = self.preparation_duration
        return True

    def get_preparation_duration(self):
        later_wave_levels = max(0, self.current_wave - 8)
        veteran_wave_levels = max(0, self.current_wave - 15)
        return max(
            6.0,
            12.0 - later_wave_levels * 0.5 - veteran_wave_levels * 0.35
        )

    def get_wave(self):
        return self.current_wave

    def get_wave_progress(self):
        return (
            self.spawned_this_wave,
            self.enemies_per_wave
        )

    def is_wave_complete(self):
        return self.wave_complete