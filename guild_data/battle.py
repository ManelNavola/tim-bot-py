import random
from enum import Enum, unique
from typing import Optional

from inventory_data.stat_being import StatBeing
from inventory_data.stats import Stats
from user_data.user import User


@unique
class BattleAction(Enum):
    ATTACK = 0


class Battle:
    def __init__(self, being_a: StatBeing, being_b: StatBeing, b_player_id: Optional[int] = None):
        self.battle_ended: bool = False
        self.being_a: StatBeing = being_a
        self.being_b: StatBeing = being_b
        self._b_player_id: Optional[int] = b_player_id
        self._log: list[str] = []

        speed_a = self.being_a.get_value(Stats.SPD)
        speed_b = self.being_b.get_value(Stats.SPD)
        self._turn_a: bool = True
        if speed_b > speed_a:
            self._turn_a = False
        elif speed_b == speed_a and random.random() < 0.5:
            self._turn_a = False

        if (self._b_player_id is None) and (not self._turn_a):
            self.action(None, BattleAction.ATTACK)

    def attack(self, is_b: bool):
        attacker: StatBeing = self.being_b if is_b else self.being_a
        receiver: StatBeing = self.being_a if is_b else self.being_b

        dealt = receiver.damage(attacker)
        self._log.append(f"{attacker.get_name()} attacked {receiver.get_name()} for {dealt} damage!")

    def pop_log(self):
        self._log.append(f"{self.being_a.get_name()} - {self.being_a.print(True)}")
        self._log.append(f"{self.being_b.get_name()} - {self.being_b.print(True)}")
        tp = '\n'.join(self._log)
        self._log.clear()
        return tp

    def _finish(self, b_won: bool = False):
        if b_won:
            self._log.append(f"{self.being_b.get_name()} won the battle!")
        else:
            self._log.append(f"{self.being_b.get_name()} won the battle!")
        self.battle_ended = True

    def action(self, user: Optional[User], action: BattleAction) -> bool:
        # Is being B?
        if user is None:
            is_b = True
        else:
            is_b = (user.id == self._b_player_id)

        # Correct turn?
        if (self._turn_a and is_b) or (not self._turn_a and not is_b):
            return False

        # Perform action
        if action == BattleAction.ATTACK:
            self.attack(is_b)

        # Check if finished
        if self.being_a.get_value(Stats.HP) == 0:
            self._finish()
            return True
        elif self.being_b.get_value(Stats.HP) == 0:
            self._finish(True)
            return True

        # Switch turn
        self._turn_a = not self._turn_a

        # Bot action
        if (not self._turn_a) and (self._b_player_id is None):
            return self.action(None, BattleAction.ATTACK)

        return True
