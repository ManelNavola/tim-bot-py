import random
from enum import Enum, unique
from typing import Optional, Any

from autoslot import Slots
from discord import Message

import utils
from commands import messages
from commands.messages import MessagePlus
from inventory_data.abilities import AbilityInstance
from inventory_data.entity import Entity, UserEntity
from inventory_data.items import ItemType
from inventory_data.stats import Stats, StatInstance
from user_data.user import User


@unique
class BattleAction(Enum):
    ATTACK = 0
    ABILITY = 1

    def get_emoji(self) -> str:
        emoji_dict: dict[BattleAction, str] = {
            BattleAction.ATTACK: utils.Emoji.BATTLE[1:]
        }
        return emoji_dict[self]


class AbilityEffect(Slots):
    def __init__(self, ability_instance: AbilityInstance):
        self.instance = ability_instance
        self.duration = ability_instance.get().duration


class AttackResult(Slots):
    def __init__(self):
        self.damage: Optional[int] = None
        self.crit: bool = False
        self.eva: bool = False
        self.vamp: bool = False
        self.counter: Optional[int] = None


class BattleEntity:
    def __init__(self, entity: Entity):
        self.entity = entity
        self._available_abilities: list[tuple[AbilityInstance, Optional[ItemType]]] = entity.get_abilities()
        self._effects: list[AbilityEffect] = []
        self._is_user: bool = isinstance(entity, UserEntity)

    def attack(self, other: 'BattleEntity', ignore_cont: bool = False) -> AttackResult:
        ar: AttackResult = AttackResult()
        # Evasion
        if random.random() < other.get_stat(Stats.EVA):
            ar.eva = True
            return ar
        # Counter
        if (not ignore_cont) and random.random() < other.get_stat(Stats.CONT):
            ar.counter, _ = other.attack(self, True)

        # Damage
        dealt: int = self.get_stat(Stats.STR)
        br: float = (dealt / (dealt + other.get_stat(Stats.DEF))) * dealt
        real_amount: int = max(1, round(br))
        other.entity.set_current_health(max(0, other.entity.get_current_hp() - real_amount))
        # Crit
        if random.random() < self.get_stat(Stats.CRIT):
            real_amount *= 2
            ar.crit = True
        # Vamp
        if random.random() < self.get_stat(Stats.VAMP):
            ar.vamp = True
        ar.damage = real_amount
        return ar

    def add_effect(self, ability_instance: AbilityInstance, include: bool = False):
        ae = AbilityEffect(ability_instance)
        if include:
            ae.duration += 1
        self._effects.append(ae)

    def end_turn(self):
        for i in range(len(self._effects) - 1, -1, -1):
            self._effects[i].duration -= 1
            if self._effects[i].duration <= 0:
                del self._effects[i]

    def use_ability(self, ability: Optional[AbilityInstance], item_type: Optional[ItemType]) \
            -> Optional[AbilityInstance]:
        for i in range(len(self._available_abilities)):
            other_ability, other_item_type = self._available_abilities[i]
            if ((ability is None) or (ability == other_ability)) \
                    and ((item_type is None) or (item_type == other_item_type)):
                del self._available_abilities[i]
                return other_ability
        return None

    def get_abilities(self) -> list[tuple[AbilityInstance, Optional[ItemType]]]:
        return self._available_abilities

    def is_user(self) -> bool:
        return self._is_user

    def get_stat(self, stat: StatInstance) -> Any:
        return stat.get_value(self._get_stat_value(stat))

    def _get_stat_value(self, stat: StatInstance) -> int:
        val = self.entity.get_stat_dict().get(stat, 0) + stat.base
        for effect in self._effects:
            if effect.instance.get().stat == stat:
                val = val * effect.instance.get().multiplier
                val += effect.instance.get().adder
        val -= stat.base
        return max(round(val), -stat.base)

    def _print_battle_stat(self, stat: StatInstance) -> str:
        stuff: list[str] = []
        for effect in self._effects:
            if effect.instance.get().stat == stat:
                if effect.instance.get().multiplier != 1:
                    stuff.append(f"x{effect.instance.get().multiplier:.2f}")
                if effect.instance.get().adder != 0:
                    stuff.append(f"{effect.instance.get().adder}")
        persistent = {
            Stats.HP: self.entity.get_current_hp(),
            Stats.MP: self.entity.get_current_mp()
        }
        if stuff:
            return stat.print(self._get_stat_value(stat), short=True, persistent_value=persistent.get(stat)) +\
                   ' (' + ', '.join(stuff) + ')'
        else:
            return stat.print(self._get_stat_value(stat), short=True, persistent_value=persistent.get(stat))

    def print(self) -> str:
        sc: list[str] = [self._print_battle_stat(Stats.HP), self._print_battle_stat(Stats.MP)]

        for stat in Stats.get_all():
            if self.get_stat(stat) > 0:
                if stat not in [Stats.HP, Stats.MP]:
                    sc.append(self._print_battle_stat(stat))

        return ', '.join(sc)


class Battle:
    def __init__(self, entity_a: UserEntity, entity_b: Entity):
        self.guild = None

        self.battle_entity_a: BattleEntity = BattleEntity(entity_a)
        self.battle_entity_b: BattleEntity = BattleEntity(entity_b)

        self.turn: int = 0
        self._log: list[str] = []
        self._message: Optional[MessagePlus] = None

        self._equipment_emoji: dict[ItemType, int] = {}

        # Get who is first
        speed_a = self.battle_entity_a.get_stat(Stats.SPD)
        speed_b = self.battle_entity_b.get_stat(Stats.SPD)
        self._turn_a: bool = False
        if speed_b > speed_a:
            self._turn_a = True
        elif speed_b == speed_a and random.random() < 0.5:
            self._turn_a = True

    async def init(self, guild, message: Message, user_id_list: list[int]):
        # Set guild
        self.guild = guild

        # Create MessagePlus
        mp = messages.register_message_reactions(guild, message, user_id_list)
        self._message = mp

        # Add basic actions
        await mp.add_reaction(BattleAction.ATTACK.get_emoji(), self.attack)

        # Add equipment actions
        for _, itemType in self.battle_entity_a.get_abilities():
            self._equipment_emoji[itemType] = self._equipment_emoji.get(itemType, 0) + 1
        if self.battle_entity_b.is_user():
            for _, itemType in self.battle_entity_b.get_abilities():
                self._equipment_emoji[itemType] = self._equipment_emoji.get(itemType, 0) + 1

        for emoji in self._equipment_emoji.keys():
            await mp.add_reaction(emoji.get_type_icon()[1:], self.ability)

        # Start
        await self._next_turn()

    async def ability(self, _, user: User, input_reaction: str) -> None:
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
            await self._message.remove_reactions(item_type.get_type_icon()[1:])

        # Who to add effect to
        if ability.get().other:
            victim.add_effect(ability)
            self._log.append(f"> {issuer.entity.get_name()} used {ability.get_name()} on {victim.entity.get_name()}!")
        else:
            issuer.add_effect(ability, True)
            self._log.append(f"> {issuer.entity.get_name()} used {ability.get_name()}!")

        # Next turn
        await self._next_turn()

    async def attack(self, _=None, user: Optional[User] = None, _2=None) -> None:
        # Check
        issuer, victim = self._get_issuer_victim(user)
        if not self._is_turn(issuer):
            return

        dealt: AttackResult = issuer.attack(victim)
        if dealt.eva:
            self._log.append(f"> {victim.entity.get_name()} evaded {issuer.entity.get_name()}'s attack!")
        else:
            if dealt.vamp:
                if dealt.crit:
                    self._log.append(f"> {victim.entity.get_name()} **critically** stole {dealt.damage} "
                                     f"health from {issuer.entity.get_name()}!")
                else:
                    self._log.append(f"> {victim.entity.get_name()} stole {dealt.damage} "
                                     f"health from {issuer.entity.get_name()}!")
            else:
                if dealt.crit:
                    self._log.append(f"> {issuer.entity.get_name()} dealt a **critical** attack to "
                                     f"{victim.entity.get_name()} for {dealt.damage} damage!")
                else:
                    self._log.append(f"> {issuer.entity.get_name()} attacked {victim.entity.get_name()} "
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

    async def _next_turn(self) -> None:
        if self._turn_a:
            self.battle_entity_a.end_turn()
            self._turn_a = False
        else:
            self.battle_entity_b.end_turn()
            self._turn_a = True
            self.turn += 1

        if self.battle_entity_a.entity.get_current_hp() == 0:
            await self._finish(True)
            return
        elif self.battle_entity_b.entity.get_current_hp() == 0:
            await self._finish(False)
            return

        # Check if 2 player
        if self.battle_entity_b.is_user():
            if self._turn_a:
                self._log.append(f"[{self.battle_entity_a.entity.get_name()}'s turn]")
            else:
                self._log.append(f"[{self.battle_entity_b.entity.get_name()}'s turn]")

        # Bot time
        if (not self.battle_entity_b.is_user()) and (not self._turn_a):
            await self.attack()
            return

        await self._message.message.edit(content=self.pop_log())

    def pop_log(self):
        if self.turn < 10:
            self._log.insert(0, f"``Turn:  {'-' * (self.turn - 1)}{self.turn}{'-' * (9 - self.turn)}``")
        else:
            self._log.insert(0, f"``Turn: {'-' * (self.turn % 10)}{self.turn}{'-' * (8 - self.turn % 10)}``")
        self._log.append(f"{self.battle_entity_a.entity.get_name()} - {self.battle_entity_a.print()}")
        self._log.append(f"{self.battle_entity_b.entity.get_name()} - {self.battle_entity_b.print()}")
        tp = '\n'.join(self._log)
        self._log.clear()
        return tp

    async def _finish(self, b_won: bool = False):
        if b_won:
            self._log.append(f"{utils.Emoji.FIRST_PLACE} {self.battle_entity_b.entity.get_name()} won the battle!")
        else:
            self._log.append(f"{utils.Emoji.FIRST_PLACE} {self.battle_entity_a.entity.get_name()} won the battle!")
        self.guild.end_battle(self)
        await self._message.message.edit(content=self.pop_log())
        messages.unregister(self._message)
