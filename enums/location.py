from enum import unique, Enum
from typing import Optional

from autoslot import Slots


class LocationInstance(Slots):
    def __init__(self, name: str):
        self.name: str = name


@unique
class Location(Enum):
    _ignore_ = ['_INFO']
    NOWHERE = LocationInstance('Nowhere')
    TUTORIAL = LocationInstance('Tutorial')
    ANYWHERE = LocationInstance('Anywhere')
    COLISEUM = LocationInstance('Coliseum')
    FOREST = LocationInstance('Forest')
    LAKE = LocationInstance('Lake')
    _INFO = {}

    @staticmethod
    def get_from_name(name: str) -> Optional['Location']:
        return Location._INFO['from_name'].get(name)

    def __repr__(self):
        return f"<Location {self.get_name()}>"

    def __str__(self):
        return self.get_name()

    def get_name(self) -> str:
        return self.value.name


el_dict = {
    'from_name': {x.value.name: x for x in Location}
}

Location._INFO = el_dict
