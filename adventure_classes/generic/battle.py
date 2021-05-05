import asyncio
import random
from asyncio import Event
from typing import Optional, Coroutine

from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle_entity import BattleEntity
from adventure_classes.generic.chapter import Chapter
from enemy_data import enemy_utils
from entities.bot_entity import BotEntityBuilder
from entities.entity import Entity
from enums.emoji import Emoji
from enums.location import Location
from helpers.timer import DelayTask
from helpers.translate import tr
from item_data.stat import Stat
from user_data.user import User


class BattleTeam:
    def __init__(self, name: str, entities: list[Entity], affiliation: Optional[int] = None):
        self.entities: list[BattleEntity] = [BattleEntity(entity) for entity in entities]
        self.users: list[BattleEntity] = [be for be in self.entities if be.is_user()]
        self.entity_dict: dict[Entity, BattleEntity] = {be.entity: be for be in self.entities}
        self.user_acted: set[BattleEntity] = set()
        self.bots: list[BattleEntity] = [be for be in self.entities if not be.is_user()]
        self.name: str = name
        self.affiliation: int = affiliation
        self.joint_speed: float = sum([entity.get_stat_value(Stat.SPD) for entity in entities]) / len(entities)
        self.speed_advantage: float = 1.0
        self.last_target: dict[BattleEntity, BattleEntity] = {}

    def any_user_alive(self):
        return any((not x.is_dead()) for x in self.users)

    def any_bot_alive(self):
        return any((not x.is_dead()) for x in self.bots)


class BattleChapter(Chapter):
    INCREASE_EVERY: int = 8

    def __init__(self):
        super().__init__(Emoji.BATTLE)
        self._teams: list[Optional[BattleTeam]] = []
        self._team_affiliations: dict[Optional[int], list[BattleTeam]] = {}
        self._user_entities: list[BattleEntity] = []
        self._chosen_target: dict[BattleEntity, BattleEntity] = {}
        self._turn: int = -1
        self._round: int = 1
        self._lowest_speed: float = 0.0
        self._pass_turn: Optional[DelayTask] = None
        self._last_messages: list[str] = []
        self._saved_last_message: str = ''
        self._current_team: Optional[BattleTeam] = None
        self._available_targets: list[BattleEntity] = []
        self._max_targets: int = 1
        self._only_bots: bool = False
        self._coroutines: list[Coroutine] = []
        self._event: Event = Event()
        self._finished: bool = False
        self._started: bool = False

    def get_round(self) -> int:
        return self._round

    def add_team(self, team: BattleTeam) -> None:
        assert not self._started, "Cannot add team after the game has started (yet?)"
        self._teams.append(team)

    async def init(self) -> None:
        # Setup
        self._started = True

        affiliations_with_users: int = 0
        for aff, teams in self._team_affiliations.items():
            for team in teams:
                if team.users:
                    affiliations_with_users += 1
                    break
        if affiliations_with_users > 1:
            self._max_targets = max(len(team.entities) for team in self._teams)
        else:
            self._max_targets = max(len(team.entities) for team in self._teams if not team.users)

        self._lowest_speed = min([team.joint_speed for team in self._teams])

        for team in self._teams:
            self._team_affiliations[team.affiliation] = self._team_affiliations.get(team.affiliation, []) + [team]
        self._teams.sort(key=lambda x: x.speed_advantage, reverse=True)
        for team in self._teams:
            self._user_entities += team.users

        actions: set[Emoji] = {Emoji.BATTLE}
        for team in self._teams:
            for be in team.entities:
                be.set_battle_instance(self)
        for ue in self._user_entities:
            actions |= ue.get_actions()
        for action in actions:
            await self.get_adventure().add_reaction(action, self.execute_action)
        if self._max_targets > 1:
            for i in range(self._max_targets):
                emoji = Emoji.get_number(i + 1)
                await self.get_adventure().add_reaction(emoji, self.select_target)
        self._coroutines.append(self.next_turn())
        while not self._finished:
            await self._coroutines.pop(0)
            await self._event.wait()
            self._event.clear()

    async def select_target(self, user: User, emoji: Emoji) -> None:
        if (self._pass_turn is None) or (not self._pass_turn.is_running()):
            return
        user_be: Optional[BattleEntity] = self._current_team.entity_dict.get(user.user_entity)
        if user_be:
            if user_be not in self._current_team.user_acted:
                target_index: int = emoji.get_number_value() - 1
                if target_index < len(self._available_targets):
                    be: BattleEntity = self._available_targets[target_index]
                    if be.is_dead():
                        return
                    self._chosen_target[self._current_team.entity_dict[user.user_entity]] = be
                    self._current_team.last_target[self._current_team.entity_dict[user.user_entity]] = be
                    await self._print_current()
        await self.get_adventure().remove_reaction(user, emoji)

    async def _perform_action(self, be: BattleEntity, action: Emoji, target_entity: Optional[BattleEntity]) -> str:
        msg: str = be.try_action(action, target_entity)
        any_alive: bool = any((not target.is_dead()) for target in self._available_targets)
        if not any_alive:
            self._last_messages.append(msg)
            await self.end_battle()
            return ''
        return msg

    async def execute_action(self, user: User, emoji: Emoji) -> None:
        if (self._pass_turn is None) or (not self._pass_turn.is_running()):
            return
        user_be: Optional[BattleEntity] = self._current_team.entity_dict.get(user.user_entity)
        if user_be:
            if user_be not in self._current_team.user_acted:
                target_entity = self._chosen_target.get(user_be)
                if target_entity is not None and target_entity.is_dead():
                    return
                msg = await self._perform_action(user_be, emoji, target_entity)
                if self._finished:
                    return
                if msg:
                    self._current_team.user_acted.add(user_be)
                    self._last_messages.append(msg)
                    if len(self._current_team.user_acted) == len(self._current_team.users):
                        self._pass_turn.cancel()
                        self._current_team.user_acted.clear()
                        await self.next_turn_bot()
                        return
                    await self.append(msg)

        await self.get_adventure().remove_reaction(user, emoji)

    def _get_targets(self, current_team: BattleTeam) -> list[BattleEntity]:
        targets: list[BattleEntity] = []
        for i in range(len(self._teams)):
            if (i != self._turn) and (self._teams[i] is not None) \
                    and ((self._teams[i].affiliation is None or current_team.affiliation is None) or
                         (self._teams[i].affiliation != current_team.affiliation)):
                for entity in self._teams[i].entities:
                    targets.append(entity)
        return targets

    def _print_round(self) -> str:
        mult: int = (self._round // self.INCREASE_EVERY) + 1
        if mult == 1:
            return tr(self.get_lang(), 'BATTLE.ROUND', EMOJI_BATTLE=Emoji.Battle, round=self._round)
        return tr(self.get_lang(), 'BATTLE.ROUND_DMG', EMOJI_BATTLE=Emoji.Battle, round=self._round, multiplier=mult)

    def _print_current_prefix(self):
        self.clear_log()
        self.start_log()

    async def _print_current(self):
        self._print_current_prefix()
        if self._round < 2:
            self.add_log(f"**{tr(self.get_lang(), 'BATTLE.START')}**")
        self.add_log(self._print_round())
        for be in self._current_team.entities:
            if be.is_dead():
                self.add_log(f"{Emoji.SKULL} {be.entity.get_name()}")
            else:
                self.add_log(f"{be.entity.get_name()}: {be.print()}")

        if len(self._available_targets) == 1:
            be = self._available_targets[0]
            self.add_log(f"{be.entity.get_name()}: {be.print()}")
        else:
            td: dict[BattleEntity, list[str]] = {}
            for be1, be2 in self._chosen_target.items():
                if be2 is not None:
                    td[be2] = td.get(be2, []) + [be1.entity.get_name()]
            for i in range(len(self._available_targets)):
                be = self._available_targets[i]
                sl: list[str] = td.get(be, [])
                if be.is_dead():
                    self.add_log(f"{Emoji.SKULL} {be.entity.get_name()}")
                else:
                    if sl:
                        self.add_log(f"{i + 1} | {be.entity.get_name()}: {be.print()} <- {', '.join(sl)}")
                    else:
                        self.add_log(f"{i + 1} | {be.entity.get_name()}: {be.print()}")

        self.add_log(self._saved_last_message)

        await self.send_log()

    async def next_turn(self):
        if self._pass_turn is not None:
            self._pass_turn.cancel()
            self._pass_turn = None

        if self._current_team:
            for entity in self._current_team.entities:
                entity.end_turn()

        self._chosen_target.clear()

        # Calculate turn
        self._turn += 1
        if self._turn >= len(self._teams):
            self._turn = 0
            if not self._only_bots:
                self._only_bots = True
                for team in self._teams:
                    for user in team.users:
                        if not user.is_dead():
                            self._only_bots = False
                            break
                    if not self._only_bots:
                        break
            if self._only_bots:
                if self._last_messages:
                    self._saved_last_message = '\n'.join(self._last_messages)
                    self._last_messages.clear()
                await self._print_current()
                await asyncio.sleep(2)
            self._round += 1

        infinite_check: int = len(self._teams) * 2
        while self._teams[self._turn] is None:
            self._turn += 1
            if self._turn >= len(self._teams):
                self._turn = 0
            infinite_check -= 1
            if infinite_check == 0:
                self._coroutines.append(self.end())
                self._event.set()
                return

        # Get team
        self._current_team: BattleTeam = self._teams[self._turn]

        self._available_targets: list[BattleEntity] = self._get_targets(self._current_team)
        if not self._available_targets:
            self._coroutines.append(self.end())
            self._event.set()
            return

        if (not self._current_team.users) or (not self._current_team.any_user_alive()):
            self._coroutines.append(self.next_turn_bot())
            self._event.set()
            return

        for e1, e2 in self._current_team.last_target.items():
            try:
                if e2 in self._available_targets:
                    self._chosen_target[e1] = e2
            except ValueError:
                pass

        if self._last_messages:
            self._saved_last_message = '\n'.join(self._last_messages)
            self._last_messages.clear()
        else:
            self._saved_last_message = ''

        await self._print_current()

        if len(self._available_targets) == 1:
            for be in self._current_team.entities:
                self._chosen_target[be] = self._available_targets[0]

        if len(self._user_entities) == 1:
            self._pass_turn = DelayTask(120, self.next_turn)
        else:
            self._pass_turn = DelayTask(30, self.next_turn)

    async def next_turn_bot(self):
        if self._current_team.any_bot_alive():
            targets: dict[BattleEntity, int] = {}
            for be in self._chosen_target.values():
                targets[be] = targets.get(be, 0) + 1
            if not targets:
                choose = [x for x in self._available_targets if not x.is_dead()]
                if not choose:
                    await self.next_turn()
                    return
                be: BattleEntity = random.choice(choose)
                targets[be] = 1
            for bot in self._current_team.bots:
                if not bot.is_dead():
                    target: BattleEntity = random.choices(list(targets.keys()), weights=list(targets.values()), k=1)[0]
                    msg: str = await self._perform_action(bot, Emoji.BATTLE, target)
                    if msg:
                        self._last_messages.append(msg)

        self._coroutines.append(self.next_turn())
        self._event.set()

    async def end_battle(self):
        if self._pass_turn is not None:
            self._pass_turn.cancel()
            self._pass_turn = None

        for team in self._teams:
            for be in team.entities:
                be.entity.end_battle()

        if self._last_messages:
            self._saved_last_message = '\n'.join(self._last_messages)
            self._last_messages.clear()
        else:
            self._saved_last_message = ''

        self._finished = True
        await self._print_current()
        await self.append(f"**{tr(self.get_lang(), 'BATTLE.WIN', name=self._current_team.name)}**")
        await self.end()

    async def end(self, lost: bool = False, skip: bool = False) -> None:
        self._finished = True
        self._event.set()
        await super().end(lost, skip)


class BattleChapterWithText(BattleChapter):
    def __init__(self, text: list[str]):
        super().__init__()
        self._text = text

    async def init(self) -> None:
        for line in self._text:
            await self.append_and_wait(f"_{line}_", 2)
        await super().init()

    def _print_current_prefix(self):
        super()._print_current_prefix()
        if self.get_round() < 2:
            self.add_log('\n'.join([f"_{line}_" for line in self._text]))


def q1v1(a: Entity, b: Entity, battle: Optional[BattleChapter] = None) -> BattleChapter:
    if not battle:
        battle = BattleChapter()
    battle.add_team(BattleTeam(a.get_name(), [a]))
    battle.add_team(BattleTeam(b.get_name(), [b]))
    return battle


def rnd(adventure: Adventure, location: Location, pool: str = ''):
    last_id: Optional[int] = adventure.saved_data.get('_battle_last_id')
    beb: BotEntityBuilder = enemy_utils.get_random_enemy(location, pool, last_id)
    adventure.saved_data['_battle_last_id'] = beb.enemy_id
    return beb.instance()
