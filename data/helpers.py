import utils

class IncrementalHelper():
    def __init__(self, d: dict, base_field: str, time_field: str, minute_incr: int):
        self.dictionary = d
        self.base_field = base_field
        self.time_field = time_field
        self.minute_increment = minute_incr
        self.rate = 60 / self.minute_increment

    def get(self):
        return self.dictionary[self.base_field] + (utils.now() - self.dictionary[self.time_field]) // self.minute_increment

    def set(self, value: int):
        self.dictionary[self.base_field] = value
        self.dictionary[self.time_field] = utils.now()

    def change(self, value: int):
        self.set(self.get() + value)