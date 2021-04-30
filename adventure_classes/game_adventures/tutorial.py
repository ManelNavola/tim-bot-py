import typing
from collections import Callable

from adventure_classes.game_adventures.forest import ChoiceChapter
from adventure_classes.generic import battle
from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle import BattleChapterWithText
from adventure_classes.generic.chapter import Chapter
from enums.emoji import Emoji
from enums.location import Location
from enums.user_class import UserClass
from user_data.user import User

if typing.TYPE_CHECKING:
    from helpers.command import Command


class TutorialClassChapter(ChoiceChapter):
    def __init__(self):
        super().__init__(Emoji.WAVES, '')

    @staticmethod
    def choose_class(uc: UserClass) -> Callable:
        def a(adventure: Adventure):
            user: User = adventure.get_user()
            user.set_class(uc)
        return a

    async def init(self) -> None:
        await self.append_and_wait("You wake up in a boat...", 2)
        await self.append_and_wait("Your mind is empty, but you remember you were a...", 2)
        for uc in UserClass:
            self.add_choice(uc.get_icon(), uc.get_name(), self.choose_class(uc))
        await super().init()


class TutorialEndChapter(Chapter):
    def __init__(self):
        super().__init__(Emoji.TUTORIAL)
        self.hidden = True

    async def init(self) -> None:
        await self.end()

    async def end(self, lost: bool = False, skip: bool = False) -> None:
        await super().end(lost, True)
        user: User = self.get_adventure().get_user()
        user.set_tutorial_stage(-1)


async def start(cmd: 'Command', user: User):
    adventure: Adventure = Adventure("Tutorial", Emoji.TUTORIAL)
    adventure.add_chapter(TutorialClassChapter())
    bcwt = BattleChapterWithText(['As you get closer to the shore, you see something fly down from the sky...'])
    adventure.add_chapter(battle.q1v1(user.user_entity, battle.rnd(adventure, Location.TUTORIAL), bcwt))
    adventure.add_chapter(TutorialEndChapter())

    await adventure.start(cmd, [user])
