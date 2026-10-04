from entities.tower import Tower


class TowerManager:
    """
    Manages tower placement, removal, and upgrades.

    Classical AI is not replaced here:
    towers are the player's defensive structures,
    while the AI Commander decides how enemies respond.
    """

    def __init__(self, game):
        self.game = game

    # --------------------------------------------------
    # TOWER PLACEMENT
    # --------------------------------------------------

    def place_tower(self, row, col):
        tower_type = self.game.selected_tower_type
        tower_specs = {
            "ARCHER": (100, 20, 3),
            "MAGE": (175, 12, 3),
            "CANNON": (250, 42, 2),
        }
        cost, damage, attack_range = tower_specs.get(
            tower_type,
            tower_specs["ARCHER"]
        )

        cell = self.game.grid.get_cell(row, col)

        if cell is None:
            return False

        if cell.blocked:
            return False

        if cell.is_castle:
            return False

        if cell.is_spawn:
            return False

        if cell.has_tower:
            return False

        # Do not allow building directly on an enemy.
        if self.is_enemy_on_cell(row, col):
            return False

        cell.has_tower = True
        has_route = any(
            self.game.commander.astar.find_path(
                spawn,
                self.game.castle.position
            )
            for spawn in self.game.grid.spawn_points
        )
        cell.has_tower = False

        if not has_route:
            return False

        if not self.game.resource_manager.can_afford(cost):
            return False

        if not self.game.resource_manager.spend_gold(cost):
            return False

        tower = Tower(
            position=(row, col),
            damage=max(
                1,
                round(damage * self.game.tower_damage_multiplier)
            ),
            attack_range=attack_range,
            tower_type=tower_type
        )

        self.game.towers.append(tower)
        cell.has_tower = True

        print(f"Tower placed at ({row}, {col})")

        return True

    # --------------------------------------------------
    # TOWER REMOVAL
    # --------------------------------------------------

    def remove_tower(self, row, col):
        for tower in self.game.towers:

            if tower.position == (row, col):

                self.game.towers.remove(tower)

                cell = self.game.grid.get_cell(row, col)

                if cell is not None:
                    cell.has_tower = False

                print(f"Tower removed at ({row}, {col})")

                return True

        return False

    # --------------------------------------------------
    # TOWER UPGRADE
    # --------------------------------------------------

    def upgrade_tower(self, row, col):
        """
        Upgrade a tower if the player can afford it.

        Level 1 -> Level 2 -> Level 3
        """

        tower = self.get_tower_at(row, col)

        if tower is None:
            return False

        if not tower.can_upgrade():
            print(
                f"Tower at ({row}, {col}) is already max level."
            )
            return False

        cost = tower.upgrade_cost

        if not self.game.resource_manager.can_afford(cost):
            print(
                f"Not enough gold to upgrade tower at ({row}, {col})."
            )
            return False

        if not self.game.resource_manager.spend_gold(cost):
            return False

        old_level = tower.level

        if not tower.upgrade():
            # Refund if upgrade somehow fails.
            self.game.resource_manager.add_gold(cost)
            return False

        print(
            f"Tower at ({row}, {col}) upgraded "
            f"from level {old_level} to level {tower.level}."
        )

        return True

    # --------------------------------------------------
    # LOOKUP
    # --------------------------------------------------

    def get_tower_at(self, row, col):
        for tower in self.game.towers:
            if tower.position == (row, col):
                return tower

        return None

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    def can_place_tower(self, row, col):
        cell = self.game.grid.get_cell(row, col)

        if cell is None:
            return False

        if cell.blocked:
            return False

        if cell.is_castle:
            return False

        if cell.is_spawn:
            return False

        if cell.has_tower:
            return False

        if self.is_enemy_on_cell(row, col):
            return False

        return self.game.resource_manager.can_build_tower()

    def can_upgrade_tower(self, row, col):
        tower = self.get_tower_at(row, col)

        if tower is None:
            return False

        if not tower.can_upgrade():
            return False

        return self.game.resource_manager.can_afford(
            tower.upgrade_cost
        )

    # --------------------------------------------------
    # ENEMY CHECK
    # --------------------------------------------------

    def is_enemy_on_cell(self, row, col):
        for enemy in self.game.enemies:

            if not enemy.alive:
                continue

            if enemy.position == (row, col):
                return True

        return False

    # --------------------------------------------------
    # INFORMATION
    # --------------------------------------------------

    def get_tower_count(self):
        return len(self.game.towers)

    def get_tower_positions(self):
        return [
            tower.position
            for tower in self.game.towers
        ]

    def get_tower_status(self):
        return [
            tower.get_status()
            for tower in self.game.towers
        ]