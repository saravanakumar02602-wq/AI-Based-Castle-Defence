class GameStateManager:
    """
    Controls the overall state of the castle defence game.

    Possible states:
        PLAYING
        VICTORY
        GAME_OVER
    """

    PLAYING = "PLAYING"
    VICTORY = "VICTORY"
    GAME_OVER = "GAME_OVER"

    def __init__(self, game):
        self.game = game

        self.state = self.PLAYING

        self.final_wave = None

        self.message = ""
        self.restart_requested = False

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def update(self):

        # Do not change the state once the game has ended.
        if self.state != self.PLAYING:
            return

        # -----------------------------------------------------
        # GAME OVER
        # -----------------------------------------------------

        if not self.game.castle.alive:
            self.state = self.GAME_OVER
            self.message = "The keep has fallen."

            print("GAME OVER")
            return

        # -----------------------------------------------------
        # VICTORY
        # -----------------------------------------------------

        wave_manager = self.game.wave_manager

        if (
            self.final_wave is not None
            and wave_manager.current_wave >= self.final_wave
            and wave_manager.wave_complete
        ):
            self.state = self.VICTORY
            self.message = "The realm has been secured."

            print("VICTORY")
            return

    # ---------------------------------------------------------
    # GAME STATE
    # ---------------------------------------------------------

    def is_playing(self):
        return self.state == self.PLAYING

    def is_game_over(self):
        return self.state == self.GAME_OVER

    def is_victory(self):
        return self.state == self.VICTORY

    # ---------------------------------------------------------
    # RESTART
    # ---------------------------------------------------------

    def request_restart(self):
        self.restart_requested = True

    def should_restart(self):
        return self.restart_requested

    def reset_restart_request(self):
        self.restart_requested = False

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    def get_state(self):
        return {
            "game_state": self.state,
            "message": self.message,
            "castle_health": self.game.castle.health,
            "castle_alive": self.game.castle.alive,
            "wave": self.game.wave_manager.get_wave(),
            "gold": self.game.resource_manager.get_gold(),
            "enemy_count": self.get_living_enemy_count(),
            "tower_count": len(self.game.towers),
            "wall_count": self.get_wall_count(),
            "blocked_cells": self.get_blocked_cells(),
        }

    # ---------------------------------------------------------
    # ENEMY INFORMATION
    # ---------------------------------------------------------

    def get_living_enemies(self):

        return [
            enemy
            for enemy in self.game.enemies
            if enemy.alive
        ]

    def get_living_enemy_count(self):

        return len(
            self.get_living_enemies()
        )

    # ---------------------------------------------------------
    # TOWER INFORMATION
    # ---------------------------------------------------------

    def get_towers(self):

        return self.game.towers

    def get_tower_count(self):

        return len(
            self.game.towers
        )

    # ---------------------------------------------------------
    # WALL INFORMATION
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
    # BLOCKED CELLS
    # ---------------------------------------------------------

    def get_blocked_cells(self):

        blocked = []

        for row in range(self.game.grid.rows):

            for col in range(self.game.grid.cols):

                cell = self.game.grid.get_cell(
                    row,
                    col
                )

                if cell.blocked:
                    blocked.append(
                        (row, col)
                    )

        return blocked

    # ---------------------------------------------------------
    # ENEMY STATE
    # ---------------------------------------------------------

    def get_enemy_state(self, enemy):

        return {
            "position": enemy.position,
            "health": enemy.health,
            "alive": enemy.alive,
            "damage": enemy.damage,
            "speed": enemy.speed,
            "target": self.game.castle.position,
        }

    # ---------------------------------------------------------
    # AI STATE
    # ---------------------------------------------------------

    def get_ai_state(self):

        commander = self.game.commander

        return {
            "strategy": commander.strategy,
            "action": commander.current_action,
            "target": commander.current_target,
            "path_length": len(
                commander.current_path
            ),
            "rule": commander.last_rule,
            "decisions": commander.decision_count,
            "alpha_beta_nodes":
                commander.alpha_beta_nodes,
            "alpha_beta_pruned":
                commander.alpha_beta_pruned,
        }

    # ---------------------------------------------------------
    # DESCRIPTION
    # ---------------------------------------------------------

    def describe(self):

        state = self.get_state()

        return {
            "Game State":
                state["game_state"],

            "Castle HP":
                state["castle_health"],

            "Castle Alive":
                state["castle_alive"],

            "Wave":
                state["wave"],

            "Gold":
                state["gold"],

            "Living Enemies":
                state["enemy_count"],

            "Towers":
                state["tower_count"],

            "Walls":
                state["wall_count"],

            "Blocked Cells":
                len(state["blocked_cells"]),
        }