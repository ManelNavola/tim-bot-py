import random
import typing

from adventure_classes.generic.battle import battle
from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.bonus import BonusChapter
from adventure_classes.generic.choice import ChoiceChapter
from adventure_classes.generic.reward import MoneyRewardChapter, ItemRewardChapter
from adventure_classes.generic.stat_modifier import StatModifierAdd
from entities.ai.ability_ai import AbilityAI, AbilityDecision
from entities.bot_entity import BotEntity
from enums.emoji import Emoji
from enums.location import Location
from enums.item_rarity import ItemRarity
from helpers.translate import tr
from item_data.abilities import AbilityContainer, AbilityEnum
from item_data.item_classes import Item
from item_data.item_utils import RandomItemBuilder
from item_data.stat import Stat

if typing.TYPE_CHECKING:
    from helpers.command import Command


def eat_mushroom(color: int):
    def mushroom_effect(adventure: Adventure):
        bc = BonusChapter(tr(adventure.get_lang(), 'FOREST.EVENT6'))
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
    bc = BonusChapter(tr(adventure.get_lang(), 'FOREST.EVENT5'))
    if random.random() < 0.5:
        bc.add_modifier(StatModifierAdd(Stat.EVA, 3))
    else:
        bc.add_modifier(StatModifierAdd(Stat.SPD, 3))
    adventure.add_chapter(bc)
    battle.qsab(adventure, Location.FOREST, 'C')

    cc = ChoiceChapter(Emoji.MUSHROOM, tr(adventure.get_lang(), 'FOREST.DECISION4_TEXT'))
    cc.add_choice(Emoji.RED, tr(adventure.get_lang(), 'FOREST.DECISION4_OPTION1'), eat_mushroom(0))
    cc.add_choice(Emoji.BLUE, tr(adventure.get_lang(), 'FOREST.DECISION4_OPTION2'), eat_mushroom(1))
    cc.add_choice(Emoji.GREEN, tr(adventure.get_lang(), 'FOREST.DECISION4_OPTION3'), eat_mushroom(2))
    adventure.add_chapter(cc)

    battle.qsab(adventure, Location.FOREST, 'B')
    ability_ai: AbilityAI = AbilityAI([
        AbilityDecision(0, 0.5, AbilityContainer(AbilityEnum.SUMMON, 100), max_uses=1)
    ])
    boss: BotEntity = battle.rnd(adventure, Location.FOREST, 'BOSS', ability_ai)
    battle.qcsab(adventure, boss,
                 icon=Emoji.FOREST,
                 pre_text=[tr(adventure.get_lang(), 'FOREST.BOSS1'),
                           tr(adventure.get_lang(), 'FOREST.BOSS2'),
                           tr(adventure.get_lang(), 'FOREST.BOSS3')])

    item: Item = RandomItemBuilder(0).set_location(Location.FOREST).build()
    adventure.add_chapter(ItemRewardChapter(item))


def ab_continue_path(adventure):
    if random.random() < 0.5:
        bc = BonusChapter(tr(adventure.get_lang(), 'FOREST.EVENT3'))
        bc.add_modifier(StatModifierAdd(Stat.DEF, 3))
        adventure.add_chapter(bc)
    else:
        bc = BonusChapter(tr(adventure.get_lang(), 'FOREST.EVENT4'))
        bc.add_persistent(Stat.HP, Stat.HP.get_value(2))
        adventure.add_chapter(bc)
    battle.qsab(adventure, Location.FOREST, 'A')
    battle.qsab(adventure, Location.FOREST, 'C')
    if random.random() < 0.5:
        adventure.add_chapter(MoneyRewardChapter(random.randint(100, 150)))
    else:
        item: Item = RandomItemBuilder(0).set_location(Location.ANYWHERE) \
            .choose_rarity([ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC], [6, 3, 1]).build()
        adventure.add_chapter(ItemRewardChapter(item))


def a_deep(adventure):
    battle.qsab(adventure, Location.FOREST, 'B')
    battle.qsab(adventure, Location.FOREST, 'B')
    adventure.add_chapter(ChoiceChapter(Emoji.BEAR, tr(adventure.get_lang(), 'FOREST.DECISION3_TEXT'))
                          .add_choice(Emoji.UP, tr(adventure.get_lang(), 'FOREST.DECISION3_OPTION1'), aa_deeper)
                          .add_choice(Emoji.RIGHT, tr(adventure.get_lang(), 'FOREST.DECISION3_OPTION2'),
                                      ab_continue_path))


def b_reward(adventure):
    if random.random() < 0:
        adventure.add_chapter(MoneyRewardChapter(random.randint(50, 100)))
    else:
        item: Item = RandomItemBuilder(0).set_location(Location.ANYWHERE) \
            .choose_rarity([ItemRarity.COMMON, ItemRarity.UNCOMMON], [5, 2]).build()
        adventure.add_chapter(ItemRewardChapter(item))


def ba_bear(adventure):
    if random.random() < 0.4:
        battle.qsab(adventure, Location.FOREST, 'D', icon=Emoji.BEAR,
                    pre_text=[tr(adventure.get_lang, 'FOREST.EVENT2')])
    else:
        battle.qsab(adventure, Location.FOREST, 'A')
    b_reward(adventure)


def bb_around_bear(adventure):
    battle.qsab(adventure, Location.FOREST, 'A')
    battle.qsab(adventure, Location.FOREST, 'B')
    b_reward(adventure)


def b_around(adventure):
    bc = BonusChapter(tr(adventure.get_lang, 'FOREST.EVENT1'))
    bc.add_persistent(Stat.HP, Stat.HP.get_value(3))
    adventure.add_chapter(bc)
    battle.qsab(adventure, Location.FOREST, 'B')
    adventure.add_chapter(ChoiceChapter(Emoji.BEAR, tr(adventure.get_lang(), 'FOREST.DECISION2_TEXT'))
                          .add_choice(Emoji.UP, tr(adventure.get_lang(), 'FOREST.DECISION2_OPTION1'), ba_bear)
                          .add_choice(Emoji.RIGHT, tr(adventure.get_lang(), 'FOREST.DECISION2_OPTION2'),
                                      bb_around_bear))


async def setup(_: 'Command', adventure: Adventure):
    battle.qsab(adventure, Location.FOREST, 'A')
    battle.qsab(adventure, Location.FOREST, 'A')
    adventure.add_chapter(ChoiceChapter(Emoji.GARDEN, tr(adventure.get_lang(), 'FOREST.DECISION1_TEXT'))
                          .add_choice(Emoji.UP, tr(adventure.get_lang(), 'FOREST.DECISION1_OPTION1'), a_deep)
                          .add_choice(Emoji.RIGHT, tr(adventure.get_lang(), 'FOREST.DECISION1_OPTION2'), b_around))
