import asyncio
import random
from typing import Optional

import utils
from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle_entity import BattleEntity, AttackResult
from adventure_classes.generic.chapter import Chapter
from enemy_data import enemy_utils
from entities.bot_entity import BotEntity
from enums.emoji import Emoji
from enums.location import Location
from item_data.abilities import AbilityInstance
from enums.item_type import ItemType
from item_data.stat import Stat
from user_data.user import User


class BattleChapter(Chapter):
    def __init__(self, entity_b: BotEntity, messages: list[str] = None, is_boss: bool = False):
        super().__init__(Emoji.BATTLE)
        self.battle_entity_a: Optional[BattleEntity] = None
        self.battle_entity_b: BattleEntity = BattleEntity(entity_b)

        if messages is None:
            messages = []
        self._messages: list[str] = [f"_{x}_" for x in messages]

        self._speedDiff: float = 0
        self._battle_log: list[str] = []
        self._finished: bool = False

        self._equipment_emoji: dict[ItemType, int] = {}
        self._first_message: str = ""
        self._turn_a: bool = False
        self._is_boss = is_boss

    async def init(self):
        assert len(self.get_adventure().get_users()) == 1, 'Battle with more than one user not currently supported'

        user = list(self.get_adventure().get_users().keys())[0]
        battle_num: int = self._adventure.saved_data.get('_battle_num', 0) + 1
        battle_started: str = f"{Emoji.BATTLE} BATTLE #{battle_num} STARTED {Emoji.BATTLE}"
        if self._is_boss:
            battle_started = f"{Emoji.BATTLE} **BOSS BATTLE** STARTED {Emoji.BATTLE}"
            await self.send_log('')
            for msg in self._messages:
                await self.get_adventure().append_message(msg)
                await asyncio.sleep(3)
            await asyncio.sleep(3)
        else:
            self.add_log(battle_started)
            self.add_log('\n'.join(self._messages))
        self._adventure.saved_data['_battle_num'] = battle_num
        self._first_message = battle_started
        setup_wait: int = utils.current_ms()
        await self.pop_log()
        self.battle_entity_a = BattleEntity(user.user_entity)

        # Get who is first
        speed_a = self.battle_entity_a.get_stat(Stat.SPD)
        speed_b = self.battle_entity_b.get_stat(Stat.SPD)
        if speed_b > speed_a:
            self._turn_a = True
        elif speed_b == speed_a and random.random() < 0.5:
            self._turn_a = True

        # Add basic actions
        await self.get_adventure().add_reaction(Emoji.BATTLE, self.attack)

        # Add equipment actions
        for _, itemType in self.battle_entity_a.get_abilities():
            self._equipment_emoji[itemType] = self._equipment_emoji.get(itemType, 0) + 1
        if self.battle_entity_b.is_user():
            for _, itemType in self.battle_entity_b.get_abilities():
                self._equipment_emoji[itemType] = self._equipment_emoji.get(itemType, 0) + 1

        for emoji in self._equipment_emoji.keys():
            await self.get_adventure().add_reaction(emoji.get_type_icon()[1:], self.ability)

        # Start
        diff = (utils.current_ms() - setup_wait) / 1000

        if diff < 1.5:
            await asyncio.sleep(diff)
        await self._next_turn(True)

    async def ability(self, user: User, input_reaction: str) -> None:
        # Check
        issuer, victim = self._get_issuer_victim(user)
        if not self._is_turn(issuer):
            return

        # Check ability available
        item_type: ItemType = ItemType.get_from_type_icon(f"\\{input_reaction}")
        ability: Optional[AbilityInstance] = issuer.use_ability(None, item_type)
        if not ability:
            return

        # Remove reaction
        self._equipment_emoji[item_type] -= 1
        if self._equipment_emoji[item_type] <= 0:
            del self._equipment_emoji[item_type]
            await self.get_adventure().remove_reactions(item_type.get_type_icon()[1:])

        # Who to add effect to
        # if ability.get().other:
        #     victim.add_effect(ability)
        #     self._battle_log.append(f"> {issuer.entity.get_name()} used {ability.get_name()} "
        #                             f"on {victim.entity.get_name()}!")
        # else:
        #     issuer.add_effect(ability, True)
        #     self._battle_log.append(f"> {issuer.entity.get_name()} used {ability.get_name()}!")

        # Next turn
        await self._next_turn()

    async def attack(self, user: Optional[User] = None, _2=None) -> None:
        # Check
        issuer, victim = self._get_issuer_victim(user)
        if not self._is_turn(issuer):
            return

        dealt: AttackResult = issuer.attack(victim)
        if dealt.eva:
            self._battle_log.append(f"> {victim.entity.get_name()} evaded {issuer.entity.get_name()}'s attack!")
        else:
            if dealt.vamp:
                if dealt.crit:
                    self._battle_log.append(f"> {issuer.entity.get_name()} **critically** stole {dealt.damage} "
                                            f"health from {victim.entity.get_name()}!")
                else:
                    self._battle_log.append(f"> {issuer.entity.get_name()} stole {dealt.damage} "
                                            f"health from {victim.entity.get_name()}!")
            else:
                if dealt.crit:
                    self._battle_log.append(f"> {issuer.entity.get_name()} dealt a **critical** attack to "
                                            f"{victim.entity.get_name()} for {dealt.damage} damage!")
                else:
                    self._battle_log.append(f"> {issuer.entity.get_name()} attacked {victim.entity.get_name()} "
                                            f"for {dealt.damage} damage!")

        await self._next_turn()

    def _get_issuer_victim(self, user: User) -> tuple[BattleEntity, BattleEntity]:
        issuer: BattleEntity = self.battle_entity_a
        victim: BattleEntity = self.battle_entity_b
        if (user is None) or (user.user_entity == self.battle_entity_b.entity):
            issuer, victim = victim, issuer

        return issuer, victim

    def _is_turn(self, battle_entity: BattleEntity):
        if battle_entity.entity == self.battle_entity_a.entity:
            return self._turn_a
        elif battle_entity.entity == self.battle_entity_b.entity:
            return not self._turn_a
        else:
            return False

    async def _next_turn(self, first_time: bool = False) -> None:
        if self._finished:
            return

        if self._turn_a:
            # B action
            self.battle_entity_a.end_turn()
            self._turn_a = False
            if self._speedDiff >= 1.0:
                self._speedDiff -= 1.0
                await self._next_turn()
                return
        else:
            # A action (New turn)
            self.battle_entity_b.end_turn()
            self._turn_a = True
            diff: float = self.battle_entity_a.get_stat(Stat.SPD) - self.battle_entity_b.get_stat(Stat.SPD)
            if first_time:
                diff = 0
            self._speedDiff += diff
            if self._speedDiff <= -1.0:
                self._speedDiff += 1.0 - diff
                await self._next_turn()
                return

        if self.battle_entity_a.entity.get_persistent(Stat.HP) == 0:
            await self._finish(True)
            return
        elif self.battle_entity_b.entity.get_persistent(Stat.HP) == 0:
            await self._finish(False)
            return

        # Check if 2 player
        if self.battle_entity_b.is_user():
            if self._turn_a:
                self._battle_log.append(f"[{self.battle_entity_a.entity.get_name()}'s turn]")
            else:
                self._battle_log.append(f"[{self.battle_entity_b.entity.get_name()}'s turn]")

        # Bot time
        if (not self.battle_entity_b.is_user()) and (not self._turn_a):
            await self.attack()
            return

        await self.pop_battle_log()

    async def pop_battle_log(self):
        how_many: int = max(min(round(self._speedDiff * 10), 10), -10)
        cti = '¦'
        if abs(self._speedDiff) >= 1.0:
            cti = '❚'
        self._battle_log.insert(0, f"``{self.battle_entity_b.entity.get_name()} "
                                   f"{'-' * (how_many + 10)}{cti}{'-' * (10 - how_many)} "
                                   f"{self.battle_entity_a.entity.get_name()}`` Speed Advantage")
        if self._first_message:
            self._battle_log.insert(0, self._first_message)
            if not self._is_boss:
                if self._messages:
                    self._battle_log.insert(0, '\n'.join(self._messages))
            self._first_message = ""
        self._battle_log.append(f"{self.battle_entity_a.entity.get_name()} - {self.battle_entity_a.print()}")
        self._battle_log.append(f"{self.battle_entity_b.entity.get_name()} - {self.battle_entity_b.print()}")
        tp = '\n'.join(self._battle_log)
        self.add_log(tp)
        self._battle_log.clear()
        await self.pop_log()

    async def _finish(self, b_won: bool = False):
        self._finished = True
        self.battle_entity_a.entity.end_battle()
        self.battle_entity_b.entity.end_battle()
        if b_won:
            self._battle_log.append(f"{Emoji.FIRST_PLACE} "
                                    f"{self.battle_entity_b.entity.get_name()} won the battle!")
            await self.pop_battle_log()
            await self.end(True)
        else:
            self._battle_log.append(f"{Emoji.FIRST_PLACE} "
                                    f"{self.battle_entity_a.entity.get_name()} won the battle!")
            await self.pop_battle_log()
            await self.end()


def add_to_adventure(adventure: Adventure, location: Location, pool: str = '', messages: list[str] = None,
                     boss: bool = False) -> BattleChapter:
    enemy = enemy_utils.get_random_enemy(location, pool, last_chosen_id=adventure.saved_data.get('_enemy_id'))
    adventure.saved_data['_enemy_id'] = enemy.enemy_id
    bc = BattleChapter(enemy.instance(), messages=messages, is_boss=boss)
    adventure.add_chapter(bc)
    return bc
