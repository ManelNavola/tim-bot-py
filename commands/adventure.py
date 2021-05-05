from adventure_classes.game_adventures import forest
from enums.location import Location
from helpers.command import Command
from helpers.translate import tr


async def start_adventure(cmd: Command, location: str):
    loc: Location = Location.get_from_name(location)
    if loc == Location.FOREST:
        await forest.start(cmd.ctx, cmd.user)
    else:
        await cmd.send_hidden(tr(cmd.lang, 'COMMANDS.ADVENTURE.UNKNOWN', location=location))
