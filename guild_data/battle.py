import random
from enum import Enum, unique
from typing import Optional

from discord import Message

import utils
from inventory_data.entity import Entity
from inventory_data.stats import Stats
from user_data.user import User


@unique
class BattleAction(Enum):
    ATTACK = 0


class Battle:
    BATTLE_ACTIONS: dict[str, BattleAction] = {
        utils.Emoji.BATTLE[1]: BattleAction.ATTACK
    }

    def __init__(self, entity_a: Entity, entity_b: Entity, b_player_id: Optional[int] = None):
        self.battle_ended: bool = False
        self.entity_a: Entity = entity_a
        self.entity_b: Entity = entity_b
        self._b_player_id: Optional[int] = b_player_id
        self._log: list[str] = []
        self._message_id: int = -1

        speed_a = self.entity_a.get_stat(Stats.SPD)
        speed_b = self.entity_b.get_stat(Stats.SPD)
        self._turn_a: bool = True
        if speed_b > speed_a:
            self._turn_a = False
        elif speed_b == speed_a and random.random() < 0.5:
            self._turn_a = False

        if (self._b_player_id is None) and (not self._turn_a):
            self.action(None, BattleAction.ATTACK)

        if self._b_player_id is not None:
            if self._turn_a:
                self._log.append(f"[{self.entity_a.get_name()}'s turn]")
            else:
                self._log.append(f"[{self.entity_b.get_name()}'s turn]")

    async def init(self, message: Message):
        self._message_id = message.id
        for emoji in Battle.BATTLE_ACTIONS.keys():
            await message.add_reaction(emoji)

    def attack(self, is_b: bool):
        attacker: Entity = self.entity_b if is_b else self.entity_a
        receiver: Entity = self.entity_a if is_b else self.entity_b

        dealt = receiver.damage(attacker)
        self._log.append(f"> {attacker.get_name()} attacked {receiver.get_name()} for {dealt} damage!")

    def pop_log(self):
        self._log.append(f"{self.entity_a.get_name()} - {self.entity_a.print_simple()}")
        self._log.append(f"{self.entity_b.get_name()} - {self.entity_b.print_simple()}")
        tp = '\n'.join(self._log)
        self._log.clear()
        return tp

    def get_message_id(self):
        return self._message_id

    def _finish(self, b_won: bool = False):
        if b_won:
            self._log.append(f"{utils.Emoji.FIRST_PLACE} {self.entity_b.get_name()} won the battle!")
        else:
            self._log.append(f"{utils.Emoji.FIRST_PLACE} {self.entity_a.get_name()} won the battle!")
        self.battle_ended = True

    def action(self, user: Optional[User], action: BattleAction) -> bool:
        if action is None:
            return False
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
        if self.entity_a.get_current_hp() == 0:
            self._finish(True)
            return True
        elif self.entity_b.get_current_mp() == 0:
            self._finish()
            return True

        # Switch turn
        self._turn_a = not self._turn_a

        # Bot action
        if (not self._turn_a) and (self._b_player_id is None):
            return self.action(None, BattleAction.ATTACK)

        if self._b_player_id is not None:
            if self._turn_a:
                self._log.append(f"[{self.entity_a.get_name()}'s turn]")
            else:
                self._log.append(f"[{self.entity_b.get_name()}'s turn]")

        return True
