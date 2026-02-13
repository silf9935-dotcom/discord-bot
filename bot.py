import discord
from discord.ext import commands
import os
from datetime import timedelta

TOKEN = os.getenv("TOKEN")

LOG_CHANNEL_ID = 1464584421205082215
ROLES_CHANNEL_ID = 1471485984372818025

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# 🔹 Приветствие
# ========================

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(
            f"✨ Welcome to **{member.guild.name}**, {member.mention}!\n"
            f"We're excited to have you here! 🎉\n"
            f"Make sure to read the rules and grab your roles!"
        )

# ========================
# 🔹 Мут
# ========================

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
    await ctx.message.delete()

    duration = timedelta(minutes=minutes)
    await member.timeout(discord.utils.utcnow() + duration, reason=reason)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    if log_channel:
        await log_channel.send(
            f"🔇 **User Muted**\n"
            f"👤 User: {member}\n"
            f"👮 Moderator: {ctx.author}\n"
            f"⏳ Duration: {minutes} minutes\n"
            f"📄 Reason: {reason}"
        )

    try:
        await member.send(
            f"⚠️ You have been muted in **{ctx.guild.name}**\n"
            f"⏳ Duration: {minutes} minutes\n"
            f"📄 Reason: {reason}"
        )
    except:
        pass

# ========================
# 🔹 Warn
# ========================

@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()

    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    if log_channel:
        await log_channel.send(
            f"⚠️ **User Warned**\n"
            f"👤 User: {member}\n"
            f"👮 Moderator: {ctx.author}\n"
            f"📄 Reason: {reason}"
        )

    try:
        await member.send(
            f"⚠️ You have received a warning in **{ctx.guild.name}**\n"
            f"📄 Reason: {reason}"
        )
    except:
        pass

# ========================
# 🔹 Kick
# ========================

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()

    await member.kick(reason=reason)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            f"👢 **User Kicked**\n"
            f"👤 User: {member}\n"
            f"👮 Moderator: {ctx.author}\n"
            f"📄 Reason: {reason}"
        )

# ========================
# 🔹 Ban
# ========================

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()

    await member.ban(reason=reason)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            f"⛔ **User Banned**\n"
            f"👤 User: {member}\n"
            f"👮 Moderator: {ctx.author}\n"
            f"📄 Reason: {reason}"
        )

# ========================
# 🔹 Авто-реакция
# ========================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == ROLES_CHANNEL_ID:
        await message.add_reaction("🟦")

    await bot.process_commands(message)

bot.run(TOKEN)
