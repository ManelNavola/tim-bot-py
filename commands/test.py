from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle import BattleChapter, BattleTeam
from adventure_classes.generic.stat_modifier import StatModifierAdd
from enums.item_rarity import ItemRarity
from enums.item_type import ItemType
from enums.location import Location
from helpers.command import Command
from entities.bot_entity import BotEntityBuilder
from enums.emoji import Emoji
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
    cmd.user.user_entity.add_modifier(StatModifierAdd(Stat.EVA, 9999))
    cmd.user.user_entity.add_modifier(StatModifierAdd(Stat.STR, 9999))
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


async def test(cmd: Command):
    if FIGHT_BOT:
        potato = BotEntityBuilder('Potato', {
            Stat.HP: 50,
            Stat.STR: 1,
        })
        potate = BotEntityBuilder('Potate', {
            Stat.HP: 50,
            Stat.STR: 1,
        })
        hapi = BotEntityBuilder(':)', {
            Stat.HP: 200,
            Stat.STR: 4,
        })
        adventure: Adventure = Adventure("Test Adventure", Emoji.BANK)
        adventure.add_chapter(BattleChapter([
            BattleTeam(potato.name, [potato.instance(), potate.instance()]),
            BattleTeam(cmd.user.get_name(), [cmd.user.user_entity, hapi.instance()])
        ]))
        await adventure.start(cmd, [cmd.user])
    else:
        pass
        # if saved is None:
        #    saved = cmd.user
        # else:
        #    pass
        #    await cmd.guild.start_battle(cmd.ctx, cmd.user, opponent_user=saved)
