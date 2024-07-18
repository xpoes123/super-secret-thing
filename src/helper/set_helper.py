import discord
import json
from discord.ext import commands
from datetime import date
import helper
from variables import roles, games
import os

def open_json(file_name):
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def close_json(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

async def get_member(guild, user_id):
    try:
        user_id = int(user_id)
        member = guild.get_member(user_id)
        if member is None:
            member = await guild.fetch_member(user_id)
        return member
    except ValueError:
        return None

async def help_init_host(ctx, user_id: str, venmo, cashapp, role: roles, bot):
    if not helper.is_valid_int(user_id):
        await ctx.respond("Not valid user_id, must be integer", ephemeral=True)
        return

    user_id = int(user_id)
    user_data = open_json("user_info.json")
    username = await helper.get_username_from_user_id(bot, user_id)

    user_data.setdefault(user_id, {"username": username})
    user_data[user_id].update({
        "username": username,
        "venmo": venmo,
        "cashapp": cashapp,
        "role": role,
        "unverified": 0,
        "low-stakes-nlh": 0,
        "mid-stakes-nlh": 0,
        "high-stakes-nlh": 0,
        "plo": 0,
        "unverified-sf": 0,
        "low-stakes-nlh-sf": 0,
        "mid-stakes-nlh-sf": 0,
        "high-stakes-nlh-sf": 0,
        "plo-sf": 0,
        "hosting": "None"
    })

    close_json("user_info.json", user_data)

    member = await get_member(ctx.guild, user_id)
    if member is None:
        await ctx.respond("Invalid user ID provided.", ephemeral=True)
        return

    role_obj = discord.utils.get(ctx.guild.roles, name=role)
    if role_obj is None:
        await ctx.respond(f"Role '{role}' not found.", ephemeral=True)
        return

    if role_obj in member.roles:
        await ctx.respond(f"{member.mention} already has the '{role}' role.", ephemeral=True)
    else:
        await member.add_roles(role_obj)
        await ctx.respond(f"{username} is now a {role} host!")

async def help_venmo(ctx, user_id, venmo):
    if not helper.is_valid_int(user_id):
        await ctx.respond("Not valid user_id, must be integer", ephemeral=True)
        return

    user_id = str(user_id)
    user_data = open_json("user_info.json")

    if user_id in user_data:
        user_data[user_id]["venmo"] = venmo
        user_name = user_data[user_id]["username"]
        close_json("user_info.json", user_data)
        await ctx.respond(f"Venmo set to {venmo} for user {user_name}", ephemeral=True)
    else:
        await ctx.respond("Host Not Initialized", ephemeral=True)

async def help_cashapp(ctx, user_id, cashapp):
    if not helper.is_valid_int(user_id):
        await ctx.respond("Not valid user_id, must be integer", ephemeral=True)
        return

    user_id = str(user_id)
    user_data = open_json("user_info.json")

    if user_id in user_data:
        user_data[user_id]["cashapp"] = cashapp
        user_name = user_data[user_id]["username"]
        close_json("user_info.json", user_data)
        await ctx.respond(f"Cashapp set to {cashapp} for user {user_name}", ephemeral=True)
    else:
        await ctx.respond("Host Not Initialized", ephemeral=True)

async def help_promotion(ctx, user_id, role: roles):
    if not helper.is_valid_int(user_id):
        await ctx.respond("Not valid user_id, must be integer", ephemeral=True)
        return

    user_id = str(user_id)
    user_data = open_json("user_info.json")

    if user_id in user_data:
        user_data[user_id]["role"] = role
        user_name = user_data[user_id]["username"]
        close_json("user_info.json", user_data)
        await ctx.respond(f"Role set to {role} for user {user_name}", ephemeral=True)
    else:
        await ctx.respond("Host Not Initialized", ephemeral=True)
