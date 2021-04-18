from typing import Optional, Any

from entities.entity import Entity
from item_data.abilities import AbilityInstance
from item_data.stats import StatInstance, Stats


class BotEntityBuilder:
    def __init__(self, name: str, stat_dict: dict[StatInstance, int],
                 abilities: Optional[list[AbilityInstance]] = None, enemy_id: Optional[int] = None):
        if not abilities:
            abilities = []
        self.abilities: list[AbilityInstance] = abilities
        self.stat_dict: dict[StatInstance, int] = stat_dict
        self.name = name
        self.enemy_id: Optional[int] = enemy_id

    def instance(self):
        return BotEntity(self.name, self.stat_dict.copy(), [ab for ab in self.abilities])


class BotEntity(Entity):
    def __init__(self, name: str, stat_dict: dict[StatInstance, int],
                 abilities: Optional[list[AbilityInstance]] = None):
        super().__init__(stat_dict)
        self._name: str = name
        self._persistent_ref = {stat: stat.get_value(stat_dict.get(stat, 0))
                                for stat in Stats.get_all() if stat.is_persistent}
        if abilities is not None:
            self._available_abilities = abilities

    def get_name(self) -> str:
        return self._name

    def set_persistent(self, stat: StatInstance, value: Any) -> None:
        self._persistent_ref[stat] = value

    def get_persistent(self, stat: StatInstance, default=0) -> Any:
        return self._persistent_ref.get(stat, default)

    def get_stat_value(self, stat: StatInstance) -> int:
        return self._stat_dict.get(stat, 0)

    def print_detailed(self) -> str:
        dc: list[str] = []
        for stat in Stats.get_all():
            if stat in self._stat_dict:
                dc.append(stat.print(self._stat_dict.get(stat, 0)))
        return '\n'.join(dc)
