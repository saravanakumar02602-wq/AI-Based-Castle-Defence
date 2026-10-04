class KnowledgeBase:
    """
    Classical AI Knowledge Representation.

    Stores facts about the current battlefield that
    the AI Commander can reason about.
    """

    def __init__(self):
        self.facts = {}

    def set_fact(self, name, value):
        """Add or update a fact."""
        self.facts[name] = value

    def get_fact(self, name, default=None):
        """Retrieve a fact."""
        return self.facts.get(name, default)

    def has_fact(self, name):
        """Check whether a fact exists."""
        return name in self.facts

    def remove_fact(self, name):
        """Remove a fact."""
        if name in self.facts:
            del self.facts[name]

    def get_all_facts(self):
        """Return all known facts."""
        return self.facts.copy()

    def update_from_game(self, game):
        """
        Build the AI's knowledge from the current game state.
        """

        # Castle information
        self.set_fact(
            "castle_position",
            game.castle.position
        )

        self.set_fact(
            "castle_health",
            game.castle.health
        )

        self.set_fact(
            "castle_alive",
            game.castle.alive
        )

        # Enemy information
        enemy_positions = []

        for enemy in game.enemies:

            if enemy.alive:
                enemy_positions.append(
                    enemy.position
                )

        self.set_fact(
            "enemy_positions",
            enemy_positions
        )

        self.set_fact(
            "enemy_count",
            len(enemy_positions)
        )

        # Battlefield information
        self.set_fact(
            "spawn_points",
            game.grid.spawn_points
        )

        self.set_fact(
            "blocked_cells",
            self.get_blocked_cells(game)
        )

    def get_blocked_cells(self, game):
        """Return all blocked battlefield cells."""

        blocked = []

        for row in range(game.grid.rows):

            for col in range(game.grid.cols):

                cell = game.grid.get_cell(
                    row,
                    col
                )

                if cell.blocked:
                    blocked.append(
                        (row, col)
                    )

        return blocked

    def describe(self):
        """
        Return a readable description of the
        AI's current knowledge.
        """

        return {
            "Castle": self.get_fact("castle_position"),
            "Castle HP": self.get_fact("castle_health"),
            "Enemies": self.get_fact("enemy_count"),
            "Enemy Positions": self.get_fact("enemy_positions"),
            "Spawn Points": self.get_fact("spawn_points"),
            "Blocked Cells": self.get_fact("blocked_cells"),
        }