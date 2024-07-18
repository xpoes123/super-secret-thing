import discord
from discord.ext import commands
from game_helper import help_host, help_add_table, help_sf, help_check_roles
from variables import roles, games
from set_helper import (
    help_init_host,
    help_venmo,
    help_cashapp,
    help_promotion,
)

intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content
intents.messages = True  # Enable message events
intents.guilds = True  # Enable guild-related events
intents.members = True  # Enable member-related events

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(name="init_host", description="Set Your Venmo")
async def init_host(ctx, user_id: str, venmo, cashapp, role: roles):
    await help_init_host(ctx, user_id, venmo, cashapp, role, bot)

set = discord.SlashCommandGroup("set", "Setting Host Information")

@set.command()
async def venmo(ctx, user_id, venmo):
    await help_venmo(ctx, user_id, venmo)

@set.command()
async def cashapp(ctx, user_id, cashapp):
    await help_cashapp(ctx, user_id, cashapp)

@set.command()
async def promotion(ctx, user_id, role: roles):
    await help_promotion(ctx, user_id, role)

bot.add_application_command(set)

game = discord.SlashCommandGroup("game", "Hosting games")

@game.command()
async def host(ctx, game_link, stakes, private=False):
    await help_host(ctx, game_link, stakes, private)
    
@game.command()
async def add_table(ctx, new_game_link):
    await help_add_table(ctx, new_game_link)

@game.command()
async def sf(ctx):
    await help_sf(ctx, bot)

bot.add_application_command(game)

@bot.slash_command(name="roles", description="Check if a user has specific roles")
async def check_roles(ctx, member: discord.Member):
    await help_check_roles(ctx, member)

bot.run("YOUR_DISCORD_BOT_TOKEN")
