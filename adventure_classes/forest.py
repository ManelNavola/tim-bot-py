from discord_slash import SlashContext

from adventure_classes.adventure import Adventure, Chapter
from adventure_classes.battle import BattleChapter
from enemy_data import enemy_utils
from enums.emoji import Emoji
from enums.location import Location
from user_data.user import User


class PathChapter(Chapter):
    _PATHS: list[str] = ["In front of you there is",
                         "To the right,",
                         "On your left,",
                         "And behind you there's"]
    _PATH_NAMES: list[str] = ['front', 'right', 'left', 'behind']
    _ARROWS: list[Emoji] = [Emoji.UP, Emoji.RIGHT, Emoji.LEFT, Emoji.DOWN]

    async def init(self, user: 'User'):
        self.add_log("You find yourself at an intersection:")
        for i in range(len(self.paths)):
            self.add_log(PathChapter._PATHS[i] + ' ' + self.paths[i])
        await self.pop_log()
        for i in range(len(self.paths)):
            await self.message.add_reaction(PathChapter._ARROWS[i], self.choose_path(i))

    def choose_path(self, path: int):
        async def end_path():
            self._adventure.saved_data['path'] = path
            await self.send_log(f"You chose the {PathChapter._PATH_NAMES[path]} path")
            await self.end()
        return end_path

    def __init__(self, emoji: Emoji, paths: list[str]):
        super().__init__(emoji)
        self.paths: list[str] = paths


async def start(ctx: SlashContext, user: User):
    adventure: Adventure = Adventure("Forest", Emoji.GARDEN.value)
    adventure.saved_data['enemy_id'] = None
    for i in range(2):
        enemy = enemy_utils.get_random_enemy(Location.FOREST, 'B', last_chosen_id=adventure.saved_data['enemy_id'])
        adventure.saved_data['enemy_id'] = enemy.enemy_id
        adventure.add_chapter(BattleChapter(enemy.instance()))
    adventure.add_chapter(PathChapter(Emoji.GARDEN,
                                      ['a path that goes deep into the forest',
                                       'a path that goes around the forest']))
    await user.start_adventure(ctx, adventure)
