import typing

from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle import battle
from adventure_classes.generic.chapter import Chapter
from enums.emoji import Emoji
from user_data.user import User
if typing.TYPE_CHECKING:
    from helpers.command import Command


class DuelWinnerChapter(Chapter):
    def __init__(self):
        super().__init__(Emoji.CLOCK)
        self.hidden = True

    async def init(self):
        if self.get_adventure().lost:
            self.get_adventure().end_override_text = f"{self.get_adventure().saved_data['duel_user'].get_name()} " \
                                                     f"won the duel!"
        else:
            self.get_adventure().end_override_text = f"{self.get_adventure().get_users()[0].get_name()} " \
                                                     f"won the duel!"
        await self.end(skip=True)


class DuelAwaitChapter(Chapter):
    def __init__(self):
        super().__init__(Emoji.CLOCK)
        self.duel_user: typing.Optional[User] = None

    async def click_tick(self, user: User):
        if user == self.get_adventure().saved_data['duel_user']:
            self.get_adventure().saved_data['duel_user'].join_adventure(self.get_adventure())
            battle.qtvt(self.get_adventure(),
                        [self.get_adventure().get_users()[0]],
                        [self.duel_user])
            self.get_adventure().add_chapter(DuelWinnerChapter())
            await self.end(skip=True)

    async def click_cross(self):
        await self.end(skip=True)

    async def init(self):
        self.duel_user = self.get_adventure().saved_data['duel_user']
        self.add_log(f"Waiting for {self.duel_user.member.mention}...")
        self.get_adventure().get_message().register(self.duel_user.id)
        await self.send_log()
        await self.get_adventure().add_reaction(Emoji.TICK, self.click_tick)
        await self.get_adventure().add_reaction(Emoji.CROSS, self.click_cross)


async def setup(cmd: 'Command', adventure: Adventure):
    adventure.start_override_text = f"{cmd.user.get_name()} challenged " \
                                    f"{adventure.saved_data['duel_user'].get_name()} to a duel!"
    adventure.add_chapter(DuelAwaitChapter())
