import discord
roles = discord.Option(
        str, choices=["Unverified", "Accredited", "Verified", "Lead", "Admin"])
games = discord.Option(
        str, choices=["Unverified", "Accredited", "Verified", "Lead", "Admin"])