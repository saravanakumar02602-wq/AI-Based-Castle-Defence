class GameState:
    """
    Represents one possible state of the enemy/castle situation.

    Used by Minimax and Alpha-Beta pruning.
    """

    def __init__(
        self,
        castle_health,
        enemy_position,
        enemy_health,
        target,
        distance_to_castle=None,
        tower_nearby=False,
    ):
        self.castle_health = castle_health
        self.enemy_position = enemy_position
        self.enemy_health = enemy_health
        self.target = target

        self.distance_to_castle = (
            distance_to_castle
            if distance_to_castle is not None
            else 0
        )

        self.tower_nearby = tower_nearby

    def copy(self):
        return GameState(
            castle_health=self.castle_health,
            enemy_position=self.enemy_position,
            enemy_health=self.enemy_health,
            target=self.target,
            distance_to_castle=self.distance_to_castle,
            tower_nearby=self.tower_nearby,
        )

    def is_terminal(self):
        return (
            self.castle_health <= 0
            or self.enemy_health <= 0
        )

    def __repr__(self):
        return (
            "GameState("
            f"castle_health={self.castle_health}, "
            f"enemy_position={self.enemy_position}, "
            f"enemy_health={self.enemy_health}, "
            f"target={self.target}, "
            f"distance_to_castle={self.distance_to_castle}, "
            f"tower_nearby={self.tower_nearby}"
            ")"
        )


class StateSpace:
    """
    Generates possible actions and successor states.

    This is the state-space representation used by
    Minimax and Alpha-Beta pruning.
    """

    ACTIONS = [
        "ATTACK_CASTLE",
        "MOVE_TO_CASTLE",
        "CHANGE_ROUTE",
        "ATTACK_TOWER",
        "RETREAT",
    ]

    def __init__(self):
        self.actions = self.ACTIONS.copy()

    # ============================================================
    # POSSIBLE ACTIONS
    # ============================================================

    def get_possible_actions(self, state):

        if state.is_terminal():
            return []

        return self.actions.copy()

    # ============================================================
    # APPLY ACTION
    # ============================================================

    def apply_action(self, state, action):

        new_state = state.copy()

        if action == "ATTACK_CASTLE":

            new_state.castle_health -= 10

            new_state.distance_to_castle = max(
                0,
                new_state.distance_to_castle - 1
            )

        elif action == "MOVE_TO_CASTLE":

            new_state.distance_to_castle = max(
                0,
                new_state.distance_to_castle - 2
            )

        elif action == "CHANGE_ROUTE":

            new_state.target = "ALTERNATE_ROUTE"

            new_state.distance_to_castle = max(
                0,
                new_state.distance_to_castle - 1
            )

        elif action == "ATTACK_TOWER":

            new_state.enemy_health -= 5

            new_state.tower_nearby = False

        elif action == "RETREAT":

            new_state.target = "RETREAT"

            new_state.distance_to_castle += 3

        return new_state

    # ============================================================
    # SUCCESSORS
    # ============================================================

    def generate_successors(self, state):

        successors = []

        for action in self.get_possible_actions(state):

            next_state = self.apply_action(
                state,
                action
            )

            successors.append(
                (action, next_state)
            )

        return successors