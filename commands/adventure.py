from adventure_classes import coliseum
from helpers.command import Command


async def coliseum_start(cmd: Command):
    await coliseum.start(cmd.ctx, cmd.user)
