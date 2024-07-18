import discord
import textwrap
from discord.ext import commands
import helper
from datetime import date


class MyView(discord.ui.View):
    def __init__(self, game_link):
        super().__init__()
        self.game_link = game_link
        self.pause_button = discord.ui.Button(
            label="Pause", style=discord.ButtonStyle.primary, custom_id="pause_button"
        )
        self.resume_button = discord.ui.Button(
            label="Resume",
            style=discord.ButtonStyle.success,
            custom_id="resume_button",
            disabled=True,
        )
        self.reping_button = discord.ui.Button(
            label="Re-ping",
            style=discord.ButtonStyle.primary,
            custom_id="reping_button",
        )
        self.end_game_button = discord.ui.Button(
            label="End Game",
            style=discord.ButtonStyle.danger,
            custom_id="end_game_button",
        )

        self.pause_button.callback = self.pause_button_callback
        self.resume_button.callback = self.resume_button_callback
        self.reping_button.callback = self.reping_button_callback
        self.end_game_button.callback = self.end_game_button_callback

        self.add_item(self.pause_button)
        self.add_item(self.resume_button)
        self.add_item(self.reping_button)
        self.add_item(self.end_game_button)

    async def pause_button_callback(self, interaction: discord.Interaction):
        self.pause_button.disabled = True
        self.resume_button.disabled = False
        await interaction.response.edit_message(view=self)
        await self.run_pause_function(interaction)

    async def resume_button_callback(self, interaction: discord.Interaction):
        self.pause_button.disabled = False
        self.resume_button.disabled = True
        await interaction.response.edit_message(view=self)
        await self.run_resume_function(interaction)

    async def reping_button_callback(self, interaction: discord.Interaction):
        await self.run_reping_function(interaction)

    async def end_game_button_callback(self, interaction: discord.Interaction):
        await self.run_end_game_function(interaction)

    async def run_pause_function(self, interaction: discord.Interaction):
        await help_pause(interaction, self.game_link)

    async def run_resume_function(self, interaction: discord.Interaction):
        await help_resume(interaction, self.game_link)

    async def run_reping_function(self, interaction: discord.Interaction):
        await help_reping(interaction, self.game_link)

    async def run_end_game_function(self, interaction: discord.Interaction):
        await help_end(interaction, self.game_link)


async def help_host(ctx, game_link, stakes, private=False):
    if not helper.check_game_link(game_link):
        await ctx.send(f"{game_link} is not a valid pokernow link")
        return

    user_mention = ctx.author.mention
    channel = ctx.channel
    user_id = str(ctx.author.id)

    user_data = helper.open_json("user_info.json")
    game_data = helper.open_json("games.json")

    role = None
    if str(channel) == "low-stakes-nlh":
        role = discord.utils.get(ctx.guild.roles, name="low-ping")
    elif str(channel) == "mid-stakes-nlh":
        role = discord.utils.get(ctx.guild.roles, name="mid-ping")
    elif str(channel) == "high-stakes-nlh":
        role = discord.utils.get(ctx.guild.roles, name="high-ping")
    elif str(channel) == "plo":
        role = discord.utils.get(ctx.guild.roles, name="plo-ping")

    venmo = user_data.get(user_id, {}).get("venmo", "Not Set")
    cashapp = user_data.get(user_id, {}).get("cashapp", "Not Set")

    if user_id in user_data:
        try:
            user_data[user_id][str(channel)] += 1
        except KeyError:
            await ctx.send("You can't host a game in this channel!")
            return
    else:
        await ctx.send("Host doesn't exist, please ask admin to initialize")
        return

    response_message = ""

    if private:
        response_message = textwrap.dedent(
            f"""\
            Game Hosted By: {user_mention}

            # DM {user_mention} for Game Link
            # Stakes: **{stakes}**

            **Venmo: @{venmo}**
            **Cashapp: ${cashapp}**
            
            <@&{role.id}>
            """
        )
    else:
        response_message = textwrap.dedent(
            f"""\
            Game Hosted By: {user_mention}

            # [Click To View Game]({game_link})
            # Stakes: **{stakes}**

            **Venmo: @{venmo}**
            **Cashapp: ${cashapp}**
            
            <@&{role.id}>
            """
        )

    sent_message = await ctx.send(response_message, view=MyView(game_link))

    if game_link not in game_data:
        game_data[game_link] = {}

    game_data[game_link].update(
        {
            "host": user_id,
            "game-type": str(channel),
            "stakes": stakes,
            "time": str(date.today()),
            "message": response_message,
            "host-message": sent_message.id,
            "sf": False,
            "running": True,
            "ping": role.id,
            "other-games": []
        }
    )
    user_data[user_id]["hosting"] = game_link
    helper.close_json("user_info.json", user_data)
    helper.close_json("games.json", game_data)


async def help_add_table(ctx, new_game_link: str):
    game_data = helper.open_json("games.json")
    user_data = helper.open_json("user_info.json")
    user_id = str(ctx.author.id)
    game_link = user_data[user_id]["hosting"]
    if game_link == "None":
        await ctx.respond("No primary game hosted, please do /game host first")
        return
    tables = game_data[game_link]['other-games']
    tables.append(new_game_link)
    tables.insert(0, game_link)

    new_message_content = generate_message(tables)
    game_data[game_link]["other-games"].append(new_game_link)

    host_message_id = game_data[game_link]["host-message"]
    try:
        host_message = await ctx.channel.fetch_message(host_message_id)
        await host_message.edit(content=new_message_content)
        await ctx.respond("Table added and host message updated.", ephemeral=True)
    except discord.NotFound:
        await ctx.respond("Could not find the host message to edit.")
    except discord.Forbidden:
        await ctx.respond("I do not have permission to edit the host message.")
    except discord.HTTPException as e:
        await ctx.respond(f"Failed to edit the host message: {e}")
    game_data[game_link]["message"] = new_message_content
    helper.close_json("user_info.json", user_data)
    helper.close_json("games.json", game_data)


def generate_message(game_links):
    main_link = game_links[0]
    game_data = helper.open_json("games.json")
    user_data = helper.open_json("user_info.json")
    
    user_id = game_data[main_link]["host"]
    
    table_messages = ""
    for index, table_link in enumerate(game_links):
        table_messages += f"# [Table {index+1}]({table_link})\n"
    table_messages.strip()
    response_message = (
        f"Games Hosted By: <@{user_id}>\n\n"
        f"{table_messages}\n"
        f"# Stakes: **{game_data[main_link]['stakes']}**\n\n"
        f"**Venmo: @{user_data[user_id]['venmo']}**\n"
        f"**Cashapp: ${user_data[user_id]['cashapp']}**\n\n"
        f" <@&{game_data[main_link]['ping']}>"
    )
    return response_message


async def help_pause(interaction, game_link: str):
    if not helper.check_game_link(game_link):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            f"{game_link} is not a valid pokernow link", ephemeral=True
        )
        return
    channel = interaction.channel
    game_data = helper.open_json("games.json")
    message_id = game_data.get(game_link, {}).get("host-message")
    if not message_id:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            "No hosted game found to pause.", ephemeral=True
        )
        return
    try:
        message = await channel.fetch_message(message_id)
        await message.edit(content="# BUY-INS PAUSED FOR A BIT")
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(f"Message edited successfully.", ephemeral=True)
    except discord.NotFound:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            f"Message with ID {message_id} not found in channel {channel}.",
            ephemeral=True,
        )
    except discord.Forbidden:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            f"Bot does not have permission to edit the message.", ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            f"Failed to edit the message: {str(e)}", ephemeral=True
        )


async def help_resume(interaction, game_link: str):
    if not helper.check_game_link(game_link):
        await interaction.followup.send(
            f"{game_link} is not a valid pokernow link", ephemeral=True
        )
        return
    channel = interaction.channel
    game_data = helper.open_json("games.json")
    message_id = game_data.get(game_link, {}).get("host-message")
    if not message_id:
        await interaction.followup.send(
            "No hosted game found to pause.", ephemeral=True
        )
        return
    try:
        message = await channel.fetch_message(message_id)
        await message.edit(content=game_data[game_link]["message"])
    except discord.NotFound:
        await interaction.followup.send(
            f"Message with ID {message_id} not found in channel {channel}.",
            ephemeral=True,
        )
    except discord.Forbidden:
        await interaction.followup.send(
            f"Bot does not have permission to edit the message.", ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.followup.send(
            f"Failed to edit the message: {str(e)}", ephemeral=True
        )


async def help_reping(interaction, game_link: str):
    if not helper.check_game_link(game_link):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            f"{game_link} is not a valid pokernow link", ephemeral=True
        )
        return

    game_data = helper.open_json("games.json")
    role_id = game_data.get(game_link, {}).get("ping")

    if not role_id:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            "No role set to ping for this game.", ephemeral=True
        )
        return

    role = discord.utils.get(interaction.guild.roles, id=int(role_id))

    if role is None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            f"Role with ID {role_id} not found.", ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(f"{role.mention} Seats Open!!")


async def help_end(interaction, game_link: str):
    if not helper.check_game_link(game_link):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            f"{game_link} is not a valid pokernow link", ephemeral=True
        )
        return
    
    game_data = helper.open_json("games.json")
    user_data = helper.open_json("user_info.json")

    user_id = str(interaction.user.id)
    if user_id != game_data.get(game_link, {}).get("host"):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("You can't end someone else's game", ephemeral=True)
        return

    if not game_data.get(game_link, {}).get("sf"):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            "Scam fund must be sent first, <#1262357471763107883>, send a screenshot of your venmo to @StackSociety and then type /sf [game_link]",
            ephemeral=True,
        )
        return

    if game_link in game_data and "host-message" in game_data[game_link]:
        channel = interaction.channel
        message_id = game_data[game_link]["host-message"]

        try:
            message = await channel.fetch_message(message_id)
            start_time = message.created_at
            await message.delete()
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("Hosted game message deleted.", ephemeral=True)
            
            log_channel_id = 1263327362515472479
            log_channel = interaction.guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(f"The game hosted by {interaction.user.mention} has ended. Game link: {game_link}, started {start_time}")
            
            game_data[game_link]["running"] = False
            helper.close_json("games.json", game_data)
            user_data[user_id]["hosting"] = "None"
            helper.close_json("user_info.json", user_data)
        except discord.NotFound:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("Message not found.", ephemeral=True)
    else:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("No hosted game found to end.", ephemeral=True)


async def help_sf(ctx, bot):
    game_data = helper.open_json("games.json")
    user_data = helper.open_json("user_info.json")
    user_id = str(ctx.author.id)
    game_link = user_data[user_id]["hosting"]
    messages = await ctx.channel.history(limit=5).flatten()
    messages = [msg for msg in messages if msg.author.id != bot.user.id]

    if len(messages) < 1:
        await ctx.respond("No previous message found.", ephemeral=True)
        return

    previous_message = messages[0]

    if previous_message.author.id == ctx.author.id:
        image_urls = [
            attachment.url
            for attachment in previous_message.attachments
            if attachment.content_type and attachment.content_type.startswith("image/")
        ]
        if image_urls:
            await ctx.respond(
                f"The previous message contains an image: {image_urls[-1]}"
            )
            game_data[game_link]["sf"] = True
            game_type = game_data[game_link]["game-type"] + "-sf"
            user_data[user_id][game_type] += 1
            helper.close_json("games.json", game_data)
        else:
            await ctx.respond(
                "The previous message does not contain an image.", ephemeral=True
            )
    else:
        await ctx.respond("The previous message is not from you.", ephemeral=True)


async def help_check_roles(ctx, member: discord.Member):
    roles_to_check = ["trusted", "L tipper", "huge tipper", "admin", "Verified", "Accredited", "Lead"]
    roles = [role.name for role in member.roles]
    missing_roles = [role for role in roles_to_check if role not in roles]
    roles_had = [i for i in roles_to_check if i not in missing_roles]
    if roles_had:
        message = f"{member.mention} has the roles: {', '.join(roles_had)}"
    else:
        message = f"{member.mention} has none of the roles."
    await ctx.respond(message, ephemeral=True)
