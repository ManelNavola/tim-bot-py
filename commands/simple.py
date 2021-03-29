from commands.command import Command
from data import users
import utils
import discord

async def inv(cmd: Command):
    await cmd.send_hidden(cmd.user.print_inventory(private=True))

async def postinv(cmd: Command):
    await cmd.send(cmd.user.print_inventory(checking=cmd.user.get_name(), private=True))

async def check(cmd: Command, member: discord.Member):
    user = users.get(member.id, False)
    if not user:
        await cmd.send(f"This user hasn't interacted with me yet")
        return
    await cmd.send(user.print_inventory(checking=member.name, private=False))

async def transfer(cmd: Command):
    transfer = cmd.user.transfer()
    await cmd.send_hidden(transfer)