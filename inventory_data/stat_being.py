import utils
from utils import DictRef
from inventory_data.items import Item
from inventory_data.stats import StatInstance, Stats


class StatBeing:
    def __init__(self, name: DictRef, current_hp: DictRef, current_mp: DictRef):
        self._name: DictRef = name
        self._stats: dict[StatInstance, int] = {}
        self.stat_sum: int = 0
        self._stats_print: str = ""
        self._current_hp: DictRef = current_hp
        self._current_mp: DictRef = current_mp
        self.init_stats()

    def damage(self, stat_being: 'StatBeing') -> int:
        dealt = stat_being.get_value(Stats.STR)
        if dealt <= 0:
            return 0
        real_amount = max(1, int(round(dealt / (dealt + self.get_value(Stats.DEF)))))
        self._current_hp.set(max(0, self._current_hp.get() - real_amount))
        self.update_text()
        return real_amount

    def get_name(self):
        return self._name.get()

    def get_value(self, stat: StatInstance):
        if stat == Stats.HP:
            return self._current_hp.get()
        elif stat == Stats.MP:
            return self._current_mp.get()
        else:
            return stat.get_value(self._stats.get(stat, 0))

    def init_stats(self):
        self._stats.clear()
        for stat in Stats.get_all():
            if stat.base > 0:
                self._stats[stat] = 0
        self.update_text()

    def update_text(self):
        tr = []
        for stat in Stats.get_all():
            if stat in self._stats:
                if stat == Stats.HP:
                    tr.append(stat.print(self._stats[stat], self._current_hp.get()))
                elif stat == Stats.MP:
                    tr.append(stat.print(self._stats[stat], self._current_mp.get()))
                else:
                    tr.append(stat.print(self._stats[stat]))
        self._stats_print = '\n'.join(tr)

    def update(self, item_list: list[Item]):
        self.stat_sum = 0
        self.init_stats()
        for item in item_list:
            for stat, value in item.data.stats.items():
                self._stats[stat] = self._stats.get(stat, 0) + value
                self.stat_sum += value
        self.update_text()

    def print(self, one_line: bool = False) -> str:
        if one_line:
            tr = []
            for stat in Stats.get_all():
                if stat in self._stats:
                    if stat == Stats.HP:
                        tr.append(f"{stat.abv}: {self._current_hp.get()}/{stat.get_value(self._stats[stat])}")
                    elif stat == Stats.MP:
                        tr.append(f"{stat.abv}: {self._current_mp.get()}/{stat.get_value(self._stats[stat])}")
                    else:
                        tr.append(f"{stat.abv}: {stat.get_value(self._stats[stat])}")
            return ', '.join(tr)
        else:
            return '\n'.join([f"{utils.Emoji.STATS} Player Stats:", self._stats_print])
