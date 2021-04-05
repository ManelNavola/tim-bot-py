from typing import Optional

from autoslot import Slots

from inventory_data import items
from inventory_data.abilities import AbilityInstance
from utils import DictRef
from inventory_data.items import Item, ItemType
from inventory_data.stats import StatInstance, Stats
from abc import ABCMeta, abstractmethod


class AbilityEffect(Slots):
    def __init__(self, ability_instance: AbilityInstance):
        self.instance = ability_instance
        self.duration = ability_instance.get().duration


class Entity(metaclass=ABCMeta):
    def __init__(self, stat_dict: dict[StatInstance, int]):
        self._stat_dict: dict[StatInstance, int] = stat_dict
        self._available_abilities: list[AbilityInstance] = []
        self._ability_effects: dict[StatInstance, list[AbilityEffect]] = {}

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_current_hp(self) -> int:
        pass

    @abstractmethod
    def get_current_mp(self) -> int:
        pass

    @abstractmethod
    def set_current_health(self, amount: int) -> None:
        pass

    def add_effect(self, ability_instance: AbilityInstance):
        stat: StatInstance = ability_instance.get().stat
        if stat not in self._ability_effects:
            self._ability_effects[stat] = []
        self._ability_effects[stat].append(AbilityEffect(ability_instance))

    def clear_effects(self):
        self._ability_effects.clear()

    def apply_turn(self):
        to_del = []
        for key, effect_list in self._ability_effects.items():
            for i in range(len(effect_list) - 1, -1, -1):
                effect_list[i].duration -= 1
                if effect_list[i].duration <= 0:
                    del effect_list[i]
            if len(effect_list) == 0:
                to_del.append(key)
        for key in to_del:
            del self._ability_effects[key]

    def use_ability(self, ability_instance: AbilityInstance) -> bool:
        if ability_instance in self._available_abilities:
            self._available_abilities.remove(ability_instance)
            return True
        return False

    def get_stat(self, stat: StatInstance) -> int:
        val = stat.get_value(self._stat_dict.get(stat, 0))
        for effect in self._ability_effects.get(stat, []):
            val = val * effect.instance.get().multiplier
            val += effect.instance.get().adder
        return round(val)

    def print_battle_stat(self, stat: StatInstance) -> str:
        stuff: list[str] = []
        for effect in self._ability_effects.get(stat, []):
            if effect.instance.get().multiplier != 1:
                stuff.append(f"x{effect.instance.get().multiplier:.2f}")
            if effect.instance.get().adder != 0:
                stuff.append(f"{effect.instance.get().adder}")
        persistent = {
            Stats.HP: self.get_current_hp(),
            Stats.MP: self.get_current_mp()
        }
        if stuff:
            return stat.print(self.get_stat(stat), short=True, persistent_value=persistent.get(stat)) +\
                   ' (' + ', '.join(stuff) + ')'
        else:
            return stat.print(self.get_stat(stat), short=True, persistent_value=persistent.get(stat))

    def print_battle(self):
        sc: list[str] = [self.print_battle_stat(Stats.HP), self.print_battle_stat(Stats.MP)]

        for stat in Stats.get_all():
            if stat in self._stat_dict:
                if stat not in [Stats.HP, Stats.MP]:
                    sc.append(self.print_battle_stat(stat))

        return ', '.join(sc)

    def print_detailed(self):
        dc: list[str] = [Stats.HP.print(self.get_stat(Stats.HP), persistent_value=self.get_current_hp()),
                         Stats.MP.print(self.get_stat(Stats.MP), persistent_value=self.get_current_mp())]

        for stat in Stats.get_all():
            if stat in self._stat_dict:
                if stat not in [Stats.HP, Stats.MP]:
                    dc.append(stat.print(self.get_stat(stat)))

        return '\n'.join(dc)

    def damage(self, other: 'Entity') -> int:
        dealt = other.get_stat(Stats.STR)
        if dealt <= 0:
            return 0
        br: float = (dealt / (dealt + self.get_stat(Stats.DEF))) * dealt
        real_amount = max(1, round(br))
        self.set_current_health(max(0, self.get_current_hp() - real_amount))
        return real_amount


class BotEntity(Entity):
    def __init__(self, name: str, max_hp: int, max_mp: int, stat_dict: dict[StatInstance, int],
                 abilities: Optional[list[AbilityInstance]] = None):
        stat_dict.update({
            Stats.HP: max_hp - Stats.HP.base,
            Stats.MP: max_mp - Stats.MP.base
        })
        super().__init__(stat_dict)
        self._name: str = name
        self._current_hp: int = max_hp
        self._current_mp: int = max_mp
        if abilities is not None:
            self._available_abilities = abilities

    def get_name(self) -> str:
        return self._name

    def get_current_hp(self) -> int:
        return self._current_hp

    def get_current_mp(self) -> int:
        return self._current_mp

    def set_current_health(self, amount: int) -> None:
        self._current_hp = amount


class UserEntity(Entity):
    def __init__(self, name_ref: DictRef, hp_ref: DictRef, mp_ref: DictRef):
        super().__init__({})
        self._stat_dict: dict[StatInstance, int] = {}
        self._mp_ref: DictRef = mp_ref
        self._hp_ref: DictRef = hp_ref
        self._name_ref: DictRef = name_ref
        self._stat_sum: int = 0
        self._equipment_abilities: dict[ItemType, AbilityInstance] = {}

    def get_stat_sum(self) -> int:
        return self._stat_sum

    def get_name(self) -> str:
        return self._name_ref.get()

    def get_current_hp(self) -> int:
        return self._hp_ref.get()

    def get_current_mp(self) -> int:
        return self._mp_ref.get()

    def set_current_health(self, amount: int) -> None:
        self._hp_ref.set(amount)

    def update_items(self, item_list: list[Item]):
        self._stat_sum = 0
        self._stat_dict.clear()
        self._equipment_abilities.clear()
        self._available_abilities.clear()
        for item in item_list:
            for stat, value in item.data.stats.items():
                self._stat_dict[stat] = self._stat_dict.get(stat, 0) + value
                self._stat_sum += value
            if item.data.ability is not None:
                self._available_abilities.append(item.data.ability)
                self._equipment_abilities[items.INDEX_TO_ITEM[item.data.desc_id].type] = item.data.ability

    def get_equipment_abilities(self) -> dict[ItemType, AbilityInstance]:
        return self._equipment_abilities
