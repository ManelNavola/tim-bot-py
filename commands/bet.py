import utils
from helpers.command import Command
from enums.emoji import Emoji
from guild_data.bet import Bet
from helpers.translate import tr


async def info(cmd: Command):
    bet1: str = tr(cmd.lang, 'BET.INFO1')
    bet2: str = tr(cmd.lang, 'BET.INFO2')
    await cmd.send_hidden(f"{bet1}\n{bet2}")


async def add(cmd: Command, money: int):
    was_not_active = not cmd.guild.bet.is_active()
    if was_not_active:
        if money < Bet.MIN_BET:
            await cmd.error(tr(cmd.lang, 'BET.MIN_BET', money=utils.print_money(cmd.lang, Bet.MIN_BET)))
            return
    if money < Bet.MIN_INCR:
        await cmd.error(tr(cmd.lang, 'BET.MIN_INCREASE', money=utils.print_money(cmd.lang, Bet.MIN_INCR)))
        return
    previous_bet = None
    if not was_not_active:
        previous_bet = cmd.guild.bet.get_bet(cmd.user.id)
    state, response = cmd.guild.bet.add_bet(cmd.user, money, cmd.ctx)
    if state:
        to_send = []
        if was_not_active:
            to_send.append(tr(cmd.lang, 'BET.CREATE', name=cmd.user.get_name(),
                              money=utils.print_money(cmd.lang, money), EMOJI_MONEY_FLY=Emoji.MONEY_FLY))
        else:
            if previous_bet == 0:
                to_send.append(tr(cmd.lang, 'BET.START', name=cmd.user.get_name(),
                                  money=utils.print_money(cmd.lang, money), EMOJI_MONEY_FLY=Emoji.MONEY_FLY))
            else:
                to_send.append(tr(cmd.lang, 'BET.INCREASE', name=cmd.user.get_name(),
                                  money=utils.print_money(cmd.lang, money + previous_bet),
                                  EMOJI_INCREASE=Emoji.INCREASE))
        if response:
            to_send.append(tr(cmd.lang, 'BET.INCREASE', name=response[1],
                              money=utils.print_money(cmd.lang, response[0]), EMOJI_INCREASE=Emoji.INCREASE))
        await cmd.send('\n'.join(to_send))
    else:
        if response:
            await cmd.error(tr(cmd.lang, 'BET.INCREASE', money=utils.print_money(cmd.lang, response)))
        else:
            await cmd.error(tr(cmd.lang, 'BET.LACK', money=utils.print_money(cmd.lang, response)))


async def check(cmd: Command):
    if cmd.guild.bet.is_active():
        await cmd.send(cmd.guild.bet.print())
    else:
        await cmd.send_hidden(tr(cmd.lang, 'BET.NO_BET'))
