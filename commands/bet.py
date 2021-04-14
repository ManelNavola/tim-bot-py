import utils
from helpers.command import Command
from enums.emoji import Emoji
from guild_data.bet import Bet


BET_INFO = "Bet money with other users against the bot to win the Jackpot! " \
           "Each bot has a different behaviour, can you overcome their betting strategy?"


async def info(cmd: Command):
    await cmd.send_hidden(BET_INFO)


async def add(cmd: Command, money: int):
    was_not_active = not cmd.guild.bet.is_active()
    if was_not_active:
        if money < Bet.MIN_BET:
            await cmd.error(f"Starting bet must be at least {utils.print_money(Bet.MIN_BET)}!")
            return
    if money < Bet.MIN_INCR:
        await cmd.error(f"The minimum bet increase is of {utils.print_money(Bet.MIN_INCR)}!")
        return
    previous_bet = None
    if not was_not_active:
        previous_bet = cmd.guild.bet.get_bet(cmd.user.id)
    state, response = cmd.guild.bet.add_bet(cmd.user, money, cmd.ctx)
    if state:
        to_send = []
        if was_not_active:
            to_send.append(f"{cmd.user.get_name()} started a bet with {utils.print_money(money)}! "
                           f"{Emoji.MONEY_FLY}")
        else:
            if previous_bet == 0:
                to_send.append(f"{cmd.user.get_name()} has bet {utils.print_money(money)} {Emoji.MONEY_FLY}")
            else:
                to_send.append(f"{cmd.user.get_name()} has increased their bet "
                               f"to {utils.print_money(money + previous_bet)} {Emoji.INCREASE}")
        if response:
            to_send.append(f"{response[1]} has increased their bet to {utils.print_money(response[0])} "
                           f"{Emoji.INCREASE}")
        await cmd.send('\n'.join(to_send))
    else:
        if response:
            await cmd.error(f"Your bet cannot increase {utils.print_money(response)}!")
        else:
            await cmd.error(f"You don't have {utils.print_money(money)}!")


async def check(cmd: Command):
    if cmd.guild.bet.is_active():
        await cmd.send(cmd.guild.bet.print())
    else:
        await cmd.send_hidden("No ongoing bet at the moment")
