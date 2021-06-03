from enum import unique, Enum

from autoslot import Slots


class LocationInstance(Slots):
    def __init__(self, loc_id: int, name: str):
        self.id: int = loc_id
        self.name: str = name


@unique
class Location(Enum):
    _ignore_ = ['_INFO']
    NOWHERE = LocationInstance(0, 'Nowhere')
    TUTORIAL = LocationInstance(1, 'Tutorial')
    ANYWHERE = LocationInstance(2, 'Anywhere')
    COLISEUM = LocationInstance(3, 'Coliseum')
    FOREST = LocationInstance(4, 'Forest')
    LAKE = LocationInstance(5, 'Lake')
    _INFO = {}

    def get_id(self) -> int:
        return self.value.id

    @staticmethod
    def from_name(name: str) -> 'Location':
        return {
            x.value.name: x for x in Location
        }[name]

    @staticmethod
    def from_id(eid: int) -> 'Location':
        return {
            x.value.id: x for x in Location
        }[eid]

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
