from item_data.stat import Stat


def pack_stat_dict(stats: dict[Stat, int]):
    return {
        stat.get_abv(): value for stat, value in stats.items()
    }


def unpack_stat_dict(stats: dict[str, int]):
    return {
        Stat.get_by_abv(abv): value for abv, value in stats.items()
    }
