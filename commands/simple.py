from commands.command import Command
from data import users
import utils
import discord

async def inv(cmd: Command):
    money_str = utils.print_money(cmd.user.get_money())
    await cmd.send(f"**Money**: You have {money_str} (+$1/min)")

async def check(cmd: Command, member: discord.Member):
    user = users.get(str(member.id), False)
    if not user:
        await cmd.send(f"This user hasn't interacted with me yet")
        return
    money_str = utils.print_money(user.get_money())
    await cmd.send(f"""{member.name} profile:\n**Money**: {money_str}""")