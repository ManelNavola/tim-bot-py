import asyncio
import typing

from typing import Optional

import utils
from adventure_classes.generic.adventure import Adventure
from adventure_classes.generic.battle.battle_action_data import BattleActionData
from adventure_classes.generic.battle.battle_entity import BattleEntity
from adventure_classes.generic.battle.battle_group import BattleGroup
from adventure_classes.generic.chapter import Chapter
from enemy_data import enemy_utils
from enemy_data.bot_entity_builder import BotEntityBuilder
from entities.ai.base_ai import BotAI
from entities.bot_entity import BotEntity
from enums.battle_emoji import BattleEmoji
from enums.emoji import Emoji
from enums.location import Location
from helpers.timer import WaitUntil
from helpers.translate import tr
from item_data.abilities import AbilityInstance

if typing.TYPE_CHECKING:
    from user_data.user import User


class BattleChapter(Chapter):
    INCREASE_EVERY: typing.Final[int] = 8
    SINGLE_PLAYER_DELAY: int = 300
    MULTI_PLAYER_DELAY: int = 20

    def __init__(self, group_a: BattleGroup, group_b: BattleGroup,
                 icon: Emoji = Emoji.BATTLE, pre_text: list[str] = None, is_boss: bool = False):
        super().__init__(icon)
        if pre_text is None:
            pre_text = []
        self._group_a: BattleGroup = group_a
        self._group_b: BattleGroup = group_b
        self._multiple_users: bool = (self._group_a.has_multiple_users() or self._group_b.has_multiple_users())
        self._turn_a: bool = True
        self._battle_log: list[str] = []
        self._round: int = 0
        self._round_offbeat: bool = False
        self._available_targets: list[BattleEntity] = []
        self._chosen_targets: dict[BattleEntity, BattleEntity] = {}
        self._pass_turn: Optional[WaitUntil] = None
        self._acted: set[User] = set()
        self._pre_text: list[str] = pre_text
        self._late_clear: bool = False
        self._max_targets: int = 1
        self._speed_balance: float = 0
        self._dont_add_speed: bool = False
        self._is_boss: bool = is_boss

    def _recalculation_will_involve_first_time(self) -> bool:
        old_max_targets: int = self._max_targets
        if old_max_targets > 1:
            return False
        max_targets: int = 1
        if self._group_a.has_users() and self._group_b.has_users():
            max_targets = max(len(self._group_a.get_battle_entities()), len(self._group_b.get_battle_entities()))
        elif self._group_a.has_users() or self._group_b.has_users():
            if self._group_a.has_users():
                max_targets = len(self._group_b.get_battle_entities())
            elif self._group_b.has_users():
                max_targets = len(self._group_a.get_battle_entities())
        return max_targets > 1

    async def _recalculate_max_targets(self) -> None:
        old_max_targets: int = self._max_targets
        if self._group_a.has_users() and self._group_b.has_users():
            self._max_targets = max(len(self._group_a.get_battle_entities()), len(self._group_b.get_battle_entities()))
        elif self._group_a.has_users() or self._group_b.has_users():
            if self._group_a.has_users():
                self._max_targets = len(self._group_b.get_battle_entities())
            elif self._group_b.has_users():
                self._max_targets = len(self._group_a.get_battle_entities())
        if self._max_targets > old_max_targets:
            if old_max_targets == 1:
                old_max_targets = 0
            for num in range(old_max_targets, self._max_targets):
                await self.get_adventure().add_reaction(Emoji.get_number(num + 1), self.choose_target)

    def _get_mulitplier(self) -> int:
        return (self._round // self.INCREASE_EVERY) + 1

    def _print_round(self) -> str:
        mult: int = self._get_mulitplier()
        ret_txt: str
        if self._round == 0:
            ret_txt = tr(self.get_lang(), 'BATTLE.LOADING', EMOJI_BATTLE=Emoji.BATTLE)
        elif mult == 1:
            ret_txt = tr(self.get_lang(), 'BATTLE.ROUND', EMOJI_BATTLE=Emoji.BATTLE, round=self._round)
        else:
            ret_txt = tr(self.get_lang(), 'BATTLE.ROUND_DMG', EMOJI_BATTLE=Emoji.BATTLE, round=self._round,
                         multiplier=mult)
        if self._multiple_users:
            ret_txt += f" {Emoji.CLOCK} {utils.print_time(self.get_lang(), BattleChapter.MULTI_PLAYER_DELAY)}"
        return ret_txt

    def _get_current_team(self) -> BattleGroup:
        return self._group_a if self._turn_a else self._group_b

    def _get_opposing_team(self) -> BattleGroup:
        return self._group_b if self._turn_a else self._group_a

    def _is_finished(self) -> bool:
        return self._group_b.get_alive_count() == 0 or self._group_a.get_alive_count() == 0

    async def update(self, final: bool = False):
        current_team: BattleGroup = self._get_current_team()
        other_team: BattleGroup = self._get_opposing_team()
        self.clear_log()
        self.start_log()
        if self._round < 2:
            if self._pre_text:
                self.add_log('\n'.join([f"_{x}_" for x in self._pre_text]))
            if self._is_boss:
                self.add_log(f"**{tr(self.get_lang(), 'BATTLE.BOSS_START')}**")
            else:
                self.add_log(f"{tr(self.get_lang(), 'BATTLE.START')}")
        self.add_log(self._print_round())
        for battle_entity in current_team.get_battle_entities():
            self.add_log(battle_entity.print())

        if self._get_current_team().get_alive_user_count() > 0:
            if len(self._available_targets) == 1:
                for battle_entity in other_team.get_battle_entities():
                    self.add_log(f"{battle_entity.print()}")
            else:
                td: dict[BattleEntity, list[str]] = {}
                for be1, be2 in self._chosen_targets.items():
                    if be2 is not None:
                        td[be2] = td.get(be2, []) + [be1.get_name()]
                for battle_entity in other_team.get_battle_entities():
                    if battle_entity in self._available_targets:
                        index: int = self._available_targets.index(battle_entity)
                        sl: list[str] = td.get(battle_entity, [])
                        if sl and (not battle_entity.is_dead()):
                            self.add_log(f"{index + 1} | {battle_entity.print()} <- {', '.join(sl)}")
                        else:
                            self.add_log(f"{index + 1} | {battle_entity.print()}")
                    else:
                        self.add_log(f"{battle_entity.print()}")
        else:
            for battle_entity in other_team.get_battle_entities():
                self.add_log(f"{battle_entity.print()}")

        self.add_log('\n'.join(self._battle_log))

        if not final:
            if self._speed_balance == 0:
                if self._group_a.get_speed() > self._group_b.get_speed():
                    self.add_log(tr(self.get_lang(), 'BATTLE.SPEED_BONUS', EMOJI_SPD=Emoji.SPD,
                                    name=self._group_a.get_name(), value='0%'))
                elif self._group_a.get_speed() < self._group_b.get_speed():
                    self.add_log(tr(self.get_lang(), 'BATTLE.SPEED_BONUS', EMOJI_SPD=Emoji.SPD,
                                    name=self._group_b.get_name(), value='0%'))
                else:
                    self.add_log(tr(self.get_lang(), 'BATTLE.NO_SPEED_BONUS', EMOJI_SPD=Emoji.SPD))
            else:
                if self._speed_balance > 0:
                    self.add_log(tr(self.get_lang(), 'BATTLE.SPEED_BONUS', EMOJI_SPD=Emoji.SPD,
                                    name=self._group_a.get_name(), value=f"{self._speed_balance:.0%}"))
                else:
                    self.add_log(tr(self.get_lang(), 'BATTLE.SPEED_BONUS', EMOJI_SPD=Emoji.SPD,
                                    name=self._group_b.get_name(), value=f"{-self._speed_balance:.0%}"))

        await self.send_log()

    async def execute_turn(self) -> None:
        current_team: BattleGroup = self._get_current_team()

        # Turn happenings
        for battle_entity in current_team.get_battle_entities():
            battle_entity.regen_ap()
            # Step turn modifiers
            battle_entity.step_turn_modifiers()
            # Step abilities
            instances: list[AbilityInstance] = []
            for ability_instance in battle_entity.get_ability_instances():
                ability_instance.duration_remaining -= 1
                if ability_instance.duration_remaining > 0:
                    turn: str = ability_instance.ability_holder.turn(self.get_lang(), battle_entity)
                    if turn:
                        self._battle_log.append(f"> {ability_instance.get_icon()} {turn}")
                    instances.append(ability_instance)
                else:
                    end_ability: str = ability_instance.ability_holder.end(self.get_lang(), battle_entity)
                    if end_ability:
                        self._battle_log.append(end_ability)
                battle_entity.set_ability_instances(instances)

        if self._is_finished():
            return

        other_team: BattleGroup = self._get_opposing_team()

        self._available_targets: list[BattleEntity] = [battle_entity
                                                       for battle_entity in other_team.get_battle_entities()
                                                       if not battle_entity.is_dead()]

        self._acted.clear()
        self._chosen_targets.clear()

        if current_team.get_alive_user_count() == 0:
            return await self.execute_turn_bot()

        # User turn
        for battle_entity in current_team.get_battle_entities():
            target: BattleEntity = battle_entity.get_last_target()
            if (target is not None) and (target in self._available_targets):
                self._chosen_targets[battle_entity] = target
            else:
                battle_entity.set_last_target(None)

        if self._recalculation_will_involve_first_time():
            self._chosen_targets.clear()
        await self.update()
        await self._recalculate_max_targets()
        self._late_clear = True

        if len(self._available_targets) == 1:
            for battle_entity in current_team.get_battle_entities():
                self._chosen_targets[battle_entity] = self._available_targets[0]
                battle_entity.set_last_target(self._available_targets[0])

        if current_team.has_multiple_users():
            self._pass_turn = WaitUntil(BattleChapter.MULTI_PLAYER_DELAY)
        else:
            self._pass_turn = WaitUntil(BattleChapter.SINGLE_PLAYER_DELAY)

        await self._pass_turn.wait()
        if self._late_clear:
            self._battle_log.clear()
            self._late_clear = False
        return await self.execute_turn_bot()

    async def choose_target(self, user: 'User', emoji: Emoji) -> None:
        if (self._pass_turn is None) or (not self._pass_turn.is_running()):
            return

        current_team: BattleGroup = self._get_current_team()
        battle_entity: Optional[BattleEntity] = current_team.find_user(user)
        if battle_entity is not None:
            if (battle_entity not in self._acted) and (not battle_entity.is_dead()):
                num: int = emoji.get_number_value() - 1
                if num < len(self._available_targets):
                    self._chosen_targets[battle_entity] = self._available_targets[num]
                    battle_entity.set_last_target(self._available_targets[num])
                    await self.update()

        await self.get_adventure().remove_reaction(user, emoji)

    async def execute_action(self, user: 'User', emoji: Emoji) -> None:
        if (self._pass_turn is None) or (not self._pass_turn.is_running()):
            return

        current_team: BattleGroup = self._get_current_team()
        battle_entity: Optional[BattleEntity] = current_team.find_user(user)
        if battle_entity is not None:
            if (battle_entity not in self._acted) and (not battle_entity.is_dead()):
                target_battle_entity = self._chosen_targets.get(battle_entity)
                if (target_battle_entity is not None) and (target_battle_entity.is_dead()):
                    return
                msg: Optional[str] = battle_entity.try_perform_action(
                    BattleEmoji(emoji),
                    BattleActionData(self.get_lang(), self._get_mulitplier(), target_battle_entity))
                if msg is not None:
                    self._acted.add(user)
                    if self._late_clear:
                        self._battle_log.clear()
                        self._late_clear = False
                    self._battle_log.append(msg)
                    if self._is_finished() or len(self._acted) == current_team.get_alive_user_count():
                        # Finished
                        self._pass_turn.cancel()
                        return
                    await self.append(msg)

        await self.get_adventure().remove_reaction(user, emoji)

    async def execute_turn_bot(self) -> None:
        if self._late_clear:
            self._battle_log.clear()
            self._late_clear = False
        if self._is_finished():
            return
        current_team: BattleGroup = self._get_current_team()
        target_dict: dict[BattleEntity, int] = {
            battle_entity: 0
            for battle_entity in self._get_opposing_team().get_battle_entities()
            if not battle_entity.is_dead()
        }
        for battle_entity in self._chosen_targets.values():
            if not battle_entity.is_dead():
                target_dict[battle_entity] += 1
        for battle_entity in current_team.get_battle_entities():
            if battle_entity.is_bot() and (not battle_entity.is_dead()):
                bad: BattleActionData = BattleActionData(self.get_lang(), self._get_mulitplier(),
                                                         targeted_entities=target_dict)
                emoji: BattleEmoji = battle_entity.bot_decide(bad)
                msg: Optional[str] = battle_entity.try_perform_action(emoji, bad)
                if msg is not None:
                    self._battle_log.append(msg)
            if self._is_finished():
                return

    async def init(self) -> None:
        self._group_a.load(self.get_adventure())
        self._group_b.load(self.get_adventure())
        self._turn_a = (self._group_a.get_speed() >= self._group_b.get_speed())
        # Pretext
        if self._pre_text:
            self.start_log()
            ta: list[str] = [f"_{x}_" for x in self._pre_text]
            for i in range(len(self._pre_text)):
                await self.send_log('\n'.join([ta[i]]))
                await asyncio.sleep(2)
        # Add reactions
        await self.update()
        abilities: int = 0
        for battle_entity in self._group_a.get_battle_entities() + self._group_b.get_battle_entities():
            if battle_entity.is_user():
                abilities = max(abilities, len(battle_entity.get_abilities()))
        await self.get_adventure().add_reaction(BattleEmoji.ATTACK.value, self.execute_action)
        for battle_emoji in BattleEmoji.get_spells(abilities):
            await self.get_adventure().add_reaction(battle_emoji.value, self.execute_action)
        for user in self.get_adventure().get_users():
            if (self._group_a.find_user(user) is not None) or (self._group_b.find_user(user) is not None):
                if user.inventory.get_potion() is not None:
                    await self.get_adventure().add_reaction(BattleEmoji.POTION.value, self.execute_action)
                    break
        if utils.is_test():
            await self.get_adventure().add_reaction(BattleEmoji.WAIT.value, self.execute_action)
        await self._recalculate_max_targets()
        # Loop
        self._round = 1
        while True:
            if (not self._round_offbeat) and self._battle_log and \
                    (self._group_a.get_alive_user_count() + self._group_b.get_alive_user_count() == 0):
                await self.update()
                await asyncio.sleep(3)
                self._battle_log.clear()
            await self.execute_turn()
            if self._is_finished():
                break
            speed_diff: float = (self._group_a.get_speed() - self._group_b.get_speed())
            if self._dont_add_speed:
                self._dont_add_speed = False
            else:
                self._speed_balance += speed_diff * 0.5
            if self._turn_a and self._speed_balance >= 1:
                self._speed_balance -= 1
                self._dont_add_speed = True
            elif not self._turn_a and self._speed_balance <= -1:
                self._speed_balance += 1
                self._dont_add_speed = True
            else:
                if self._round_offbeat:
                    self._round_offbeat = False
                    self._round += 1
                else:
                    self._round_offbeat = True
                self._turn_a = not self._turn_a
        # End
        if self._group_a.get_alive_count() == 0:
            winner = self._group_b
            loser = self._group_a
        else:
            winner = self._group_a
            loser = self._group_b
        if winner.has_users():
            money_won: int = 0
            for battle_entity in loser.get_battle_entities():
                money_won += battle_entity.get_money_value()
            self._battle_log.append(f"**{Emoji.TROPHY} "
                                    f"{tr(self.get_lang(), 'BATTLE.WIN', name=self._get_current_team().get_name())}** "
                                    f"(+{utils.print_money(self.get_lang(), money_won)})")
            distribute: int = round(float(money_won) / len(self.get_adventure().get_users()))
            for user in self.get_adventure().get_users():
                user.add_money(distribute)
            await self.update(final=True)
            await self.end()
        else:
            self._battle_log.append(f"**{Emoji.TROPHY} "
                                    f"{tr(self.get_lang(), 'BATTLE.WIN', name=self._get_current_team().get_name())}**")
            await self.update(final=True)
            await self.end(lost=True)


# Get random enemy
def rnd(adventure: Adventure, location: Location, pool: str = '', bot_ai: Optional[BotAI] = None) -> BotEntity:
    last_id: Optional[int] = adventure.saved_data.get('_battle_last_id')
    beb: BotEntityBuilder = enemy_utils.get_random_enemy(location, pool, last_id)
    adventure.saved_data['_battle_last_id'] = beb.enemy_id
    return beb.instance(bot_ai)


# Quick single-player adventure battle
def qsab(adventure: Adventure, location: Location, pool: str = '',
         icon: Emoji = Emoji.BATTLE, pre_text: list[str] = None) -> None:
    qcsab(adventure, rnd(adventure, location, pool), icon, pre_text)


# Quick custom single-player adventure battle
def qcsab(adventure: Adventure, bot_entity: BotEntity,
          icon: Emoji = Emoji.BATTLE, pre_text: list[str] = None, is_boss: bool = False) -> None:
    adventure.add_chapter(BattleChapter(BattleGroup(users=adventure.get_users()), BattleGroup([bot_entity]),
                                        icon=icon, pre_text=pre_text, is_boss=is_boss))


# Quick custom single-player adventure battle
def qsbb(adventure: Adventure, bot_entity: BotEntity, icon: Emoji = Emoji.BATTLE, pre_text: list[str] = None) -> None:
    adventure.add_chapter(BattleChapter(BattleGroup(users=adventure.get_users()), BattleGroup([bot_entity]),
                                        icon=icon, pre_text=pre_text, is_boss=True))


# Team vs team battle
def qtvt(adventure: Adventure, team_a: list['User'], team_b: list['User']) -> None:
    adventure.add_chapter(BattleChapter(BattleGroup(users=team_a), BattleGroup(users=team_b)))
