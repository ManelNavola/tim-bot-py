# Imports
import os

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

import utils
from commands import command, simple, box, bet, upgrade, shop
from db import database

# Load database
registered_guild_ids = None
if utils.is_test():
    # Local test
    database.load_test_database()
    registered_guild_ids = [824723874544746507]  # Update quick
else:
    # Production
    database.load_database()

bot = commands.Bot(command_prefix='/')
slash = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print("Ready!")
    if utils.is_test():
        from commands import console
        await console.execute()


@slash.slash(name="check", description="Check information about a user",
             options=[
                 create_option(
                     name="user",
                     description="User to check",
                     option_type=6,
                     required=True
                 )
             ], guild_ids=registered_guild_ids)
async def _check(ctx: SlashContext, member: discord.Member):
    await command.call(ctx, simple.check, member)


@slash.slash(name="inv", description="Check your inventory",
             guild_ids=registered_guild_ids)
async def _inv(ctx):
    await command.call(ctx, simple.inv)


@slash.slash(name="transfer", description="Retrieves money from the bank",
             guild_ids=registered_guild_ids)
async def _bank(ctx):
    await command.call(ctx, simple.transfer)


@slash.subcommand(base="bet", name="info", description="Get information about betting", guild_ids=registered_guild_ids)
async def _bet_info(ctx):
    await command.call(ctx, bet.info)


@slash.subcommand(base="bet", name="add", description="Place or start a bet",
                  options=[
                      create_option(
                          name="money",
                          description="Amount of money to raised the bet to",
                          option_type=4,
                          required=True
                      )
                  ], guild_ids=registered_guild_ids)
async def _bet_add(ctx, money: int):
    await command.call(ctx, bet.add, money)


@slash.subcommand(base="bet", name="check", description="Check the current bet",
                  guild_ids=registered_guild_ids)
async def _bet_check(ctx):
    await command.call(ctx, bet.check)


@slash.subcommand(base="upgrade", name="menu", description="View available upgrades", guild_ids=registered_guild_ids)
async def _upgrade(ctx):
    await command.call(ctx, upgrade.menu)


@slash.subcommand(base="upgrade", name="money_limit", description="Upgrade money capacity",
                  guild_ids=registered_guild_ids)
async def _upgrade(ctx):
    await command.call(ctx, upgrade.upgrade, 'money_limit')


@slash.subcommand(base="upgrade", name="bank", description="Upgrade bank capacity", guild_ids=registered_guild_ids)
async def _upgrade(ctx):
    await command.call(ctx, upgrade.upgrade, 'bank')


@slash.subcommand(base="upgrade", name="garden", description="Upgrade garden production",
                  guild_ids=registered_guild_ids)
async def _upgrade(ctx):
    await command.call(ctx, upgrade.upgrade, 'garden')


@slash.slash(name="post_inv", description="Post your inventory",
             guild_ids=registered_guild_ids)
async def _inv(ctx):
    await command.call(ctx, simple.post_inv)


@slash.subcommand(base="crate", name="check", description="Check money in the box",
                  guild_ids=registered_guild_ids)
async def _box_check(ctx):
    await command.call(ctx, box.check)


@slash.subcommand(base="crate", name="place", description="Place money in the box",
                  options=[
                      create_option(
                          name="money",
                          description="Amount of money to place on the box",
                          option_type=4,
                          required=True
                      )
                  ], guild_ids=registered_guild_ids)
async def _box_place(ctx, money):
    await command.call(ctx, box.place, money)


@slash.subcommand(base="crate", name="take", description="Take money from the box",
                  guild_ids=registered_guild_ids)
async def _box_take(ctx):
    await command.call(ctx, box.take)


@slash.slash(name="leaderboard", description="Check out who's got the most money",
             guild_ids=registered_guild_ids)
async def _leaderboard(ctx):
    await command.call(ctx, simple.leaderboard)


@slash.subcommand(base="shop", name="check", description="Check the guild shop",
                  guild_ids=registered_guild_ids)
async def _shop_check(ctx):
    await command.call(ctx, shop.check)


@slash.subcommand(base="shop", name="buy", description="Buy an item shop",
                  options=[
                      create_option(
                          name="number",
                          description="Number of the item to buy",
                          option_type=4,
                          required=True
                      )
                  ],
                  guild_ids=registered_guild_ids)
async def _shop_buy(ctx, number: int):
    await command.call(ctx, shop.buy, number)


@slash.slash(name="stats", description="Check your stats",
             guild_ids=registered_guild_ids)
async def _stats(ctx):
    await command.call(ctx, simple.stats)


@slash.slash(name="equip", description="Equip an item",
             options=[
                 create_option(
                     name="number",
                     description="Number of the item to equip",
                     option_type=4,
                     required=True
                 )
             ],
             guild_ids=registered_guild_ids)
async def _stats(ctx, number: int):
    await command.call(ctx, simple.equip, number)


@slash.slash(name="unequip", description="Unequip an item",
             options=[
                 create_option(
                     name="number",
                     description="Number of the item to unequip",
                     option_type=4,
                     required=True
                 )
             ],
             guild_ids=registered_guild_ids)
async def _stats(ctx, number: int):
    await command.call(ctx, simple.unequip, number)


# Hacky uwu
if utils.is_test():
    with open('local/d.txt') as f:
        bot.run(f.readline())
else:
    bot.run(os.environ['CLIENT_KEY'])
