# from adventure_classes.generic.battle_entity import BattleEntity
# from adventure_classes.generic.stat_modifier import StatModifier
# from user_data.user import User
#
#
# class UserAdventureData:
#     def __init__(self, user: User):
#         self.user = user
#         self.battle_modifiers: list[StatModifier] = []
#
#     def add_battle_modifier(self, modifier: StatModifier):
#         self.battle_modifiers.append(modifier)
#
#     def get_battle_entity(self, lang: str):
#         return BattleEntity(self.user.user_entity, lang)
