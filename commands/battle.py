from typing import Optional

from commands.command import Command
from guild_data.battle import Battle, BattleAction


async def action(cmd: Command, battle_action: BattleAction):
    battle: Optional[Battle] = cmd.guild.get_battle(cmd.user)
    if battle is None:
        await cmd.error("You are not in a battle!")
        return
    if not battle.action(cmd.user, battle_action):
        await cmd.error("It is not your turn yet!")
        return
    await cmd.send_hidden(battle.pop_log())
