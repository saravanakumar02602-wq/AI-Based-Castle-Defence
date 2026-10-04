from ai.knowledge import KnowledgeBase
from ai.rules import RuleEngine
from ai.minimax import Minimax
from ai.alpha_beta import AlphaBeta
from ai.astar import AStar
from ai.state_space import GameState


class AICommander:
    """
    Classical AI Enemy Commander.

    Decision pipeline:

        Knowledge Base
              ↓
        Rule Engine
              ↓
        Minimax / Alpha-Beta
              ↓
        A* Pathfinding
              ↓
        Enemy Action

    Dynamic behaviour:

        Player changes battlefield
              ↓
        Detect blocked-cell change
              ↓
        Recalculate A* paths
              ↓
        Enemies follow new route

    No machine learning is used.
    """

    def __init__(self, game):

        self.game = game

        # =============================================
        # CLASSICAL AI COMPONENTS
        # =============================================

        self.knowledge = KnowledgeBase()

        self.rules = RuleEngine()

        self.minimax = Minimax(depth=3)

        self.alpha_beta = AlphaBeta(depth=3)

        # A* requires the Grid.
        self.astar = AStar(game.grid)

        # =============================================
        # CURRENT AI STATE
        # =============================================

        self.strategy = "CLASSICAL AI"

        self.current_action = "NONE"

        self.current_target = None

        self.current_path = []

        self.last_rule = "NONE"

        self.decision_count = 0

        self.alpha_beta_nodes = 0

        self.alpha_beta_pruned = 0

        # =============================================
        # DYNAMIC REPLANNING
        # =============================================

        self.replanning = False

        self.replan_count = 0

        self.previous_blocked_cells = set()

        self.recent_decisions = []

    # =================================================
    # KNOWLEDGE BASE
    # =================================================

    def update_knowledge(self, game):

        self.knowledge.update_from_game(game)

    # =================================================
    # DISTANCE
    # =================================================

    def get_distance(self, start, goal):

        return (
            abs(start[0] - goal[0])
            +
            abs(start[1] - goal[1])
        )

    # =================================================
    # TOWER DETECTION
    # =================================================

    def is_tower_nearby(self, game, enemy):

        for tower in game.towers:

            distance = self.get_distance(
                enemy.position,
                tower.position
            )

            if distance <= 3:
                return True

        return False

    # =================================================
    # ROUTE BLOCK CHECK
    # =================================================

    def is_route_blocked(self, game, enemy):

        if not enemy.path:
            return False

        for position in enemy.path:

            cell = game.grid.get_cell(
                position[0],
                position[1]
            )

            if cell is None:
                return True

            if not cell.walkable:
                return True

        return False

    # =================================================
    # BUILD STATE
    # =================================================

    def build_state(self, game, enemy):

        distance_to_castle = self.get_distance(
            enemy.position,
            game.castle.position
        )

        tower_nearby = self.is_tower_nearby(
            game,
            enemy
        )

        return GameState(
            castle_health=game.castle.health,
            enemy_position=enemy.position,
            enemy_health=enemy.health,
            target=game.castle.position,
            distance_to_castle=distance_to_castle,
            tower_nearby=tower_nearby
        )

    # =================================================
    # STRATEGIC DECISION
    # =================================================

    def choose_strategic_action(self, game, enemy):

        self.update_knowledge(game)

        state = self.build_state(
            game,
            enemy
        )

        distance_to_castle = (
            state.distance_to_castle
        )

        tower_nearby = (
            state.tower_nearby
        )

        route_blocked = (
            self.is_route_blocked(
                game,
                enemy
            )
        )

        # ---------------------------------------------
        # RULE ENGINE
        # ---------------------------------------------

        rule_state = {
            "castle_health":
                game.castle.health,

            "enemy_health":
                enemy.health,

            "route_blocked":
                route_blocked,

            "tower_nearby":
                tower_nearby,

            "distance_to_castle":
                distance_to_castle,
        }

        rule_action = self.rules.evaluate(
            rule_state
        )

        self.last_rule = (
            self.rules.get_last_rule()
        )

        # ---------------------------------------------
        # IMMEDIATE RULE ACTIONS
        # ---------------------------------------------

        immediate_actions = {
            "RETREAT",
            "CHANGE_ROUTE",
            "ATTACK_TOWER",
            "ATTACK_CASTLE"
        }

        if rule_action in immediate_actions:

            self.strategy = "RULE-BASED AI"

            self.current_action = rule_action

            self.decision_count += 1

            self.record_decision(
                f"RULE → {rule_action}"
            )

            return rule_action

        # ---------------------------------------------
        # ALPHA-BETA
        # ---------------------------------------------

        action = self.alpha_beta.choose_action(
            state
        )

        statistics = (
            self.alpha_beta.get_statistics()
        )

        self.alpha_beta_nodes = (
            statistics["nodes_visited"]
        )

        self.alpha_beta_pruned = (
            statistics["nodes_pruned"]
        )

        self.strategy = "ALPHA-BETA"

        self.current_action = action

        self.decision_count += 1

        self.record_decision(
            f"ALPHA-BETA → {action}"
        )

        return action

    # =================================================
    # COMMAND ENEMY
    # =================================================

    def command_enemy(self, game, enemy):

        if not enemy.alive:
            return []

        # Always make sure A* has the latest grid.
        self.astar.grid = game.grid

        action = self.choose_strategic_action(
            game,
            enemy
        )

        # ---------------------------------------------
        # DEFAULT TARGET
        # ---------------------------------------------

        target = self.choose_gate_target(
            game,
            enemy.position,
            enemy.health
        ) or game.castle.position

        # ---------------------------------------------
        # ATTACK TOWER
        # ---------------------------------------------

        if action == "ATTACK_TOWER":

            tower = self.find_nearest_tower(
                game,
                enemy
            )

            if tower is not None:

                target = tower.position

        # ---------------------------------------------
        # RETREAT
        # ---------------------------------------------

        elif action == "RETREAT":

            enemy.state = "RETREATING"
            target = self.select_retreat_target(
                game,
                enemy
            )

        # ---------------------------------------------
        # CHANGE ROUTE
        # ---------------------------------------------

        elif action == "CHANGE_ROUTE":

            target = self.choose_gate_target(
                game,
                enemy.position,
                enemy.health
            ) or game.castle.position

        # ---------------------------------------------
        # ATTACK CASTLE
        # ---------------------------------------------

        elif action == "ATTACK_CASTLE":

            target = self.choose_gate_target(
                game,
                enemy.position,
                enemy.health
            ) or game.castle.position

        # ---------------------------------------------
        # A* SEARCH
        # ---------------------------------------------

        path = self.calculate_path(
            enemy.position,
            target
        )

        self.current_target = target

        self.current_path = path

        enemy.set_path(path)

        return path

    # =================================================
    # CALCULATE A* PATH
    # =================================================

    def calculate_path(self, start, target):

        self.astar.grid = self.game.grid

        path = self.astar.find_path(
            start,
            target
        )

        return path

    # =================================================
    # FIND NEAREST TOWER
    # =================================================

    def find_nearest_tower(self, game, enemy):

        if not game.towers:
            return None

        return min(
            game.towers,
            key=lambda tower:
                self.get_distance(
                    enemy.position,
                    tower.position
                )
        )

    # =================================================
    # RETREAT TARGET
    # =================================================

    def select_retreat_target(self, game, enemy):

        if not game.grid.spawn_points:
            return enemy.position

        self.astar.grid = game.grid
        reachable = []
        for position in game.grid.spawn_points:
            path = self.astar.find_path(enemy.position, position)
            if path:
                reachable.append((len(path), position))

        return min(reachable)[1] if reachable else enemy.position

    # =================================================
    # GET BLOCKED CELLS
    # =================================================

    def get_blocked_cells(self, game):

        blocked = set()

        for row in range(game.grid.rows):

            for col in range(game.grid.cols):

                cell = game.grid.get_cell(
                    row,
                    col
                )

                if cell.blocked or cell.has_tower:

                    blocked.add(
                        (row, col)
                    )

        return blocked

    def choose_spawn_point(self, game, enemy_health):
        """Use depth-two Minimax to prefer a safer reachable entry."""
        self.astar.grid = game.grid
        candidates = []

        for spawn in game.grid.spawn_points:
            gate = self.choose_gate_target(
                game,
                spawn,
                enemy_health
            )
            if gate is None:
                continue

            path = self.astar.find_path(spawn, gate)
            exposure = self.get_path_tower_exposure(game, path)
            state = GameState(
                castle_health=game.castle.health,
                enemy_position=spawn,
                enemy_health=max(1, enemy_health - exposure * 0.2),
                target=gate,
                distance_to_castle=len(path),
                tower_nearby=exposure > 0,
            )
            score = self.minimax.minimax(
                state,
                depth=2,
                maximizing_player=True
            ) - exposure
            candidates.append((score, spawn))

        if not candidates:
            return None

        return max(candidates, key=lambda candidate: candidate[0])[1]

    def choose_gate_target(self, game, start, enemy_health):
        """Choose the least-defended reachable gate using depth-two Minimax."""
        self.astar.grid = game.grid
        candidates = []

        for gate in game.grid.castle_gate_positions:
            path = self.astar.find_path(start, gate)
            if not path:
                continue

            exposure = self.get_path_tower_exposure(game, path)
            state = GameState(
                castle_health=game.castle.health,
                enemy_position=start,
                enemy_health=max(1, enemy_health - exposure * 0.2),
                target=gate,
                distance_to_castle=len(path),
                tower_nearby=exposure > 0,
            )
            score = self.minimax.minimax(
                state,
                depth=2,
                maximizing_player=True
            ) - exposure
            candidates.append((score, gate))

        return max(candidates, key=lambda candidate: candidate[0])[1] if candidates else None

    def get_path_tower_exposure(self, game, path):
        exposure = 0.0
        for position in path:
            for tower in game.towers:
                if tower.is_enemy_in_range(position):
                    exposure += (
                        tower.damage / max(1, tower.attack_cooldown)
                    ) * 0.2
        return exposure

    # =================================================
    # DETECT BATTLEFIELD CHANGE
    # =================================================

    def battlefield_changed(self, game):

        current_blocked = (
            self.get_blocked_cells(game)
        )

        # First observation.
        if not self.previous_blocked_cells:

            self.previous_blocked_cells = (
                current_blocked.copy()
            )

            return False

        changed = (
            current_blocked
            != self.previous_blocked_cells
        )

        if changed:

            added = (
                current_blocked
                - self.previous_blocked_cells
            )

            removed = (
                self.previous_blocked_cells
                - current_blocked
            )

            if added:

                print(
                    f"AI: New obstacles detected: "
                    f"{sorted(added)}"
                )

            if removed:

                print(
                    f"AI: Obstacles removed: "
                    f"{sorted(removed)}"
                )

        self.previous_blocked_cells = (
            current_blocked.copy()
        )

        return changed

    # =================================================
    # DYNAMIC A* REPLANNING
    # =================================================

    def recalculate_all_paths(self, game):

        self.replanning = True

        self.replan_count += 1

        self.strategy = "DYNAMIC A*"

        self.current_action = "REPLANNING"

        self.record_decision(
            "BATTLEFIELD CHANGED → REPLANNING"
        )

        print()
        print("========================================")
        print("AI COMMANDER: BATTLEFIELD CHANGED")
        print("AI COMMANDER: STARTING DYNAMIC A*")
        print("========================================")

        # Make sure A* uses current Grid.
        self.astar.grid = game.grid

        for enemy in game.enemies:

            if not enemy.alive:
                continue

            old_path = enemy.path.copy()

            new_path = self.calculate_path(
                enemy.position,
                game.castle.position
            )

            enemy.set_path(
                new_path
            )

            # Keep the most recently
            # calculated path visible.
            self.current_path = (
                new_path.copy()
            )

            self.current_target = (
                game.castle.position
            )

            print(
                f"Enemy {enemy.position}: "
                f"path {len(old_path)} → "
                f"{len(new_path)} cells"
            )

        print(
            "AI COMMANDER: REPLANNING COMPLETE"
        )

        print("========================================")
        print()

        self.replanning = False

    # =================================================
    # MAIN AI UPDATE
    # =================================================

    def update(self, game):

        self.game = game

        # A* always uses the current battlefield.
        self.astar.grid = game.grid

        # Update Knowledge Base.
        self.update_knowledge(game)

        # ---------------------------------------------
        # Detect player-created walls.
        # ---------------------------------------------

        if self.battlefield_changed(game):

            self.recalculate_all_paths(
                game
            )

        # ---------------------------------------------
        # Give a path to new enemies.
        # ---------------------------------------------

        for enemy in game.enemies:

            if not enemy.alive:
                continue

            if enemy.state in {"RETREATING", "ATTACKING"}:
                continue

            if not enemy.path:

                self.command_enemy(
                    game,
                    enemy
                )

            elif (
                enemy.path_index
                >= len(enemy.path)
            ):

                self.command_enemy(
                    game,
                    enemy
                )

    # =================================================
    # DECISION HISTORY
    # =================================================

    def record_decision(self, decision):

        self.recent_decisions.append(
            decision
        )

        if len(
            self.recent_decisions
        ) > 8:

            self.recent_decisions.pop(0)

    # =================================================
    # CURRENT PATH
    # =================================================

    def get_current_path(self):

        return self.current_path.copy()

    # =================================================
    # STATUS
    # =================================================

    def get_ai_status(self):

        return {
            "strategy": self.strategy,

            "action": self.current_action,

            "target": self.current_target,

            "path_length": len(
                self.current_path
            ),

            "last_rule": self.last_rule,

            # Keep both names for compatibility.
            "decision_count": self.decision_count,
            "decisions": self.decision_count,

            "alpha_beta_nodes":
                self.alpha_beta_nodes,

            "alpha_beta_pruned":
                self.alpha_beta_pruned,

            "replanning":
                self.replanning,

            "replan_count":
                self.replan_count,

            "recent_decisions":
                self.recent_decisions.copy()
        }