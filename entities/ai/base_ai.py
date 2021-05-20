from abc import ABC, abstractmethod


class BotAI(ABC):
    @abstractmethod
    def decide(self):
        pass


class BaseBotAI(BotAI):
    def decide(self):
        pass
