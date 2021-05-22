from enum import Enum
from typing import Optional


class Emoji(Enum):
    # User profile
    MONEY = r'\💵'
    BANK = r'\💰'
    GARDEN = r'\🌲'
    SCROLL = r'\📜'
    HOSPITAL = r'\💉'

    # Betting
    ROBOT = r'\🤖'
    COWBOY = r'\🤠'
    SUNGLASSES = r'\😎'
    SPARKLE = r'\✨'
    MONEY_FLY = r'\💸'
    INCREASE = r'\🔺'
    DECREASE = r'\🔻'

    # Commands
    ERROR = r'\⛔'

    # Crate
    BOX = r'\📦'
    CLOCK = r'\🕓'

    # Inventory
    EQUIPPED = r'\✔️'
    TOKEN = r'\🧭'
    SHOP = r'\🛒'
    PURCHASE = r'\🛍️'
    STATS = r'\🧮'
    BAG = r'\🎒'
    WEAPON = r'\🗡️'
    SHIELD = r'\🛡️'
    HELMET = r'\⛑️'
    CHEST_PLATE = r'\👕'
    LEGGINGS = r'\👖'
    BOOTS = r'\👢'
    ARROW_RIGHT = r'➜'

    # Leaderboard
    TROPHY = r'\🏆'
    FIRST_PLACE = r'\🥇'
    SECOND_PLACE = r'\🥈'
    THIRD_PLACE = r'\🥉'

    # Stats
    HP = r'\💉'
    AP = r'\📖️'
    STR = r'\💪'
    DEF = r'\🛡️'
    SPD = r'\🏃'
    EVA = r'\💨'
    CONT = r'\👊'
    CRIT = r'\🌟'
    STUN = r'\🛑'
    VAMP = r'\🧛'

    # Adventure
    BATTLE = r'\⚔️'
    UP = r'\⬆'
    DOWN = r'⬇'
    LEFT = r'\⬅'
    RIGHT = r'\➡'
    OK = r'\✅'
    DEAD = r'\💀'

    # Tutorial
    TUTORIAL = r'\⛵'
    WAVES = r'\🌊'

    # Coliseum
    COLISEUM = r'\🔱'

    # Forest
    FOREST = r'\🌳'
    BEAR = r'\🐻'
    MUSHROOM = r'\🍄'

    # Lake
    LAKE = r'\🏕️'
    SEED = r'\🌱'
    LOBSTER = r'\🦞'

    # Classes
    WARRIOR = r'\🛡️'
    ROGUE = r'\🗡️'
    MAGE = r'\⚗️'
    BARBARIAN = r'\🪓'

    # Spells
    BLUE_BOOK = r'\📘'
    RED_BOOK = r'\📕'
    GREEN_BOOK = r'\📗'
    ORANGE_BOOK = r'\📙'

    # Colors
    RED = r'\🟥'
    BLUE = r'\🟦'
    GREEN = r'\🟩'

    # Numbers
    ZERO = r'\0️⃣'
    ONE = r'\1️⃣'
    TWO = r'\2️⃣'
    THREE = r'\3️⃣'
    FOUR = r'\4️⃣'
    FIVE = r'\5️⃣'
    SIX = r'\6️⃣'
    SEVEN = r'\7️⃣'
    EIGHT = r'\8️⃣'
    NINE = r'\9️⃣'
    TEN = r'\🔟'

    # Abilities
    BURN = r'\🔥'

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
