import typing
from collections import Callable

from adventure_classes.generic import battle
from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle import BattleChapterWithText
from adventure_classes.generic.chapter import Chapter
from adventure_classes.generic.choice import ChoiceChapter
from adventure_classes.generic.reward import ItemRewardChapter
from enums.emoji import Emoji
from enums.item_rarity import ItemRarity
from enums.location import Location
from enums.user_class import UserClass
from helpers.translate import tr
from item_data.item_utils import RandomItemBuilder
from user_data.user import User

if typing.TYPE_CHECKING:
    from helpers.command import Command


class TutorialBattleChapter(BattleChapterWithText):
    def _print_current_prefix(self):
        super()._print_current_prefix()
        if not self._finished:
            self.add_log(tr(self.get_lang(), 'TUTORIAL.ATTACK', EMOJI_BATTLE=Emoji.BATTLE))

    async def end(self, lost: bool = False, skip: bool = False) -> None:
        await self.append(tr(self.get_lang(), 'TUTORIAL.BATTLE_END', EMOJI_OK=Emoji.OK))
        await super().end(lost, skip)


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
        await self.append_and_wait(tr(self.get_lang(), "TUTORIAL.WAKE"), 2)
        await self.append_and_wait(tr(self.get_lang(), "TUTORIAL.REMEMBER"), 2)
        for uc in UserClass:
            self.add_choice(uc.get_icon(), uc.get_name(self.get_lang()), self.choose_class(uc))
        await super().init()


class TutorialEndChapter(Chapter):
    def __init__(self):
        super().__init__(Emoji.TUTORIAL)
        self.hidden = True

    async def init(self) -> None:
        self.add_log(tr(self.get_lang(), "TUTORIAL.CONGRATULATIONS", name=self.get_adventure().get_user().get_name()))
        self.add_log(tr(self.get_lang(), "TUTORIAL.TOKENS", tokens=self.get_adventure().get_user().get_tokens(),
                        EMOJI_TOKEN=Emoji.TOKEN))
        await self.send_log(tr(self.get_lang(), "TUTORIAL.REFERENCE", command="/guide"))
        user: User = self.get_adventure().get_user()
        user.set_tutorial_stage(-1)
        await self.end()


async def start(cmd: 'Command', user: User):
    adventure: Adventure = Adventure(tr(cmd.lang, 'TUTORIAL.NAME'), Emoji.TUTORIAL,
                                     override_str=tr(cmd.lang, "TUTORIAL.WELCOME",
                                                     name=user.get_name(),
                                                     bot_name="Tim Bot"))
    adventure.add_chapter(TutorialClassChapter())
    tbc = TutorialBattleChapter([tr(cmd.lang, "TUTORIAL.SEAGULL")])
    adventure.add_chapter(battle.q1v1(cmd.lang, user.user_entity, battle.rnd(adventure, Location.TUTORIAL), tbc))
    adventure.add_chapter(TutorialEndChapter())
    adventure.add_chapter(ItemRewardChapter(RandomItemBuilder(0).set_rarity(ItemRarity.COMMON).build()))

    await adventure.start(cmd, [user])
