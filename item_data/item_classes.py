import random
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict

from enums.emoji import Emoji
from enums.item_type import EquipmentType
from enums.location import Location
from enums.item_rarity import ItemRarity
from item_data import item_loader
from item_data.item_descriptions import EquipmentDescription, ItemDescription, PotionDescription
from item_data.stat import Stat, StatType
from item_data.stat_modifier import StatModifier


class Item(ABC):
    def __init__(self, item_id: int = -1):
        self._id: int = item_id
        self._desc: Optional[ItemDescription] = None
        self._price_modifier: Optional[float] = None

    def get_id(self) -> int:
        return self._id

    def get_desc(self) -> ItemDescription:
        return self._desc

    @abstractmethod
    def get_price(self) -> int:
        pass

    def get_price_modifier(self) -> Optional[float]:
        return self._price_modifier

    def from_dict(self, desc_id: int, data_dict: Dict[str, Any]) -> None:
        self._desc = item_loader.get_description(desc_id)
        self._price_modifier = data_dict.get('price_modifier', None)

    def build(self, desc_id: int, price_modifier: Optional[int] = None) -> None:
        self._desc = item_loader.get_description(desc_id)
        self._price_modifier = price_modifier

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self._price_modifier is not None:
            d['price_modifier'] = self._price_modifier
        return d

    def print(self) -> str:
        raise NotImplementedError("Should not be able to print a base Item class")


class Equipment(Item):
    def __init__(self, item_id: int = -1):
        super().__init__(item_id)
        self._rarity: ItemRarity = ItemRarity.UNKNOWN
        self._stat_bonus: Dict[Stat, int] = {}

    def from_dict(self, desc_id: int, data_dict: Dict[str, Any]) -> None:
        super().from_dict(desc_id, data_dict)
        self._rarity = ItemRarity.get_from_id(data_dict['rarity'])
        self._stat_bonus = EquipmentDescription.unpack_stat_dict(data_dict['stat_bonus'])

    def build(self, desc_id: int, rarity: ItemRarity, stat_bonus: Dict[Stat, int], # noqa who cares
              price_modifier: Optional[float] = None) -> None:
        super().build(desc_id, price_modifier)
        self._rarity = rarity
        self._stat_bonus = stat_bonus

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = super().to_dict()
        d.update({
            'rarity': self._rarity.get_id(),
            'stat_bonus': EquipmentDescription.pack_stat_dict(self._stat_bonus)
        })
        return d

    def get_desc(self) -> EquipmentDescription:
        desc: ItemDescription = super().get_desc()
        assert isinstance(desc, EquipmentDescription)
        return desc

    def get_stats(self):
        stats: Dict[Stat, int] = self.get_desc().base_stats.copy()
        for stat, value in self._stat_bonus.items():
            stats[stat] = stats.get(stat, 0) + value
        return stats

    def get_price(self, ignore_modifier: bool = False) -> int:
        stat_dict: Dict[Stat, int] = self.get_stats()
        stat_sum: float = sum([float(v) * k.get_type().get_weighted_value() for k, v in stat_dict.items()])
        rarity = self._rarity.get_id() + 1
        price_mod = 1
        if (self.get_price_modifier() is not None) and (not ignore_modifier):
            price_mod = self.get_price_modifier()

        before_round = (stat_sum * pow(rarity, 0.8) * 80) * price_mod
        return round(before_round / 10) * 10

    def print(self) -> str:
        stat_dict: Dict[Stat, int] = self.get_stats()
        stats = ', '.join([f"+{v} {k.get_abv()}" for k, v in stat_dict.items()])
        return f"{self.get_desc().subtype} _{self._rarity.get_name()}_ {self.get_desc().name} [{stats}]"


class RandomEquipmentBuilder:
    def __init__(self, tier: int):
        self.tier: int = tier
        self.location: Location = Location.ANYWHERE
        self.item_type: List[EquipmentType] = []
        self.item_type_weights: List[int] = []
        self.item_rarity: List[ItemRarity] = \
            [ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]
        self.item_rarity_weights: List[int] = \
            [100, 60, 25, 5, 1]

    def set_location(self, location: Location) -> 'RandomEquipmentBuilder':
        self.location = location
        return self

    def set_type(self, item_type: EquipmentType) -> 'RandomEquipmentBuilder':
        self.item_type = [item_type]
        self.item_type_weights = [1]
        return self

    def choose_type(self, item_types: List[EquipmentType], weights: Optional[List[int]]) -> 'RandomEquipmentBuilder':
        self.item_type = item_types
        if weights:
            assert len(weights) == len(item_types)
            self.item_type_weights = weights
        else:
            self.item_type_weights = [1] * len(item_types)
        return self

    def set_rarity(self, rarity: ItemRarity):
        self.item_rarity = [rarity]
        self.item_rarity_weights = [1]
        return self

    def choose_rarity(self, item_rarities: List[ItemRarity], weights: Optional[List[float]] = None)\
            -> 'RandomEquipmentBuilder':
        self.item_rarity = item_rarities
        if weights:
            assert len(weights) == len(item_rarities)
            self.item_rarity_weights = weights
        else:
            self.item_rarity_weights = [1] * len(item_rarities)
        return self

    def build(self) -> Equipment:
        if not self.item_type:
            self.item_type = list(item_loader.get_equipment_dict()[self.tier][self.location].keys())
            self.item_type_weights = [1 for _ in self.item_type]
        item_type: EquipmentType = random.choices(self.item_type, weights=self.item_type_weights, k=1)[0]
        item_rarity: ItemRarity = random.choices(self.item_rarity, weights=self.item_rarity_weights, k=1)[0]
        if item_rarity == ItemRarity.LEGENDARY:
            r: float = random.random()
            if 0.1 < r < 0.2:
                item_rarity = ItemRarity.RED_LEGENDARY
            elif r < 0.1:
                item_rarity = ItemRarity.BLUE_LEGENDARY
        desc: EquipmentDescription = random.choice(item_loader.get_equipment_dict()
                                                   [self.tier][self.location][item_type])
        equipment: Equipment = Equipment()
        equipment.build(desc.id, item_rarity, self.get_stat_bonus(desc, item_rarity))
        return equipment

    @staticmethod
    def get_stat_bonus(desc: EquipmentDescription, rarity: ItemRarity) -> Dict[Stat, int]:
        base_main: List[Stat] = [x for x in desc.base_stats.keys() if x.get_type() == StatType.MAIN]
        chance_main: List[Stat] = [x for x in desc.base_stats.keys() if x.get_type() == StatType.CHANCE]

        sb: Dict[Stat, int] = {}
        if rarity == ItemRarity.COMMON:  # =
            pass

        elif rarity == ItemRarity.UNCOMMON:  # +0/1
            if chance_main:
                sb[random.choice(chance_main)] = 1
            else:
                sb[random.choice(Stat.get_type_list(StatType.CHANCE))] = 1

        elif rarity == ItemRarity.RARE:  # +1/1
            if chance_main:
                sb[random.choice(chance_main)] = 1
            else:
                sb[random.choice(Stat.get_type_list(StatType.CHANCE))] = 1
            if base_main:
                sb[random.choice(base_main)] = 1
            else:
                if chance_main:
                    rc = random.choice(chance_main)
                    sb[rc] = sb.get(rc, 0) + 1
                else:
                    rc = random.choice(Stat.get_type_list(StatType.CHANCE))
                    sb[rc] = sb.get(rc, 0) + 1

        elif rarity == ItemRarity.EPIC:  # +1/2
            first_one = random.randint(1, 2)
            if base_main:
                sb[random.choice(base_main)] = first_one
            else:
                sb[random.choice(Stat.get_type_list(StatType.MAIN))] = first_one
            if chance_main:
                sb[random.choice(chance_main)] = 3 - first_one
            else:
                sb[random.choice(Stat.get_type_list(StatType.CHANCE))] = 3 - first_one

        elif rarity == ItemRarity.LEGENDARY:  # +2/2
            if base_main:
                sb[random.choice(base_main)] = 2
            else:
                sb[random.choice(Stat.get_type_list(StatType.MAIN))] = 2
            if chance_main:
                sb[random.choice(chance_main)] = 2
            else:
                sb[random.choice(Stat.get_type_list(StatType.CHANCE))] = 2

        elif rarity == ItemRarity.RED_LEGENDARY:  # +3/1
            if base_main:
                sb[random.choice(base_main)] = 3
            else:
                sb[random.choice(Stat.get_type_list(StatType.MAIN))] = 3
            if chance_main:
                sb[random.choice(chance_main)] = 1
            else:
                sb[random.choice(Stat.get_type_list(StatType.CHANCE))] = 1

        elif rarity == ItemRarity.BLUE_LEGENDARY:  # +1/3
            if base_main:
                sb[random.choice(base_main)] = 1
            else:
                sb[random.choice(Stat.get_type_list(StatType.MAIN))] = 1
            if chance_main:
                sb[random.choice(chance_main)] = 3
            else:
                sb[random.choice(Stat.get_type_list(StatType.CHANCE))] = 3

        return sb


class Potion(Item):
    def __init__(self, item_id: int = -1):
        super().__init__(item_id)

    def get_desc(self) -> PotionDescription:
        desc: ItemDescription = super().get_desc()
        assert isinstance(desc, PotionDescription)
        return desc

    def copy_stat_modifiers(self) -> List[StatModifier]:
        return [sm.clone() for sm in self.get_desc().stat_modifiers]

    def get_price(self, ignore_modifier: bool = False) -> int:
        stat_sum: float = 0
        for sm in self.get_desc().stat_modifiers:
            stat_sum += sm.get_price()
        price_mod = 1
        if (self.get_price_modifier() is not None) and (not ignore_modifier):
            price_mod = self.get_price_modifier()

        return round((stat_sum * price_mod * 10) / 10) * 10

    def print(self) -> str:
        grouped_stat_modifiers: Dict[int, Dict[int, List[StatModifier]]] = {
            0: {},  # Battle
            1: {},  # Turn
            2: {},  # Instant
        }
        for sm in self.get_desc().stat_modifiers:
            d: Dict[int, List[StatModifier]]
            if sm.persistent:
                d = grouped_stat_modifiers[2]
                d[sm.duration] = d.get(0, []) + [sm]
            elif sm.per_battle:
                d = grouped_stat_modifiers[1]
                d[sm.duration] = d.get(sm.duration, []) + [sm]
            else:
                d = grouped_stat_modifiers[0]
                d[sm.duration] = d.get(sm.duration, []) + [sm]
        tp: List[str] = []
        for _, sm_list in grouped_stat_modifiers[2].items():
            tp.append(f"{', '.join(x.print(True) for x in sm_list)}")
        for duration, sm_list in grouped_stat_modifiers[1].items():
            tp.append(f"{', '.join(x.print(True) for x in sm_list)} for {duration} turns")
        for duration, sm_list in grouped_stat_modifiers[0].items():
            tp.append(f"{', '.join(x.print(True) for x in sm_list)} for {duration} battles")

        sss: str = '\n'.join(tp)
        return f"{Emoji.POTION_TUBE} {self.get_desc().name} " \
               f"({sss})"
