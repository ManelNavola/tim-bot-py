from enums.enum_plus import EnumPlus


class Emoji(EnumPlus):
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
    MP = r'\⚗️'
    STR = r'\💪'
    DEF = r'\🛡️'
    SPD = r'\🏃'
    EVA = r'\💨'
    CONT = r'\👊'
    CRIT = r'\🌟'
    STUN = r'\🛑'
    VAMP = r'\🧛'

    # Adventure
    COLISEUM = r'\🔱'
    BATTLE = r'\⚔️'

    @classmethod
    def get_all(cls) -> list['Emoji']:
        return list(cls)

    def __str__(self) -> str:
        return self.value

    def first(self) -> str:
        return self.value[1]

    def compare(self, other: str) -> bool:
        return other in self.value
