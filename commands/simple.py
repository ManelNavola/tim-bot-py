import discord

import utils
from adventure_classes.game_adventures import adventure_provider
from adventure_classes.generic.battle.battle import BattleChapter
from adventure_classes.generic.battle.battle_group import BattleGroup
from enemy_data import enemy_utils
from enums.emoji import Emoji
from enums.location import Location
from enums.user_class import UserClass
from helpers.command import Command
from helpers import storage
from helpers.translate import tr


async def inv(cmd: Command):
    await cmd.send_hidden(cmd.user.print(cmd.lang, private=True, checking=False))


async def post_inv(cmd: Command):
    await cmd.send(cmd.user.print(cmd.lang, private=True, checking=cmd.user.get_name()))


async def check(cmd: Command, user: discord.Member):
    if user.id in [824935594509336576, 824720383596560444]:
        await cmd.send("._.")
        return

    user_m = storage.get_user(cmd.db, user.id, False)
    if not user_m:
        await cmd.send_hidden(tr(cmd.lang, 'COMMAND.CHECK.NO_INTERACTION'))
        return
    await cmd.send(user_m.print(cmd.lang, private=False, checking=True))


async def duel(cmd: Command, user: discord.Member):
    if user.id in [824935594509336576, 824720383596560444]:
        await cmd.send_hidden("Sure, bring it on.")
        await adventure_provider.quick_adventure(cmd, [cmd.user], 'Tim Lord Duel', Emoji.DEAD, 0, [
            BattleChapter(BattleGroup(users=[cmd.user]),
                          BattleGroup([enemy_utils.get_random_enemy(Location.NOWHERE, 'TIM').instance()]))
        ])
        return

    user_m = storage.get_user(cmd.db, user.id, False)
    user_m.member = user
    if not user_m:
        await cmd.send_hidden(tr(cmd.lang, 'COMMAND.CHECK.NO_INTERACTION'))
        return
    await adventure_provider.name_to_adventure['_duel'].start(cmd, [cmd.user], {
        'duel_user': user_m
    })


async def transfer(cmd: Command):
    if cmd.user.get_bank() == 0:
        await cmd.error(tr(cmd.lang, 'COMMAND.TRANSFER.EMPTY'))
    else:
        transferred = cmd.user.withdraw_bank()
        if transferred == 0:
            await cmd.error(tr(cmd.lang, 'COMMAND.TRANSFER.FULL'))
        else:
            await cmd.send_hidden(tr(cmd.lang, 'COMMAND.TRANSFER.EXECUTE', EMOJI_BANK=Emoji.BANK,
                                     money=utils.print_money(cmd.lang, transferred),
                                     total=utils.print_money(cmd.lang, cmd.user.get_money())))


async def leaderboard(cmd: Command):
    await cmd.send(cmd.guild.print_leaderboard())


async def stats(cmd: Command):
    if cmd.user.get_class_index() == -1:
        await cmd.send_hidden('You have no stats yet...')
    else:
        ts: str = cmd.user.user_entity.print_detailed()
        uc: UserClass = UserClass.get_from_id(cmd.user.get_class_index())
        await cmd.send_hidden(f"{uc.get_icon()} {uc.get_name(cmd.lang)}\n{ts}")


async def abilities(cmd: Command):
    tp = []
    # for item in cmd.user.inventory.get_equipment():
    #     if item.data.ability is not None:
    #         tp.append(f"{item.data.get_description().type.get_type_icon()} {item.data.ability.get_name()}: "
    #                   f"{item.data.ability.get_effect()} (once per battle)")
    if not tp:
        await cmd.send_hidden("You currently have no abilities equipped")
    else:
        await cmd.send_hidden('\n'.join(tp))
