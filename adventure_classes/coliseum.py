from abc import ABC, abstractmethod
import random

from discord_slash import SlashContext

import utils
from adventure_classes.adventure import Adventure, Chapter
from adventure_classes.battle import BattleChapter
from enemy_data import enemy_utils
from enums.emoji import Emoji
from enums.location import Location
from guild_data.shop import Shop
from item_data import item_utils
from item_data.item_classes import ItemData
from item_data.rarity import Rarity, RarityInstance
from user_data.user import User


class ColiseumRewardInstance(ABC):
    @abstractmethod
    async def award(self, chapter: Chapter, user: User):
        pass


class ColiseumItemReward(ColiseumRewardInstance):
    def __init__(self, item_rarity: RarityInstance):
        self.item_rarity: RarityInstance = item_rarity

    async def award(self, chapter: Chapter, user: User):
        item_data: ItemData = item_utils.get_random_shop_item_data(rarity=self.item_rarity)
        slot = user.inventory.get_empty_slot()
        if slot is not None:
            item = item_utils.create_user_item(user.get_db(), user.id, item_data)
            user.inventory.add_item(item)
            chapter.add_log(f'You found {item.print()}!')
        else:
            money = int(item_data.calculate_price() * Shop.SELL_MULTIPLIER)
            user.add_money(money)
            chapter.add_log(f'Inventory full! Sold {item_data.print()} for {utils.print_money(money)}!')


class ColiseumMoneyReward(ColiseumRewardInstance):
    def __init__(self, money_min: int, money_max: int):
        self.min: int = money_min
        self.max: int = money_max

    async def award(self, chapter: Chapter, user: User):
        money = random.randint(self.min, self.max)
        chapter.add_log(f'You found {utils.print_money(money)}!')
        user.add_money(money)


class ColiseumReward:
    def __init__(self, rewards: list[tuple[ColiseumRewardInstance, int]]):
        self.rewards: list[ColiseumRewardInstance] = []
        self.weights: list[int] = []
        for tup in rewards:
            self.rewards.append(tup[0])
            self.weights.append(tup[1])

    async def award(self, chapter: Chapter, user: User):
        await random.choices(self.rewards, weights=self.weights, k=1)[0].award(chapter, user)


REWARDS = {
    0: ColiseumReward([
        (ColiseumMoneyReward(20, 40), 10),
        (ColiseumMoneyReward(40, 60), 5),
        (ColiseumItemReward(Rarity.COMMON), 1)
    ]),
    1: ColiseumReward([
        (ColiseumMoneyReward(100, 200), 10),
        (ColiseumItemReward(Rarity.COMMON), 2),
        (ColiseumItemReward(Rarity.UNCOMMON), 1)
    ]),
    2: ColiseumReward([
        (ColiseumMoneyReward(250, 400), 10),
        (ColiseumItemReward(Rarity.UNCOMMON), 2),
        (ColiseumItemReward(Rarity.RARE), 1)
    ])
}


class ColiseumRewardChapter(Chapter):
    def __init__(self):
        super().__init__(Emoji.BOX)

    async def init(self, user: User):
        self.add_log("You find a box beneath your feet.")
        self.add_log("You may collect the reward and exit, or venture further to find bigger rewards.")
        await self.pop_log()
        await self.message.add_reaction(Emoji.BOX, self.reward)
        await self.message.add_reaction(Emoji.COLISEUM, self.venture)

    async def reward(self, user: User):
        await REWARDS[self._adventure.saved_data['level']].award(self, user)
        await self.pop_log()
        await self.end()

    async def venture(self):
        level: int = self._adventure.saved_data['level'] + 1
        self._adventure.saved_data['level'] = level
        if level == 3:
            await self.end()
            return

        for i in range(3):
            enemy_build = enemy_utils.get_random_enemy(Location.COLISEUM, str(level))
            self._adventure.add_chapter(BattleChapter(enemy_build.instance()))
        self._adventure.add_chapter(ColiseumRewardChapter())
        await self.end()


async def start(ctx: SlashContext, user: User):
    adventure: Adventure = Adventure("Coliseum", Emoji.COLISEUM.value)
    adventure.saved_data['level'] = 0
    for i in range(3):
        adventure.add_chapter(BattleChapter(
            enemy_utils.get_random_enemy(Location.COLISEUM, str(adventure.saved_data['level'])).instance()))
    adventure.add_chapter(ColiseumRewardChapter())
    await user.start_adventure(ctx, adventure)
