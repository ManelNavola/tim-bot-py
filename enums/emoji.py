from enum import Enum
from typing import Optional


class Emoji(Enum):
    # User profile
    MONEY = r'\๐ต'
    BANK = r'\๐ฐ'
    GARDEN = r'\๐ฒ'
    SCROLL = r'\๐'
    HOSPITAL = r'\๐'

    # Betting
    ROBOT = r'\๐ค'
    COWBOY = r'\๐ค '
    SUNGLASSES = r'\๐'
    SPARKLE = r'\โจ'
    MONEY_FLY = r'\๐ธ'
    INCREASE = r'\๐บ'
    DECREASE = r'\๐ป'

    # Commands
    ERROR = r'\โ'

    # Crate
    BOX = r'\๐ฆ'
    CLOCK = r'\๐'

    # Inventory
    EQUIPPED = r'\โ๏ธ'
    TOKEN = r'\๐งญ'
    SHOP = r'\๐'
    PURCHASE = r'\๐๏ธ'
    STATS = r'\๐งฎ'
    BAG = r'\๐'
    WEAPON = r'\๐ก๏ธ'
    SHIELD = r'\๐ก๏ธ'
    HELMET = r'\โ๏ธ'
    CHEST_PLATE = r'\๐'
    LEGGINGS = r'\๐'
    BOOTS = r'\๐ข'
    ARROW_RIGHT = r'โ'
    POTION = r'\โ๏ธ'
    POTION_TUBE = r'\๐งช'

    # Leaderboard
    TROPHY = r'\๐'
    FIRST_PLACE = r'\๐ฅ'
    SECOND_PLACE = r'\๐ฅ'
    THIRD_PLACE = r'\๐ฅ'

    # Stats
    HP = r'\๐'
    AP = r'\๐๏ธ'
    STR = r'\๐ช'
    DEF = r'\๐ก๏ธ'
    SPD = r'\๐'
    EVA = r'\๐จ'
    CONT = r'\๐'
    CRIT = r'\๐'
    STUN = r'\๐'
    VAMP = r'\๐ง'

    # Adventure
    BATTLE = r'\โ๏ธ'
    UP = r'\โฌ'
    DOWN = r'โฌ'
    LEFT = r'\โฌ'
    RIGHT = r'\โก'
    OK = r'\โ'
    DEAD = r'\๐'

    # Tutorial
    TUTORIAL = r'\โต'
    WAVES = r'\๐'

    # Coliseum
    COLISEUM = r'\๐ฑ'

    # Forest
    FOREST = r'\๐ณ'
    BEAR = r'\๐ป'
    MUSHROOM = r'\๐'

    # Lake
    LAKE = r'\๐๏ธ'
    SEED = r'\๐ฑ'
    LOBSTER = r'\๐ฆ'

    # Classes
    WARRIOR = r'\๐ก๏ธ'
    ROGUE = r'\๐ก๏ธ'
    MAGE = r'\โ๏ธ'
    BARBARIAN = r'\๐ช'

    # Spells
    BLUE_BOOK = r'\๐'
    RED_BOOK = r'\๐'
    GREEN_BOOK = r'\๐'
    ORANGE_BOOK = r'\๐'

    # Colors
    RED = r'\๐ฅ'
    BLUE = r'\๐ฆ'
    GREEN = r'\๐ฉ'

    # Numbers
    ZERO = r'\0๏ธโฃ'
    ONE = r'\1๏ธโฃ'
    TWO = r'\2๏ธโฃ'
    THREE = r'\3๏ธโฃ'
    FOUR = r'\4๏ธโฃ'
    FIVE = r'\5๏ธโฃ'
    SIX = r'\6๏ธโฃ'
    SEVEN = r'\7๏ธโฃ'
    EIGHT = r'\8๏ธโฃ'
    NINE = r'\9๏ธโฃ'
    TEN = r'\๐'

    # Abilities
    BURN = r'\๐ฅ'

    # Generic
    TICK = r'\โ'
    CROSS = r'\โ'

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def get_number(num: int):
        return [Emoji.ZERO, Emoji.ONE, Emoji.TWO, Emoji.THREE, Emoji.FOUR, Emoji.FIVE, Emoji.SIX, Emoji.SEVEN,
                Emoji.EIGHT, Emoji.NINE, Emoji.TEN][num]

    def get_number_str(self) -> str:
        return "{}\N{COMBINING ENCLOSING KEYCAP}".format(self.get_number_value())

    def get_number_value(self) -> Optional[int]:
        return {
            Emoji.ZERO: 0,
            Emoji.ONE: 1,
            Emoji.TWO: 2,
            Emoji.THREE: 3,
            Emoji.FOUR: 4,
            Emoji.FIVE: 5,
            Emoji.SIX: 6,
            Emoji.SEVEN: 7,
            Emoji.EIGHT: 8,
            Emoji.NINE: 9,
            Emoji.TEN: 10
        }.get(self)

    def first(self) -> str:
        return self.value[1:]

    def compare(self, other: str) -> bool:
        return (other == self.value) or self.value[1:].startswith(other)
