from adventure_classes.game_adventures.adventure_provider import AdventureInstance
from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle.battle import BattleChapter, BattleGroupUsers, BattleGroup
from adventure_classes.generic.stat_modifier import StatModifierAdd
from entities.bot_entity import BotEntity
from enums.emoji import Emoji
from enums.item_rarity import ItemRarity
from enums.item_type import ItemType
from enums.location import Location
from helpers.command import Command
from item_data import item_utils
from item_data.stat import Stat

FIGHT_BOT: bool = True


async def rich(cmd: Command):
    for upg_name in cmd.user.upgrades:
        upg = cmd.user.upgrades[upg_name]
        while not upg.is_max_level():
            upg.level_up()
    cmd.user.add_money(999999999999)
    await cmd.send_hidden("capitalism ho")


async def heal(cmd: Command):
    cmd.user.user_entity.add_battle_modifier(StatModifierAdd(Stat.EVA, 9999))
    cmd.user.user_entity.add_battle_modifier(StatModifierAdd(Stat.STR, 9999))
    await cmd.send_hidden("cheater...")


async def gimme_all(cmd: Command, tier: str = '0', location: str = 'Anywhere', rarity: str = 'Common'):
    cmd.user.inventory.unequip_all()
    cmd.user.inventory.sell_all()
    tier = int(tier)
    location = Location.get_from_name(location)
    rarity = ItemRarity.get_from_name(rarity)
    i = 0
    for x in ItemType:
        item = item_utils.RandomItemBuilder(tier).set_location(location).set_rarity(rarity).set_type(x).build()
        cmd.user.inventory.create_item(item)
        i += 1
    cmd.user.inventory.equip_best()
    await cmd.send_hidden("epic")


async def setup(_: 'Command', adventure: Adventure):
    be: BotEntity = BotEntity('potato bad 1', {
        Stat.HP: 40,
        Stat.STR: 2,
        Stat.DEF: 2,
    })
    be2: BotEntity = BotEntity('potato bad 2', {
        Stat.HP: 40,
        Stat.STR: 2,
        Stat.DEF: 2,
    })
    be3: BotEntity = BotEntity('potato good', {
        Stat.HP: 40,
        Stat.STR: 2,
        Stat.DEF: 2,
    })
    adventure.add_chapter(BattleChapter(BattleGroupUsers(entities=[be3]), BattleGroup([be, be2])))


async def test(cmd: Command):
    adv = AdventureInstance(setup, 'TEST', Emoji.SPARKLE, tokens=0)
    await adv.start(cmd)
