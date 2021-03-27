from commands.command import Command
import utils

MIN_BET = 100
MIN_BET_STR = utils.print_money(MIN_BET)
MIN_INCR = 10
MIN_INCR_STR = utils.print_money(MIN_INCR)

async def info(cmd: Command):
    await cmd.send("Bet money against the bot to win the Jackpot! The bot will always bid double of the maximum bet.", hidden=True)

async def add(cmd: Command, amount: int):
    start_bet = not cmd.guild.check_ongoing_bet()
    user_id = cmd.user.id
    if start_bet:
        if amount < MIN_BET:
            await cmd.send(f"Start bet is minimum of {MIN_BET_STR}!", hidden=True)
            return
    if amount < 0:
        await cmd.send(f"The minimum bet increase is of {MIN_INCR_STR}!", hidden=True)
        return
    if amount > cmd.user.get_money():
        amount_str = utils.print_money(amount)
        await cmd.send(f"You don't have {amount_str}!", hidden=True)
        return
    if start_bet:
        cmd.guild.start_bet()
    amount_str = utils.print_money(amount)
    if cmd.user.change_money(-amount):
        post = []
        current_bet = cmd.guild.get_bet(user_id)
        if current_bet == 0:
            if start_bet:
                post.append(cmd.user_name + f" started a bet!")
            post.append(cmd.user_name + f" bet {amount_str}!")
        else:
            final_bet_str = utils.print_money(current_bet + amount)
            post.append(cmd.user_name + f" increased their bet to {final_bet_str}!")
        bot_bet = cmd.guild.add_bet(user_id, cmd.user_name, amount)
        if bot_bet:
            bot_bet_str = utils.print_money(bot_bet)
            post.append(f"Bot's bet increased to {bot_bet_str}")
        if cmd.guild.update_last_bet_info():
            post.append(cmd.guild.get_bet_info())
        await cmd.send('\n'.join(post))
    if start_bet:
        await cmd.guild.run_bet(cmd)

async def check(cmd: Command):
    await cmd.send(cmd.guild.get_bet_info())