import random
from abc import abstractmethod

import utils
from adventure_classes.generic.chapter import Chapter
from enums.emoji import Emoji
from guild_data.shop import Shop
from item_data import item_utils
from item_data.item_classes import Item
from user_data.user import User


class RewardChapter(Chapter):
    def __init__(self):
        super().__init__(Emoji.BOX)

    async def init(self) -> None:
        await self.send_log("You find a box beneath your feet")
        await self.get_adventure().add_reaction(Emoji.BOX, self.reward)

    @abstractmethod
    async def reward(self):
        pass


class ItemRewardChapter(RewardChapter):
    def __init__(self, item: Item):
        super().__init__()
        self.item = item

    async def reward(self):
        users: list[User] = list(self.get_adventure().get_users().keys())
        users = [user for user in users if user.inventory.get_empty_slot() is not None]
        if not users:
            users = list(self.get_adventure().get_users().keys())

        user: User = random.choice(users)
        user_name: str = user.get_name()
        if len(self.get_adventure().get_users()) == 1:
            user_name = 'You'

        slot = user.inventory.get_empty_slot()
        if slot is not None:
            item = item_utils.create_user_item(user.get_db(), user.id, self.item, slot)
            user.inventory.add_item(item)
            self.add_log(f'{user_name} found {item.print()}!')
        else:
            money = Shop.get_sell_price(self.item)
            user.add_money(money)
            self.add_log(f'Inventory full! {user_name} sold {self.item.print()} for {utils.print_money(money)}!')
        await self.pop_log()
        await self.end()


class MoneyRewardChapter(RewardChapter):
    def __init__(self, money: int):
        super().__init__()
        self.money = money

    async def reward(self):
        users: list[User] = list(self.get_adventure().get_users().keys())

        user: User = random.choice(users)
        user_name: str = user.get_name()
        if len(self.get_adventure().get_users()) == 1:
            user_name = 'You'

        user.add_money(self.money)
        await self.send_log(f'{user_name} found {utils.print_money(self.money)}!')
        await self.end()
