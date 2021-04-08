from entities.entity import Entity
from item_data import items
from item_data.items import Item
from item_data.stats import StatInstance
from utils import DictRef


class UserEntity(Entity):
    def __init__(self, name_ref: DictRef, hp_ref: DictRef, mp_ref: DictRef):
        super().__init__({})
        self._stat_dict: dict[StatInstance, int] = {}
        self._mp_ref: DictRef = mp_ref
        self._hp_ref: DictRef = hp_ref
        self._name_ref: DictRef = name_ref
        self._power: int = 0

    def get_power(self) -> int:
        return self._power

    def get_name(self) -> str:
        return self._name_ref.get()

    def get_current_hp(self) -> int:
        return self._hp_ref.get()

    def get_current_mp(self) -> int:
        return self._mp_ref.get()

    def set_current_health(self, amount: int) -> None:
        self._hp_ref.set(amount)

    def update_equipment(self, item_list: list[Item]):
        calc_power: float = 0
        self._stat_dict.clear()
        self._available_abilities.clear()
        for item in item_list:
            for stat, value in item.data.stats.items():
                self._stat_dict[stat] = self._stat_dict.get(stat, 0) + value
            if item.data.ability is not None:
                self._available_abilities.append((item.data.ability, items.INDEX_TO_ITEM[item.data.desc_id].type))
            calc_power += item.get_price()
        self._power = calc_power // 100
