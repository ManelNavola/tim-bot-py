import typing

from adventure_classes.game_adventures import adventure_provider

if typing.TYPE_CHECKING:
    from helpers.command import Command


async def play_tutorial(cmd: 'Command', stage: int):
    if stage == 0:  # 0: class not chosen
        await adventure_provider.name_to_adventure['_tutorial'].start(cmd)
        return
