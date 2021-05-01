# Imports
import os
from typing import Optional

import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice

import utils
from commands import simple, crate, bet, upgrade, shop, test, adventure, setup
from game_data import data_loader
from helpers import storage, messages, translate
from db import database
from helpers.command import CommandHandler
from helpers.translate import tr
from user_data.user import User

# Load data
data_loader.load()

# Check test/production
registered_guild_ids = None
db = None
if utils.is_test():
    # Local test
    db = database.load_test_database()
    registered_guild_ids = [824723874544746507]  # Update quick
else:
    # Production
    db = database.load_database()

# Register bot
bot = commands.Bot(command_prefix='/')
slash = SlashCommand(bot, sync_commands=True)

# Command handler
cmd_handler = CommandHandler(db, slash)


# Ready event
@bot.event
async def on_ready():
    print("Ready!")
    if utils.is_test():
        from commands import console
        await console.execute(db)


# Reaction catching
@bot.event
async def on_reaction_add(reaction: discord.Reaction, discord_user: discord.Member):
    user: Optional[User] = storage.get_user(db, discord_user.id, create=False)
    if user is not None:
        await messages.on_reaction_add(user, discord_user, reaction.message.id, reaction)
    db.commit()


# Register commands

# Inventory management
cmd_handler.register_command(simple.check,
                             name="check", description="Check information about a user",
                             options=[
                                 create_option(
                                     name="user",
                                     description="User to check",
                                     option_type=6,
                                     required=True
                                 )
                             ], guild_only=True,
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(simple.inv,
                             name="inv", description="Check your inventory",
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(simple.post_inv, name="post_inv", description="Post your inventory",
                             guild_only=True,
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(simple.transfer,
                             name="transfer", description="Retrieves money from the bank",
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(simple.leaderboard,
                             name="leaderboard", description="Check out the top players",
                             guild_only=True,
                             guild_ids=registered_guild_ids)

# Betting
cmd_handler.register_command(bet.info,
                             base="bet", name="info", description="Get information about betting",
                             guild_only=True,
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(bet.add,
                             base="bet", name="add", description="Place or start a bet",
                             options=[
                                 create_option(
                                     name="money",
                                     description="Amount of money to raised the bet to",
                                     option_type=4,
                                     required=True
                                 )
                             ], guild_only=True,
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(bet.check,
                             base="bet", name="check", description="Check the current bet",
                             guild_only=True,
                             guild_ids=registered_guild_ids)

# Upgrades
cmd_handler.register_command(upgrade.menu,
                             base="upgrade", name="menu", description="View available upgrades",
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(upgrade.short_menu,
                             base="upgrade", name="short_menu", description="View available upgrades",
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(upgrade.upgrade, 'money',
                             base="upgrade", name="money", description="Upgrade money capacity",
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(upgrade.upgrade, 'bank',
                             base="upgrade", name="bank", description="Upgrade bank capacity",
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(upgrade.upgrade, 'garden',
                             base="upgrade", name="garden", description="Upgrade garden production",
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(upgrade.upgrade, 'inventory',
                             base="upgrade", name="inventory", description="Upgrade inventory limit",
                             guild_ids=registered_guild_ids)

# Crate
cmd_handler.register_command(crate.check,
                             base="crate", name="check", description="Check money in the crate",
                             guild_only=True,
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(crate.place,
                             base="crate", name="place", description="Place money in the crate",
                             options=[
                                 create_option(
                                     name="money",
                                     description="Amount of money to place in the crate",
                                     option_type=4,
                                     required=True
                                 )
                             ], guild_only=True,
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(crate.take,
                             base="crate", name="take", description="Take money from the crate",
                             guild_only=True,
                             guild_ids=registered_guild_ids)

# Shop
cmd_handler.register_command(shop.check, base="shop", name="check", description="Check the guild shop",
                             guild_only=True,
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(shop.buy,
                             base="shop", name="buy", description="Buy an item shop",
                             options=[
                                 create_option(
                                     name="number",
                                     description="Number of the item to buy",
                                     option_type=4,
                                     required=True
                                 )
                             ], guild_only=True,
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(shop.sell,
                             base="shop", name="sell", description="Sell an item from your inventory",
                             options=[
                                 create_option(
                                     name="number",
                                     description="Number of the item to sell",
                                     option_type=4,
                                     required=True
                                 )
                             ],
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(shop.sell_all,
                             base="shop", name="dispose", description="Sells all unequipped items from your inventory",
                             guild_ids=registered_guild_ids)

# RPG management
cmd_handler.register_command(simple.stats,
                             name="stats", description="Check your stats",
                             guild_ids=registered_guild_ids, ignore_battle=True)

# cmd_handler.register_command(simple.abilities, ignore_battle=True,
#                              name="abilities", description="Check your abilities",
#                              guild_ids=registered_guild_ids)

cmd_handler.register_command(simple.equip,
                             name="equip", description="Equip an item",
                             options=[
                                 create_option(
                                     name="number",
                                     description="Number of the item to equip",
                                     option_type=4,
                                     required=True
                                 )
                             ],
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(simple.equip_best,
                             name="equip_best", description="Equips the best items you have according to their price",
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(simple.unequip,
                             name="unequip", description="Unequip an item",
                             options=[
                                 create_option(
                                     name="number",
                                     description="Number of the item to unequip",
                                     option_type=4,
                                     required=True
                                 )
                             ],
                             guild_ids=registered_guild_ids)

cmd_handler.register_command(simple.unequip_all,
                             name="unequip_all", description="Unequip all items",
                             guild_ids=registered_guild_ids)

# Adventures
# cmd_handler.register_command(adventure.coliseum_start,
#                              name="coliseum",
#                              description="Fight against diverse enemies to obtain rewards (Tokens: 1)",
#                              guild_ids=registered_guild_ids)

cmd_handler.register_command(adventure.start_adventure,
                             name="adventure", description="Adventure time!",
                             options=[
                                 create_option(
                                     name="location",
                                     description="Location to adventure to",
                                     option_type=3,
                                     required=True,
                                     choices=[
                                         create_choice(
                                             name="Forest",
                                             value="Forest"
                                         )
                                     ]
                                 )
                             ],
                             guild_ids=registered_guild_ids)


# Administration
cmd_handler.register_command(setup.language,
                             base="setup",
                             name="language", description="Change the bot's language",
                             options=[
                                 create_option(
                                     name="language",
                                     description="Language to set the bot to",
                                     option_type=3,
                                     required=True,
                                     choices=[
                                         create_choice(
                                             name=f"{tr(x, 'LANGUAGE')}",
                                             value=f"{x}"
                                         ) for x in translate.get_available()
                                     ]
                                 )
                             ], ignore_all=True,
                             guild_ids=registered_guild_ids)

# Register test command
saved: Optional[User] = None
fight_bot: bool = True
if utils.is_test():
    cmd_handler.register_command(test.rich,
                                 name="rich", description="MAKE IT RAIN", guild_ids=registered_guild_ids,
                                 ignore_battle=True)

    cmd_handler.register_command(test.heal,
                                 name="invincible", description="Hax", guild_ids=registered_guild_ids,
                                 ignore_battle=True)

    cmd_handler.register_command(test.test,
                                 name="test", description="Quickly test anything!",
                                 guild_ids=registered_guild_ids)

    cmd_handler.register_command(test.gimme_all,
                                 name="gimme_all", description="gimme_all!",
                                 options=[
                                     create_option(
                                         name=x,
                                         description=x,
                                         option_type=3,
                                         required=False
                                     ) for x in ['tier', 'location', 'rarity']
                                 ],
                                 guild_ids=registered_guild_ids)

# Run bot based on test
if utils.is_test():
    with open('local/d.txt') as f:
        bot.run(f.readline())
else:
    bot.run(os.environ['CLIENT_KEY'])
