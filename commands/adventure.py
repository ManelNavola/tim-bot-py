from adventure_classes import coliseum, forest
from helpers.command import Command


async def coliseum_start(cmd: Command):
    await coliseum.start(cmd.ctx, cmd.user)


async def start_adventure(cmd: Command, location: str):
    if location == 'forest':
        await forest.start(cmd.ctx, cmd.user)
