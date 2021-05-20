from adventure_classes.game_adventures import adventure_provider
from helpers.command import Command
from helpers.translate import tr


async def start_adventure(cmd: Command, location: str):
    if location in adventure_provider.name_to_adventure:
        await adventure_provider.name_to_adventure[location].start(cmd)
    else:
        await cmd.send_hidden(tr(cmd.lang, 'COMMANDS.ADVENTURE.UNKNOWN', location=location))
