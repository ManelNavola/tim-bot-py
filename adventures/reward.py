from adventures.adventure import Chapter
from enums.emoji import Emoji
from user_data.user import User


class RewardChapter(Chapter):
    def __init__(self):
        super().__init__(Emoji.BOX)

    async def init(self, user: User):
        await self.send_log("You found a chest!")
        await self.message.add_reaction(Emoji.BOX[1], self.open)

    async def open(self):
        await self.send_log("There was nothing inside...")
        await self.end()
