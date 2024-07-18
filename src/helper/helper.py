import json
import os
import discord

def open_json(file_name):
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
    return data

def close_json(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)


def is_valid_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
async def get_username_from_message_id(channel, message_id):
    try:
        message = await channel.fetch_message(message_id)
        return message.author.name
    except discord.NotFound:
        return "Message not found."
    except discord.Forbidden:
        return "Bot does not have permission to fetch the message."
    except discord.HTTPException as e:
        return f"Failed to fetch the message: {str(e)}"
    
async def get_username_from_user_id(bot, user_id):
    try:
        user = await bot.fetch_user(user_id)
        return user.name
    except discord.NotFound:
        return "User not found."
    except discord.Forbidden:
        return "Bot does not have permission to fetch the user."
    except discord.HTTPException as e:
        return f"Failed to fetch the user: {str(e)}"
    
def check_game_link(game_link : str):
    if "https://" not in game_link and "pokernow.club" not in game_link:
        return False
    else:
        return True