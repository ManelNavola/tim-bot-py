import random
from typing import Callable

from discord_slash import SlashContext

from adventure_classes.generic import battle
from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.chapter import Chapter
from adventure_classes.generic.reward import MoneyRewardChapter, ItemRewardChapter
from adventure_classes.generic.stat_modifier import StatModifier, StatModifierAdd
from enums.emoji import Emoji
from enums.location import Location
from enums.item_rarity import ItemRarity
from item_data.item_classes import Item
from item_data.item_utils import RandomItemBuilder
from item_data.stat import Stat
from user_data.user import User


class BonusChapter(Chapter):
    def __init__(self, text: str):
        super().__init__(Emoji.BOX)
        self._text: str = text
        self._bonus: list[StatModifier] = []
        self._persistent_bonus: list[tuple[Stat, int]] = []

    def add_modifier(self, modifier: StatModifier):
        self._bonus.append(modifier)

    def add_persistent(self, stat: Stat, value: int):
        self._persistent_bonus.append((stat, value))

    async def init(self):
        self.add_log(self._text)
        users: list[User] = list(self.get_adventure().get_users().keys())
        for bonus in self._bonus:
            if bonus.duration < 0:
                self.add_log(f"{bonus.print()} {bonus.stat.get_abv()} for the whole adventure")
            elif bonus.duration == 1:
                self.add_log(f"{bonus.print()} {bonus.stat.get_abv()} for the next battle")
            else:
                self.add_log(f"{bonus.print()} {bonus.stat.get_abv()} for the next {bonus.duration} battles")
            for user in users:
                user.user_entity.add_modifier(bonus)
        for bonus in self._persistent_bonus:
            stat: Stat = bonus[0]
            amount: int = bonus[1]
            for user in users:
                old_value = user.user_entity.get_persistent(stat)
                if old_value:
                    new_value = min(old_value + amount, stat.get_value(user.user_entity.get_stat_value(stat)))
                    user.user_entity.change_persistent(stat, new_value)
                    self.add_log(f"+{amount} {stat.get_abv()} ({old_value} {Emoji.ARROW_RIGHT} {new_value})")
        await self.pop_log()
        await self.end()


def eat_mushroom(color: int):
    def mushroom_effect(adventure: Adventure):
        bc = BonusChapter('You feel the effect of the mushroom...')
        if color == 0:
            bc.add_modifier(StatModifierAdd(Stat.DEF, -2, 1))
        elif color == 1:
            bc.add_modifier(StatModifierAdd(Stat.SPD, 5))
        else:
            bc.add_persistent(Stat.HP, Stat.HP.get_value(4))
        adventure.insert_chapter(bc)

    return mushroom_effect


def aa_deeper(adventure: Adventure):
    battle.add_to_adventure(adventure, Location.FOREST, 'C')
    bc = BonusChapter('As you venture deeper into the forest, you gather some courage...')
    if random.random() < 0.5:
        bc.add_modifier(StatModifierAdd(Stat.EVA, 3))
    else:
        bc.add_modifier(StatModifierAdd(Stat.SPD, 3))
    adventure.add_chapter(bc)
    battle.add_to_adventure(adventure, Location.FOREST, 'C')

    cc = ChoiceChapter(Emoji.MUSHROOM, 'Under a tree you find three mushrooms...')
    cc.add_choice(Emoji.RED, 'Eat the red mushroom', eat_mushroom(0))
    cc.add_choice(Emoji.BLUE, 'Eat the blue mushroom', eat_mushroom(1))
    cc.add_choice(Emoji.GREEN, 'Eat the green mushroom', eat_mushroom(2))
    adventure.add_chapter(cc)

    battle.add_to_adventure(adventure, Location.FOREST, 'B')
    bc = battle.add_to_adventure(adventure, Location.FOREST, 'BOSS',
                                     messages=['You feel the forest watching you...', 'Suddenly you see something move!',
                                           'But it is not a wild animal...'], boss=True)
    bc.icon = Emoji.FOREST

    item: Item = RandomItemBuilder(0).set_location(Location.FOREST).build()
    adventure.add_chapter(ItemRewardChapter(item))


def ab_continue_path(adventure):
    if random.random() < 0.5:
        bc = BonusChapter('You find some aloe behind a bush')
        bc.add_modifier(StatModifierAdd(Stat.DEF, 3))
        adventure.add_chapter(bc)
    else:
        bc = BonusChapter('You find healing herbs near a tree')
        bc.add_persistent(Stat.HP, Stat.HP.get_value(3))
        adventure.add_chapter(bc)
    battle.add_to_adventure(adventure, Location.FOREST, 'A')
    battle.add_to_adventure(adventure, Location.FOREST, 'C')
    if random.random() < 0.5:
        adventure.add_chapter(MoneyRewardChapter(random.randint(300, 400)))
    else:
        item: Item = RandomItemBuilder(0).set_location(Location.ANYWHERE)\
            .choose_rarity([ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC], [6, 3, 1]).build()
        adventure.add_chapter(ItemRewardChapter(item))


def a_deep(adventure):
    battle.add_to_adventure(adventure, Location.FOREST, 'B')
    battle.add_to_adventure(adventure, Location.FOREST, 'B')
    adventure.add_chapter(ChoiceChapter(Emoji.FOREST, 'You find a path without any light:')
                          .add_choice(Emoji.UP, 'Venture into the darkest, deepest part of the forest', aa_deeper)
                          .add_choice(Emoji.RIGHT, 'Continue your journey', ab_continue_path))


def b_reward(adventure):
    if random.random() < 0:
        adventure.add_chapter(MoneyRewardChapter(random.randint(100, 200)))
    else:
        item: Item = RandomItemBuilder(0).set_location(Location.ANYWHERE) \
            .choose_rarity([ItemRarity.COMMON, ItemRarity.UNCOMMON], [2, 1]).build()
        adventure.add_chapter(ItemRewardChapter(item))


def ba_bear(adventure):
    if random.random() < 0.4:
        battle.add_to_adventure(adventure, Location.FOREST, 'D', messages=['The bear woke up!']).icon = Emoji.BEAR
    else:
        battle.add_to_adventure(adventure, Location.FOREST, 'A')
    b_reward(adventure)


def bb_around_bear(adventure):
    battle.add_to_adventure(adventure, Location.FOREST, 'A')
    battle.add_to_adventure(adventure, Location.FOREST, 'B')
    b_reward(adventure)


def b_around(adventure):
    bc = BonusChapter('You find some healing roots...')
    bc.add_persistent(Stat.HP, Stat.HP.get_value(3))
    adventure.add_chapter(bc)
    battle.add_to_adventure(adventure, Location.FOREST, 'B')
    adventure.add_chapter(ChoiceChapter(Emoji.BEAR, 'You find a sleeping bear blocking your path:')
                          .add_choice(Emoji.UP, 'Try to sneak past the bear', ba_bear)
                          .add_choice(Emoji.RIGHT, 'Find another path', bb_around_bear))


async def start(ctx: SlashContext, user: User):
    adventure: Adventure = Adventure("Forest", Emoji.FOREST)

    battle.add_to_adventure(adventure, Location.FOREST, 'A')
    battle.add_to_adventure(adventure, Location.FOREST, 'A')
    adventure.add_chapter(ChoiceChapter(Emoji.GARDEN, 'You find yourself at an intersection:')
                          .add_choice(Emoji.UP, 'Go deep into the forest', a_deep)
                          .add_choice(Emoji.RIGHT, 'Go around the forest', b_around))

    await adventure.start(ctx, [user])
