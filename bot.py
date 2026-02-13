import discord
from discord.ext import commands, tasks
import os
from datetime import timedelta
import asyncio

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
            f"✨ Hey {member.mention}, welcome to **{member.guild.name}**! 🎉\n"
            f"Check out the rules and grab your roles!"
        )

# ========================
# 🔹 Удаление сообщения после действия
# ========================
async def delete_messages(original_message, bot_message, delay=10):
    try:
        await original_message.delete()
    except:
        pass
    await asyncio.sleep(delay)
    try:
        await bot_message.delete()
    except:
        pass

# ========================
# 🔹 Мут
# ========================
@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
    duration = timedelta(minutes=minutes)
    await member.timeout(discord.utils.utcnow() + duration, reason=reason)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    bot_msg = await ctx.send(f"🔇 {member.mention} has been muted for {minutes} minutes.")
    asyncio.create_task(delete_messages(ctx.message, bot_msg))

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
    bot_msg = await ctx.send(f"⚠️ {member.mention} has been warned.")
    asyncio.create_task(delete_messages(ctx.message, bot_msg))

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
    bot_msg = await ctx.send(f"👢 {member.mention} has been kicked.")
    asyncio.create_task(delete_messages(ctx.message, bot_msg))

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            f"👢 **User Kicked**\n"
            f"👤 User: {member}\n"
            f"👮 Moderator: {ctx.author}\n"
            f"📄 Reason: {reason}"
        )
    try:
        await member.send(
            f"⚠️ You have been kicked from **{ctx.guild.name}**\n"
            f"📄 Reason: {reason}"
        )
    except:
        pass
    await member.kick(reason=reason)

# ========================
# 🔹 Ban
# ========================
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    bot_msg = await ctx.send(f"⛔ {member.mention} has been banned.")
    asyncio.create_task(delete_messages(ctx.message, bot_msg))

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            f"⛔ **User Banned**\n"
            f"👤 User: {member}\n"
            f"👮 Moderator: {ctx.author}\n"
            f"📄 Reason: {reason}"
        )
    try:
        await member.send(
            f"⚠️ You have been banned from **{ctx.guild.name}**\n"
            f"📄 Reason: {reason}"
        )
    except:
        pass
    await member.ban(reason=reason)

# ========================
# 🔹 Реакция в канале roles
# ========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == ROLES_CHANNEL_ID:
        await message.add_reaction("🟦")

    await bot.process_commands(message)

bot.run(TOKEN)
