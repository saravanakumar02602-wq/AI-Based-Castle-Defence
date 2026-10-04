class RuleEngine:
    """
    Classical AI rule-based decision system.

    Uses IF-THEN rules to determine the enemy's
    strategic action.
    """

    def __init__(self):
        self.last_rule = "NONE"

    def evaluate(self, game_state):
        """
        Evaluate the current game state and return
        the best rule-based action.
        """

        castle_health = game_state.get(
            "castle_health",
            100
        )

        enemy_health = game_state.get(
            "enemy_health",
            100
        )

        route_blocked = game_state.get(
            "route_blocked",
            False
        )

        tower_nearby = game_state.get(
            "tower_nearby",
            False
        )

        distance_to_castle = game_state.get(
            "distance_to_castle",
            999
        )

        # Rule 1:
        # IF enemy health is very low
        # THEN retreat.
        if enemy_health <= 20:
            self.last_rule = (
                "IF enemy health <= 20 "
                "THEN RETREAT"
            )
            return "RETREAT"

        # Rule 2:
        # IF route is blocked
        # THEN change route.
        if route_blocked:
            self.last_rule = (
                "IF route is blocked "
                "THEN CHANGE_ROUTE"
            )
            return "CHANGE_ROUTE"

        # Rule 3:
        # IF tower is nearby
        # THEN attack tower.
        if tower_nearby:
            self.last_rule = (
                "IF tower is nearby "
                "THEN ATTACK_TOWER"
            )
            return "ATTACK_TOWER"

        # Rule 4:
        # IF castle is weak and enemy is close
        # THEN attack castle.
        if (
            castle_health < 30
            and distance_to_castle <= 3
        ):
            self.last_rule = (
                "IF castle health < 30 "
                "AND enemy is close "
                "THEN ATTACK_CASTLE"
            )
            return "ATTACK_CASTLE"

        # Rule 5:
        # IF enemy is close to castle
        # THEN attack castle.
        if distance_to_castle <= 2:
            self.last_rule = (
                "IF enemy is close "
                "THEN ATTACK_CASTLE"
            )
            return "ATTACK_CASTLE"

        # Rule 6:
        # Otherwise move toward castle.
        self.last_rule = (
            "IF no higher priority rule applies "
            "THEN MOVE_TO_CASTLE"
        )

        return "MOVE_TO_CASTLE"

    def get_last_rule(self):
        """
        Return the rule activated during the
        last decision.
        """

        return self.last_rule

    def reset(self):
        """
        Reset the rule engine.
        """

        self.last_rule = "NONE"