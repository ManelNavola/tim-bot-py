import random
from typing import Callable

from discord_slash import SlashContext

from adventure_classes.generic import battle
from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.chapter import Chapter
from adventure_classes.generic.stat_modifier import StatModifier
from enums.emoji import Emoji
from enums.location import Location
from item_data.stat import Stat
from user_data.user import User


class BonusChapter(Chapter):
    def __init__(self, text: str):
        super().__init__(Emoji.BOX)
        self._text: str = text
        self._bonus: list[StatModifier] = []
        self._persistent_bonus: list[tuple[Stat, int]] = []

    def add_modifier(self, modifier: StatModifier):
        self._bonus.append(modifier)

    def add_persistent(self, stat: Stat, value: int):
        self._persistent_bonus.append((stat, value))

    async def init(self):
        self.add_log(self._text)
        for bonus in self._bonus:
            if bonus.duration < 0:
                self.add_log(f"{bonus.print()} {bonus.stat.get_abv()} for the whole adventure")
            else:
                self.add_log(f"+{bonus.print()} {bonus.stat.get_abv()} for the next {bonus.duration} battles")
        for bonus in self._persistent_bonus:
            stat: Stat = bonus[0]
            amount: int = bonus[1]
            users: list[User] = self.get_adventure().get_users().keys()
            for user in users:
                old_value = user.user_entity.get_persistent(stat)
                if old_value:
                    user.user_entity.change_persistent(stat, old_value + amount)
                    new_value = user.user_entity.get_persistent(stat)
                    self.add_log(f"+{amount} {stat.get_abv()} ({old_value} {Emoji.ARROW_RIGHT} {new_value})")
        await self.pop_log()
        await self.end()


class ChoiceChapter(Chapter):
    def __init__(self, emoji: Emoji, msg: str):
        super().__init__(emoji)
        self.msg: str = msg
        self.choices: list[tuple[Emoji, str, Callable]] = []

    def add_choice(self, icon: Emoji, desc: str, result: Callable):
        self.choices.append((icon, desc, result))
        return self

    async def init(self):
        self.add_log(self.msg)
        for choice in self.choices:
            self.add_log(f"{choice[0].first()} {choice[1]}")
        await self.pop_log()
        for choice in self.choices:
            await self.get_adventure().add_reaction(choice[0], self.choose_path(choice[2]))

    def choose_path(self, action: Callable):
        async def end_path():
            action(self.get_adventure())
            await self.end(skip=True)

        return end_path


def aa_deeper(adventure):
    battle.add_to_adventure(adventure, Location.FOREST, 'C')
    # TODO: BONUS STR/EVA
    battle.add_to_adventure(adventure, Location.FOREST, 'C')
    # TODO: CHOICE 40% -SPD, 30% SPD, 30% hp
    battle.add_to_adventure(adventure, Location.FOREST, 'B')
    battle.add_to_adventure(adventure, Location.FOREST, 'BOSS')


def ab_continue_path(adventure):
    # TODO: BONUS HP/DEF
    battle.add_to_adventure(adventure, Location.FOREST, 'A')
    battle.add_to_adventure(adventure, Location.FOREST, 'C')
    # TODO: REWARD


def a_deep(adventure):
    battle.add_to_adventure(adventure, Location.FOREST, 'B')
    battle.add_to_adventure(adventure, Location.FOREST, 'B')
    adventure.add_chapter(ChoiceChapter(Emoji.FOREST, 'You find a path without any light:')
                          .add_choice(Emoji.UP, 'Venture the darkest, deepest part of the forest', aa_deeper)
                          .add_choice(Emoji.RIGHT, 'Continue your journey', ab_continue_path))


def ba_bear(adventure):
    if random.random() < 2:
        battle.add_to_adventure(adventure, Location.FOREST, 'D', message='The bear woke up!').icon = Emoji.BEAR
    else:
        battle.add_to_adventure(adventure, Location.FOREST, 'A')
    # TODO: REWARD


def bb_around_bear(adventure):
    battle.add_to_adventure(adventure, Location.FOREST, 'A')
    battle.add_to_adventure(adventure, Location.FOREST, 'B')
    # TODO: REWARD


def b_around(adventure):
    bc = BonusChapter('You find some healing roots...')
    bc.add_persistent(Stat.HP, 15)
    adventure.add_chapter(bc)
    battle.add_to_adventure(adventure, Location.FOREST, 'B')
    adventure.add_chapter(ChoiceChapter(Emoji.BEAR, 'You find a sleeping bear blocking your path:')
                          .add_choice(Emoji.UP, 'Try to sneak past the bear', ba_bear)
                          .add_choice(Emoji.RIGHT, 'Find another path', bb_around_bear))


async def start(ctx: SlashContext, user: User):
    adventure: Adventure = Adventure("Forest", Emoji.FOREST)

    battle.add_to_adventure(adventure, Location.FOREST, 'A')
    battle.add_to_adventure(adventure, Location.FOREST, 'A')
    adventure.add_chapter(ChoiceChapter(Emoji.GARDEN, 'You find yourself at an intersection:')
                          .add_choice(Emoji.UP, 'Go deep into the forest', a_deep)
                          .add_choice(Emoji.RIGHT, 'Go around the forest', b_around))

    await adventure.start(ctx, [user])
