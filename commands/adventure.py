from adventure_classes.game_adventures import coliseum, forest
from enums.location import Location
from helpers.command import Command


async def coliseum_start(cmd: Command):
    await forest.start(cmd.ctx, cmd.user)


async def start_adventure(cmd: Command, location: str):
    loc: Location = Location.get_from_name(location)
    if loc == Location.FOREST:
        await forest.start(cmd.ctx, cmd.user)
    else:
        await cmd.send_hidden(f"Unknown location: {location}")