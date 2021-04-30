import typing

from adventure_classes.game_adventures import tutorial

if typing.TYPE_CHECKING:
    from helpers.command import Command


async def play_tutorial(cmd: 'Command', stage: int):
    if stage == 0:  # 0: class not chosen
        await tutorial.start(cmd, cmd.user)
        return
