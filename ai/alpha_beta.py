from ai.state_space import StateSpace


class AlphaBeta:
    """
    Classical Alpha-Beta pruning.

    Alpha-Beta produces the same strategic result as
    Minimax while eliminating branches that cannot
    influence the final decision.
    """

    def __init__(self, depth=3):

        self.depth = depth
        self.state_space = StateSpace()

        self.nodes_visited = 0
        self.nodes_pruned = 0

        self.action_scores = {}

    # ============================================================
    # HEURISTIC EVALUATION
    # ============================================================

    def evaluate_state(self, state):

        score = 0.0

        # Enemy survival
        score += state.enemy_health * 2

        # Castle weakness
        score += (100 - state.castle_health) * 3

        # Distance to castle
        score -= state.distance_to_castle * 8

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
    # ALPHA-BETA SEARCH
    # ============================================================

    def alpha_beta(
        self,
        state,
        depth,
        alpha,
        beta,
        maximizing_player
    ):

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

                value = self.alpha_beta(
                    child_state,
                    depth - 1,
                    alpha,
                    beta,
                    False
                )

                best_value = max(
                    best_value,
                    value
                )

                alpha = max(
                    alpha,
                    best_value
                )

                # ------------------------------------------------
                # PRUNING
                # ------------------------------------------------

                if beta <= alpha:

                    self.nodes_pruned += 1

                    break

            return best_value

        # --------------------------------------------------------
        # MIN PLAYER
        # --------------------------------------------------------

        best_value = float("inf")

        for _, child_state in successors:

            value = self.alpha_beta(
                child_state,
                depth - 1,
                alpha,
                beta,
                True
            )

            best_value = min(
                best_value,
                value
            )

            beta = min(
                beta,
                best_value
            )

            # ----------------------------------------------------
            # PRUNING
            # ----------------------------------------------------

            if beta <= alpha:

                self.nodes_pruned += 1

                break

        return best_value

    # ============================================================
    # CHOOSE ACTION
    # ============================================================

    def choose_action(self, state):

        self.nodes_visited = 0
        self.nodes_pruned = 0
        self.action_scores = {}

        successors = self.state_space.generate_successors(
            state
        )

        if not successors:
            return "MOVE_TO_CASTLE"

        best_action = "MOVE_TO_CASTLE"
        best_value = float("-inf")

        alpha = float("-inf")
        beta = float("inf")

        for action, child_state in successors:

            value = self.alpha_beta(
                child_state,
                self.depth - 1,
                alpha,
                beta,
                False
            )

            self.action_scores[action] = value

            if value > best_value:

                best_value = value
                best_action = action

            alpha = max(
                alpha,
                best_value
            )

        return best_action

    # ============================================================
    # STATISTICS
    # ============================================================

    def get_statistics(self):

        return {
            "nodes_visited": self.nodes_visited,
            "nodes_pruned": self.nodes_pruned,
        }

    def get_action_scores(self):

        return self.action_scores.copy()

    def get_nodes_visited(self):

        return self.nodes_visited

    def get_nodes_pruned(self):

        return self.nodes_pruned