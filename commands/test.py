from typing import Optional

from adventure_classes.game_adventures.adventure_provider import AdventureInstance
from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle import battle
from entities.ai.ability_ai import AbilityAI, AbilityDecision
from entities.bot_entity import BotEntity
from enums.emoji import Emoji
from enums.item_rarity import ItemRarity
from enums.item_type import EquipmentType
from enums.location import Location
from helpers.command import Command
# from item_data import item_utils
from item_data.abilities import AbilityContainer, AbilityEnum
from item_data.item_classes import RandomEquipmentBuilder, Item
from item_data.stat import Stat
from item_data.stat_modifier import StatModifierOperation, StatModifier
from user_data.inventory import SlotType

FIGHT_BOT: bool = True


async def rich(cmd: Command):
    for upg_name in cmd.user.upgrades:
        upg = cmd.user.upgrades[upg_name]
        while not upg.is_max_level():
            upg.level_up()
    cmd.user.add_money(999999999999)
    await cmd.send_hidden("capitalism ho")


async def invincible(cmd: Command):
    cmd.user.user_entity.add_modifier(StatModifier(Stat.EVA, 9999, StatModifierOperation.ADD))
    await cmd.send_hidden("invincible...")


def _gimme(tier: str = '0', location: str = 'Anywhere', rarity: str = 'Common', subtype: str = 'Boots') -> Item:
    tier = int(tier)
    location = Location.from_name(location)
    rarity = ItemRarity.from_name(rarity)
    subtype = EquipmentType.from_name(subtype)
    return RandomEquipmentBuilder(tier).set_location(location).set_rarity(rarity).set_type(subtype).build()


async def gimme(cmd: Command, tier: str = '0', location: str = 'Anywhere', rarity: str = 'Common',
                subtype: str = 'Boots'):
    slot: Optional[str] = cmd.user.inventory.get_empty_slot(SlotType.ITEMS)
    if slot is None:
        await cmd.error("Full lmao")
        return
    item = _gimme(tier, location, rarity, subtype)
    cmd.user.inventory.add_item(item, slot)
    await cmd.send_hidden("nice")


async def gimme_all(cmd: Command, tier: str = '0', location: str = 'Anywhere', rarity: str = 'Common'):
    for et in EquipmentType:
        slot: Optional[str] = cmd.user.inventory.get_empty_slot(SlotType.ITEMS)
        if slot is None:
            await cmd.error("Full lmao")
            return
        item = _gimme(tier, location, rarity, et.get_name())
        cmd.user.inventory.add_item(item, slot)
    await cmd.send_hidden("epic")


async def relshop(cmd: Command):
    cmd.guild.reload_shop()
    await cmd.send_hidden(f"{Emoji.SHOP}")


async def tokenize(cmd: Command):
    cmd.user.set_tokens(5)
    await cmd.send_hidden(f"{Emoji.TOKEN}")


async def setup(_: 'Command', adventure: Adventure):
    ability_ai: AbilityAI = AbilityAI([
        AbilityDecision(0, 0.5, AbilityContainer(AbilityEnum.SUMMON, 100), max_uses=1)
    ])
    boss: BotEntity = battle.rnd(adventure, Location.FOREST, 'BOSS', ability_ai)
    battle.qcsab(adventure, boss, icon=Emoji.FOREST)


async def test(cmd: Command):
    adv = AdventureInstance(setup, 'TEST', Emoji.SPARKLE, tokens=0)
    await adv.start(cmd)
