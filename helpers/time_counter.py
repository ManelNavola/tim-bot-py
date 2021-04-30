from autoslot import Slots

import utils


class TimeCounter(Slots):
    def __init__(self):
        self.time = utils.current_ms()

    def get_seconds(self) -> float:
        return float(utils.current_ms() - self.time) / 1000
