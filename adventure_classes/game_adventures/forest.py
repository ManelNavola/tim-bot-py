import random
import typing

from adventure_classes.generic.battle import battle
from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.chapter import Chapter
from adventure_classes.generic.choice import ChoiceChapter
from adventure_classes.generic.reward import MoneyRewardChapter, ItemRewardChapter
from adventure_classes.generic.stat_modifier import StatModifier, StatModifierAdd
from entities.ai.ability_ai import AbilityAI, AbilityDecision
from entities.bot_entity import BotEntity
from enums.emoji import Emoji
from enums.location import Location
from enums.item_rarity import ItemRarity
from item_data.abilities import AbilityContainer, AbilityEnum
from item_data.item_classes import Item
from item_data.item_utils import RandomItemBuilder
from item_data.stat import Stat
from user_data.user import User

if typing.TYPE_CHECKING:
    from helpers.command import Command


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
        users: set[User] = self.get_adventure().get_users()
        for bonus in self._bonus:
            if bonus.duration < 0:
                self.add_log(f"{bonus.print()} {bonus.stat.get_abv()} for the whole adventure")
            elif bonus.duration == 1:
                self.add_log(f"{bonus.print()} {bonus.stat.get_abv()} for the next battle")
            else:
                self.add_log(f"{bonus.print()} {bonus.stat.get_abv()} for the next {bonus.duration} battles")
            for user in users:
                user.user_entity.add_battle_modifier(bonus)
        for bonus in self._persistent_bonus:
            stat: Stat = bonus[0]
            amount: int = bonus[1]
            for user in users:
                old_value = user.user_entity.get_persistent_value(stat)
                if old_value:
                    new_value = min(old_value + amount, stat.get_value(user.user_entity.get_stat(stat)))
                    user.user_entity.change_persistent_value(stat, new_value)
                    self.add_log(f"+{amount} {stat.get_abv()} ({old_value} {Emoji.ARROW_RIGHT} {new_value})")
        await self.send_log()
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
    battle.qsab(adventure, Location.FOREST, 'C')
    bc = BonusChapter('As you venture deeper into the forest, you gather some courage...')
    if random.random() < 0.5:
        bc.add_modifier(StatModifierAdd(Stat.EVA, 3))
    else:
        bc.add_modifier(StatModifierAdd(Stat.SPD, 3))
    adventure.add_chapter(bc)
    battle.qsab(adventure, Location.FOREST, 'C')

    cc = ChoiceChapter(Emoji.MUSHROOM, 'Under a tree you find three mushrooms...')
    cc.add_choice(Emoji.RED, 'Eat the red mushroom', eat_mushroom(0))
    cc.add_choice(Emoji.BLUE, 'Eat the blue mushroom', eat_mushroom(1))
    cc.add_choice(Emoji.GREEN, 'Eat the green mushroom', eat_mushroom(2))
    adventure.add_chapter(cc)

    battle.qsab(adventure, Location.FOREST, 'B')
    ability_ai: AbilityAI = AbilityAI([
        AbilityDecision(0, 0.5, AbilityContainer(AbilityEnum.SUMMON, 100), max_uses=1)
    ])
    boss: BotEntity = battle.rnd(adventure, Location.FOREST, 'BOSS', ability_ai)
    battle.qcsab(adventure, boss,
                 icon=Emoji.FOREST,
                 pre_text=['You feel the forest watching you...',
                           'Suddenly you see something move!',
                           'But it is not a wild animal...'])

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
    battle.qsab(adventure, Location.FOREST, 'A')
    battle.qsab(adventure, Location.FOREST, 'C')
    if random.random() < 0.5:
        adventure.add_chapter(MoneyRewardChapter(random.randint(300, 400)))
    else:
        item: Item = RandomItemBuilder(0).set_location(Location.ANYWHERE) \
            .choose_rarity([ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC], [6, 3, 1]).build()
        adventure.add_chapter(ItemRewardChapter(item))


def a_deep(adventure):
    battle.qsab(adventure, Location.FOREST, 'B')
    battle.qsab(adventure, Location.FOREST, 'B')
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
        battle.qsab(adventure, Location.FOREST, 'D', icon=Emoji.BEAR, pre_text=['The bear woke up...'])
    else:
        battle.qsab(adventure, Location.FOREST, 'A')
    b_reward(adventure)


def bb_around_bear(adventure):
    battle.qsab(adventure, Location.FOREST, 'A')
    battle.qsab(adventure, Location.FOREST, 'B')
    b_reward(adventure)


def b_around(adventure):
    bc = BonusChapter('You find some healing roots...')
    bc.add_persistent(Stat.HP, Stat.HP.get_value(3))
    adventure.add_chapter(bc)
    battle.qsab(adventure, Location.FOREST, 'B')
    adventure.add_chapter(ChoiceChapter(Emoji.BEAR, 'You find a sleeping bear blocking your path:')
                          .add_choice(Emoji.UP, 'Try to sneak past the bear', ba_bear)
                          .add_choice(Emoji.RIGHT, 'Find another path', bb_around_bear))


async def setup(_: 'Command', adventure: Adventure):
    battle.qsab(adventure, Location.FOREST, 'A')
    battle.qsab(adventure, Location.FOREST, 'A')
    adventure.add_chapter(ChoiceChapter(Emoji.GARDEN, 'You find yourself at an intersection:')
                          .add_choice(Emoji.UP, 'Go deep into the forest', a_deep)
                          .add_choice(Emoji.RIGHT, 'Go around the forest', b_around))
