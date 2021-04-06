# Imports
import os
from typing import Optional

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

import utils
from commands import command, simple, crate, bet, upgrade, shop, messages
from commands.command import Command
from common import storage
from db import database

# Load database
from inventory_data.entity import BotEntity
from inventory_data.stats import Stats
from user_data.user import User

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


# Ready event
@bot.event
async def on_ready():
    print("Ready!")
    if utils.is_test():
        from commands import console
        await console.execute()


@bot.event
async def on_reaction_add(reaction: discord.Reaction, discord_user: discord.User):
    user: Optional[User] = storage.get_user(discord_user.id, create=False)
    if user is not None:
        await messages.on_reaction_add(user, discord_user, reaction.message.id, reaction)


# Register commands
# Inventory management
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


@slash.slash(name="post_inv", description="Post your inventory",
             guild_ids=registered_guild_ids)
async def _post_inv(ctx):
    await command.call(ctx, simple.post_inv)


@slash.slash(name="transfer", description="Retrieves money from the bank",
             guild_ids=registered_guild_ids)
async def _transfer(ctx):
    await command.call(ctx, simple.transfer)


@slash.slash(name="leaderboard", description="Check out the top players",
             guild_ids=registered_guild_ids)
async def _leaderboard(ctx):
    await command.call(ctx, simple.leaderboard)


# Betting
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


# Upgrades
@slash.subcommand(base="upgrade", name="menu", description="View available upgrades",
                  guild_ids=registered_guild_ids)
async def _upgrade(ctx):
    await command.call(ctx, upgrade.menu)


@slash.subcommand(base="upgrade", name="short_menu", description="View available upgrades",
                  guild_ids=registered_guild_ids)
async def _upgrade(ctx):
    await command.call(ctx, upgrade.menu, True)


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


@slash.subcommand(base="upgrade", name="inventory", description="Upgrade inventory limit",
                  guild_ids=registered_guild_ids)
async def _upgrade(ctx):
    await command.call(ctx, upgrade.upgrade, 'inventory')


# Crate
@slash.subcommand(base="crate", name="check", description="Check money in the crate",
                  guild_ids=registered_guild_ids)
async def _crate_check(ctx):
    await command.call(ctx, crate.check)


@slash.subcommand(base="crate", name="place", description="Place money in the crate",
                  options=[
                      create_option(
                          name="money",
                          description="Amount of money to place in the crate",
                          option_type=4,
                          required=True
                      )
                  ], guild_ids=registered_guild_ids)
async def _crate_place(ctx, money):
    await command.call(ctx, crate.place, money)


@slash.subcommand(base="crate", name="take", description="Take money from the crate",
                  guild_ids=registered_guild_ids)
async def _crate_take(ctx):
    await command.call(ctx, crate.take)


# Shop
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


@slash.subcommand(base="shop", name="sell", description="Sell an item from your inventory",
                  options=[
                      create_option(
                          name="number",
                          description="Number of the item to sell",
                          option_type=4,
                          required=True
                      )
                  ],
                  guild_ids=registered_guild_ids)
async def _shop_sell(ctx, number: int):
    await command.call(ctx, shop.sell, number)


@slash.subcommand(base="shop", name="sellall", description="Sells all unequipped items from your inventory",
                  guild_ids=registered_guild_ids)
async def _shop_sell(ctx):
    await command.call(ctx, shop.sell_all)


# RPG management
@slash.slash(name="stats", description="Check your stats",
             guild_ids=registered_guild_ids)
async def _stats(ctx):
    await command.call(ctx, simple.stats)


@slash.slash(name="abilities", description="Check your abilities",
             guild_ids=registered_guild_ids)
async def _abilities(ctx):
    await command.call(ctx, simple.abilities, ignore_battle=True)


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
async def _equip(ctx, number: int):
    await command.call(ctx, simple.equip, number)


@slash.slash(name="equipbest", description="Equips the best items you have according to their price",
             guild_ids=registered_guild_ids)
async def _equip_best(ctx):
    await command.call(ctx, simple.equip_best)


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
async def _unequip(ctx, number: int):
    await command.call(ctx, simple.unequip, number)


@slash.slash(name="unequipall", description="Unequip all items",
             guild_ids=registered_guild_ids)
async def _unequip_all(ctx):
    await command.call(ctx, simple.unequip_all)


# Register test command
saved: Optional[User] = None
fite_bot: bool = True
if utils.is_test():
    @slash.slash(name="rich", description="MAKE IT RAIN BABYYY", guild_ids=registered_guild_ids)
    async def _rich(ctx):
        async def rich(cmd: Command):
            for upg_name in cmd.user.upgrades:
                upg = cmd.user.upgrades[upg_name]
                while not upg.is_max_level():
                    upg.level_up()
            cmd.user.add_money(999999999999)
            await cmd.send_hidden("yay")

        await command.call(ctx, rich)


    @slash.slash(name="test", description="Quickly test anything!",
                 guild_ids=registered_guild_ids)
    async def _test(ctx):
        async def to_test(cmd: Command):
            global saved, fite_bot
            if fite_bot:
                being_b = BotEntity('THE BEAST', 100, 200, {
                    Stats.STR: 2,
                    Stats.CRIT: 100
                })
                await cmd.guild.start_battle(cmd.ctx, cmd.user, opponent_bot=being_b)
            else:
                if saved is None:
                    saved = cmd.user
                else:
                    await cmd.guild.start_battle(cmd.ctx, cmd.user, opponent_user=saved)

        await command.call(ctx, to_test)

# Run bot based on test
if utils.is_test():
    with open('local/d.txt') as f:
        bot.run(f.readline())
else:
    bot.run(os.environ['CLIENT_KEY'])
