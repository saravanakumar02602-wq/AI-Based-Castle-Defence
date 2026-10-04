from ai.state_space import StateSpace


class Minimax:
    """
    Classical Minimax search.

    The enemy is treated as the maximizing player.
    The opposing side is represented by the minimizing
    response.

    This is deterministic classical AI.
    No machine learning is used.
    """

    def __init__(self, depth=3):

        self.depth = depth
        self.state_space = StateSpace()

        self.nodes_visited = 0
        self.action_scores = {}

    # ============================================================
    # EVALUATION FUNCTION
    # ============================================================

    def evaluate_state(self, state):
        """
        Higher score = better for the enemy.

        Positive factors:
            - Castle has low health
            - Enemy has high health
            - Enemy is close to castle

        Negative factors:
            - Enemy has low health
            - Enemy is far from castle
        """

        score = 0.0

        # Enemy survival
        score += state.enemy_health * 2

        # Enemy proximity
        score -= state.distance_to_castle * 8

        # Castle weakness
        score += (100 - state.castle_health) * 3

        # Tower danger
        if state.tower_nearby:
            score -= 25

        # Terminal states
        if state.castle_health <= 0:
            score += 1000

        if state.enemy_health <= 0:
            score -= 1000

        return score

    # ============================================================
    # MINIMAX
    # ============================================================

    def minimax(self, state, depth, maximizing_player):

        self.nodes_visited += 1

        if depth == 0 or state.is_terminal():
            return self.evaluate_state(state)

        successors = self.state_space.generate_successors(
            state
        )

        if not successors:
            return self.evaluate_state(state)

        # --------------------------------------------------------
        # MAX PLAYER
        # --------------------------------------------------------

        if maximizing_player:

            best_value = float("-inf")

            for _, child_state in successors:

                value = self.minimax(
                    child_state,
                    depth - 1,
                    False
                )

                best_value = max(
                    best_value,
                    value
                )

            return best_value

        # --------------------------------------------------------
        # MIN PLAYER
        # --------------------------------------------------------

        best_value = float("inf")

        for _, child_state in successors:

            value = self.minimax(
                child_state,
                depth - 1,
                True
            )

            best_value = min(
                best_value,
                value
            )

        return best_value

    # ============================================================
    # CHOOSE ACTION
    # ============================================================

    def choose_action(self, state):

        self.nodes_visited = 0
        self.action_scores = {}

        successors = self.state_space.generate_successors(
            state
        )

        if not successors:
            return "MOVE_TO_CASTLE"

        best_action = "MOVE_TO_CASTLE"
        best_value = float("-inf")

        for action, child_state in successors:

            value = self.minimax(
                child_state,
                self.depth - 1,
                False
            )

            self.action_scores[action] = value

            if value > best_value:

                best_value = value
                best_action = action

        return best_action

    # ============================================================
    # STATUS
    # ============================================================

    def get_action_scores(self):
        return self.action_scores.copy()

    def get_nodes_visited(self):
        return self.nodes_visited