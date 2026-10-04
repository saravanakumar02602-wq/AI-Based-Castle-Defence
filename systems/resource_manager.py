class ResourceManager:
    """
    Controls the player's gold economy.

    The player receives gold from:
        - Starting resources
        - Defeating enemies
        - Completing waves
        - Small passive income

    This keeps the game playable instead of allowing
    the AI to overwhelm the player during Wave 1.
    """

    def __init__(self, starting_gold=800):

        self.starting_gold = starting_gold

        self.gold = starting_gold

        # Construction costs
        self.tower_cost = 100
        self.wall_cost = 50

        # Rewards
        self.enemy_reward = 75
        self.wave_reward = 150

        # Passive income
        self.passive_income_timer = 0.0
        self.passive_income_interval = 8.0
        self.passive_income_amount = 25

        # Statistics
        self.total_earned = 0
        self.total_spent = 0
        self.enemies_rewarded = 0
        self.waves_rewarded = 0

    # ==================================================
    # UPDATE
    # ==================================================

    def update(self, delta_time):

        self.passive_income_timer += delta_time

        if (
            self.passive_income_timer
            >= self.passive_income_interval
        ):

            self.passive_income_timer = 0.0

            self.add_gold(
                self.passive_income_amount
            )

            print(
                f"+{self.passive_income_amount} gold "
                f"(passive income)"
            )

    # ==================================================
    # GOLD
    # ==================================================

    def get_gold(self):
        return self.gold

    def add_gold(self, amount):

        if amount <= 0:
            return

        self.gold += amount
        self.total_earned += amount

    def can_afford(self, amount):

        return self.gold >= amount

    def spend_gold(self, amount):

        if amount <= 0:
            return False

        if not self.can_afford(amount):
            return False

        self.gold -= amount
        self.total_spent += amount

        return True

    # ==================================================
    # TOWERS
    # ==================================================

    def can_build_tower(self):

        return self.can_afford(
            self.tower_cost
        )

    def buy_tower(self):

        return self.spend_gold(
            self.tower_cost
        )

    # ==================================================
    # WALLS
    # ==================================================

    def can_build_wall(self):

        return self.can_afford(
            self.wall_cost
        )

    def buy_wall(self):

        return self.spend_gold(
            self.wall_cost
        )

    # ==================================================
    # ENEMY REWARDS
    # ==================================================

    def reward_enemy_defeat(self, amount=None):

        reward = self.enemy_reward if amount is None else amount

        self.add_gold(
            reward
        )

        self.enemies_rewarded += 1

        print(
            f"+{reward} gold "
            f"(enemy defeated)"
        )

    # ==================================================
    # WAVE REWARD
    # ==================================================

    def reward_wave_completion(self):

        self.add_gold(
            self.wave_reward
        )

        self.waves_rewarded += 1

        print(
            f"+{self.wave_reward} gold "
            f"(wave completed)"
        )

    # ==================================================
    # STATUS
    # ==================================================

    def get_status(self):

        return {
            "gold": self.gold,
            "starting_gold": self.starting_gold,
            "tower_cost": self.tower_cost,
            "wall_cost": self.wall_cost,
            "enemy_reward": self.enemy_reward,
            "wave_reward": self.wave_reward,
            "passive_income": self.passive_income_amount,
            "total_earned": self.total_earned,
            "total_spent": self.total_spent,
            "enemies_rewarded": self.enemies_rewarded,
            "waves_rewarded": self.waves_rewarded,
        }

    # ==================================================
    # DEBUG
    # ==================================================

    def print_status(self):

        print()
        print("========== RESOURCE STATUS ==========")
        print(f"Gold: {self.gold}")
        print(f"Total earned: {self.total_earned}")
        print(f"Total spent: {self.total_spent}")
        print(
            f"Enemies rewarded: "
            f"{self.enemies_rewarded}"
        )
        print(
            f"Waves rewarded: "
            f"{self.waves_rewarded}"
        )
        print("=====================================")
        print()