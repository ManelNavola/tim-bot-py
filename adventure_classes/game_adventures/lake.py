import random
import typing

from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle import battle
from adventure_classes.generic.bonus import BonusChapter
from adventure_classes.generic.choice import ChoiceChapter
from adventure_classes.generic.reward import MoneyRewardChapter, ItemRewardChapter
from entities.ai.ability_ai import AbilityAI, AbilityDecision
from entities.bot_entity import BotEntity
from enums.emoji import Emoji
from enums.item_rarity import ItemRarity
from enums.location import Location
from helpers.translate import tr
from item_data.abilities import AbilityContainer, AbilityEnum
from item_data.item_classes import Equipment, RandomEquipmentBuilder
from item_data.stat import Stat
from item_data.stat_modifier import StatModifierOperation, StatModifier

if typing.TYPE_CHECKING:
    from helpers.command import Command


def aa_deepest(adventure: Adventure):
    battle.qsab(adventure, Location.LAKE, 'C')
    battle.qsab(adventure, Location.LAKE, 'C')
    bc: BonusChapter = BonusChapter(tr(adventure.get_lang(), 'LAKE.EVENT2'))
    bc.add_persistent(Stat.HP, 20)
    adventure.add_chapter(bc)
    ability_ai: AbilityAI = AbilityAI([
        AbilityDecision(0, 1, AbilityContainer(AbilityEnum.CLAW, 0))
    ])
    boss: BotEntity = battle.rnd(adventure, Location.LAKE, 'BOSS', ability_ai)
    battle.qsbb(adventure, boss, icon=Emoji.WAVES,
                pre_text=[tr(adventure.get_lang(), 'LAKE.BOSS1'),
                          tr(adventure.get_lang(), 'LAKE.BOSS2'),
                          tr(adventure.get_lang(), 'LAKE.BOSS3')])
    item: Equipment = RandomEquipmentBuilder(0).set_location(Location.LAKE).build()
    adventure.add_chapter(ItemRewardChapter(item))


def ab_around(adventure: Adventure):
    battle.qsab(adventure, Location.LAKE, 'A')
    battle.qsab(adventure, Location.LAKE, 'C')
    if random.random() < 0.5:
        adventure.add_chapter(MoneyRewardChapter(random.randint(175, 225)))
    else:
        item: Equipment = RandomEquipmentBuilder(0).set_location(Location.ANYWHERE) \
            .choose_rarity([ItemRarity.RARE, ItemRarity.EPIC], [5, 2]).build()
        adventure.add_chapter(ItemRewardChapter(item))


def a_deep(adventure: Adventure):
    battle.qsab(adventure, Location.LAKE, 'B')
    battle.qsab(adventure, Location.LAKE, 'B')
    bc: BonusChapter = BonusChapter(tr(adventure.get_lang(), 'LAKE.EVENT1'))
    if random.random() < 0.5:
        bc.add_modifier(StatModifier(Stat.EVA, 3, StatModifierOperation.ADD))
    else:
        bc.add_modifier(StatModifier(Stat.CONT, 4, StatModifierOperation.ADD))
    bc.add_persistent(Stat.HP, 4)
    adventure.add_chapter(bc)
    adventure.add_chapter(ChoiceChapter(Emoji.LAKE, tr(adventure.get_lang(), 'LAKE.DECISION3_TEXT'))
                          .add_choice(Emoji.UP, tr(adventure.get_lang(), 'LAKE.DECISION3_OPTION1'), aa_deepest)
                          .add_choice(Emoji.RIGHT, tr(adventure.get_lang(), 'LAKE.DECISION3_OPTION2'), ab_around))


def b_before_reward(adventure: Adventure):
    battle.qsab(adventure, Location.LAKE, 'A')
    if random.random() < 0.5:
        adventure.add_chapter(MoneyRewardChapter(random.randint(75, 125)))
    else:
        item: Equipment = RandomEquipmentBuilder(0).set_location(Location.ANYWHERE) \
            .choose_rarity([ItemRarity.UNCOMMON, ItemRarity.RARE], [5, 2]).build()
        adventure.add_chapter(ItemRewardChapter(item))


def ba_pick(adventure: Adventure):
    if random.random() < 0.5:
        bc: BonusChapter = BonusChapter(tr(adventure.get_lang(), 'LAKE.DECISION2_RESULT1'))
        if random.random() < 0.5:
            bc.add_modifier(StatModifier(Stat.STR, 2, StatModifierOperation.ADD))
        else:
            bc.add_modifier(StatModifier(Stat.DEF, 2, StatModifierOperation.ADD))
        adventure.add_chapter(bc)
        battle.qsab(adventure, Location.LAKE, 'A')
    else:
        battle.qsab(adventure, Location.LAKE, 'B', pre_text=[tr(adventure.get_lang(), 'LAKE.DECISION2_RESULT2')])
    b_before_reward(adventure)


def bb_ignore(adventure: Adventure):
    battle.qsab(adventure, Location.LAKE, 'A')
    b_before_reward(adventure)


def b_around(adventure: Adventure):
    battle.qsab(adventure, Location.LAKE, 'A')
    battle.qsab(adventure, Location.LAKE, 'B')
    adventure.add_chapter(ChoiceChapter(Emoji.SEED, tr(adventure.get_lang(), 'LAKE.DECISION2_TEXT'))
                          .add_choice(Emoji.SEED, tr(adventure.get_lang(), 'LAKE.DECISION2_OPTION1'), ba_pick)
                          .add_choice(Emoji.RIGHT, tr(adventure.get_lang(), 'LAKE.DECISION2_OPTION2'), bb_ignore))


async def setup(_: 'Command', adventure: Adventure):
    battle.qsab(adventure, Location.LAKE, 'A')
    adventure.add_chapter(ChoiceChapter(Emoji.LAKE, tr(adventure.get_lang(), 'LAKE.DECISION1_TEXT'))
                          .add_choice(Emoji.UP, tr(adventure.get_lang(), 'LAKE.DECISION1_OPTION1'), a_deep)
                          .add_choice(Emoji.RIGHT, tr(adventure.get_lang(), 'LAKE.DECISION1_OPTION2'), b_around))
