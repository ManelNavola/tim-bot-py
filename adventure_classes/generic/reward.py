import random
from abc import abstractmethod

import utils
from adventure_classes.generic.chapter import Chapter
from enums.emoji import Emoji
from guild_data.shop import Shop
from helpers.translate import tr
from item_data.item_classes import Item
from user_data.user import User


class RewardChapter(Chapter):
    def __init__(self, override_str: str = ''):
        super().__init__(Emoji.BOX)
        self._override_str: str = override_str

    async def init(self) -> None:
        if self._override_str:
            await self.send_log(self._override_str)
        else:
            await self.send_log(tr(self.get_lang(), 'REWARD.BOX'))
        await self.get_adventure().add_reaction(Emoji.BOX, self.reward)

    @abstractmethod
    async def reward(self):
        pass


class ItemRewardChapter(RewardChapter):
    def __init__(self, item: Item):
        super().__init__()
        self.item = item

    async def reward(self):
        users: list[User] = [user
                             for user in self.get_adventure().get_users()
                             if user.inventory.get_empty_slot() is not None]
        if not users:
            users = self.get_adventure().get_users()

        user: User = random.choice(users)

        if user.inventory.create_item(self.item) is not None:
            if len(self.get_adventure().get_users()) == 1:
                await self.send_log(tr(self.get_lang(), 'REWARD.ITEM_YOU', item=self.item.print()))
            else:
                await self.send_log(tr(self.get_lang(), 'REWARD.ITEM_SOMEONE', item=self.item.print(),
                                       name=user.get_name()))
        else:
            money = Shop.get_sell_price(self.item)
            user.add_money(money)
            if len(self.get_adventure().get_users()) == 1:
                await self.send_log(tr(self.get_lang(), 'REWARD.ITEM_SOLD_YOU', item=self.item.print(),
                                       money=utils.print_money(self.get_lang(), money)))
            else:
                await self.send_log(tr(self.get_lang(), 'REWARD.ITEM_SOLD_SOMEONE', item=self.item.print(),
                                       name=user.get_name(), money=utils.print_money(self.get_lang(), money)))
        await self.end()


class MoneyRewardChapter(RewardChapter):
    def __init__(self, money: int):
        super().__init__()
        self.money = money

    async def reward(self):
        user: User = random.choice(self.get_adventure().get_users())

        if len(self.get_adventure().get_users()) == 1:
            await self.send_log(tr(self.get_lang(), 'REWARD.MONEY_YOU', money=utils.print_money(self.get_lang(),
                                                                                                self.money)))
        else:
            await self.send_log(tr(self.get_lang(), 'REWARD.MONEY_SOMEONE', money=utils.print_money(self.get_lang(),
                                                                                                    self.money),
                                   name=user.get_name()))

        user.add_money(self.money)
        await self.end()
