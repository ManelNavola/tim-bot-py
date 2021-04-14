from enum import Enum


class EnumPlus(Enum):

    @classmethod
    def get_all(cls):
        return list(cls)
