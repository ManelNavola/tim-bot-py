from helpers import translate


class ActionResult:
    def __init__(self, message: str = '', success: bool = False, **kwargs):
        self.message: str = message
        self.success: bool = success
        self.__dict__.update(kwargs)
        self._kwargs = kwargs

    def tr(self, lang: str):
        return translate.tr(lang, self.message, **self._kwargs)
