from commands.command import Command
import utils

async def place(cmd: Command, amount: int):
    must_start = not cmd.guild.check_bet()
    user_id = cmd.user.id
    if amount < 10:
        await cmd.send("Minimum bet amount is 10!", hidden=True)
        return
    if amount > cmd.user.get_money():
        amount_str = utils.print_money(amount)
        await cmd.send(f"You don't have {amount_str}!", hidden=True)
        return
    if must_start:
        cmd.guild.start_bet()
    current_bet = cmd.guild.get_bet(user_id)
    if amount <= current_bet:
        current_bet = utils.print_money(current_bet)
        await cmd.send("You must bet higher than your current bet ({current_bet})!", hidden=True)
        return
    diff = amount - current_bet
    amount_str = utils.print_money(amount)
    if cmd.user.change_money(-diff):
        post = []
        if current_bet == 0:
            if must_start:
                post.append(cmd.user_name + f" started a bet!")
            post.append(cmd.user_name + f" bet {amount_str}!")
        else:
            post.append(cmd.user_name + f" increased their bet to {amount_str}!")
        cmd.guild.set_bet(user_id, cmd.user_name, amount)
        if cmd.guild.update_last_bet_info():
            post.append(cmd.guild.get_bet_info())
        await cmd.send('\n'.join(post))
    else:
        diff = utils.print_money(diff)
        await cmd.send("You don't have {diff}!", hidden=True)
    if must_start:
        await cmd.guild.run_bet(cmd)

async def check(cmd: Command):
    await cmd.send(cmd.guild.get_bet_info())