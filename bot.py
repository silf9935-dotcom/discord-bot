import discord
from discord.ext import commands
import os
import asyncio
from datetime import timedelta
from fastapi import FastAPI
import uvicorn

# =======================
# 🔹 Настройки
# =======================

TOKEN = os.getenv("TOKEN")

LOG_CHANNEL_ID = 1464584421205082215  # Канал логов
ROLES_CHANNEL_ID = 1471485984372818025  # Канал ролей

# =======================
# 🔹 Бот
# =======================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =======================
# 🔹 Приветствие
# =======================

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(
            f"✨ Welcome **{member.guild.name}**, {member.mention}! 🎉\n"
            "Glad to have you here! Make sure to read the rules and grab your roles!"
        )

# =======================
# 🔹 Авто-реакция на канал roles
# =======================

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.id == ROLES_CHANNEL_ID:
        await message.add_reaction("🟦")
    await bot.process_commands(message)

# =======================
# 🔹 Мут
# =======================

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
    duration = timedelta(minutes=minutes)
    await member.timeout(discord.utils.utcnow() + duration, reason=reason)

    # Удаляем сообщение пользователя сразу
    try:
        await ctx.message.delete()
    except:
        pass

    # Лог в канал
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        msg = await log_channel.send(
            f"🔇 **User Muted**\n"
            f"👤 User: {member}\n"
            f"👮 Moderator: {ctx.author}\n"
            f"⏳ Duration: {minutes} minutes\n"
            f"📄 Reason: {reason}"
        )
        await asyncio.sleep(10)
        await msg.delete()

    # ЛС пользователю
    try:
        await member.send(
            f"⚠️ You have been muted in **{ctx.guild.name}**\n"
            f"⏳ Duration: {minutes} minutes\n"
            f"📄 Reason: {reason}"
        )
    except:
        pass

    await ctx.send(f"🔇 {member.mention} has been muted for {minutes} minutes.", delete_after=10)

# =======================
# 🔹 Warn
# =======================

@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    try:
        await ctx.message.delete()
    except:
        pass

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        msg = await log_channel.send(
            f"⚠️ **User Warned**\n"
            f"👤 User: {member}\n"
            f"👮 Moderator: {ctx.author}\n"
            f"📄 Reason: {reason}"
        )
        await asyncio.sleep(10)
        await msg.delete()

    try:
        await member.send(
            f"⚠️ You have received a warning in **{ctx.guild.name}**\n"
            f"📄 Reason: {reason}"
        )
    except:
        pass

    await ctx.send(f"⚠️ {member.mention} has been warned.", delete_after=10)

# =======================
# 🔹 Kick
# =======================

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    try:
        await ctx.message.delete()
    except:
        pass

    await member.kick(reason=reason)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        msg = await log_channel.send(
            f"👢 **User Kicked**\n"
            f"👤 User: {member}\n"
            f"👮 Moderator: {ctx.author}\n"
            f"📄 Reason: {reason}"
        )
        await asyncio.sleep(10)
        await msg.delete()

    await ctx.send(f"👢 {member.mention} has been kicked.", delete_after=10)

# =======================
# 🔹 Ban
# =======================

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    try:
        await ctx.message.delete()
    except:
        pass

    await member.ban(reason=reason)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        msg = await log_channel.send(
            f"🔨 **User Banned**\n"
            f"👤 User: {member}\n"
            f"👮 Moderator: {ctx.author}\n"
            f"📄 Reason: {reason}"
        )
        await asyncio.sleep(10)
        await msg.delete()

    await ctx.send(f"🔨 {member.mention} has been banned.", delete_after=10)

# =======================
# 🔹 Мини-вебсервер для Render
# =======================

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Bot is running"}

# =======================
# 🔹 Запуск
# =======================

import threading

def run_discord():
    bot.run(TOKEN)

# Запускаем Discord в отдельном потоке
threading.Thread(target=run_discord).start()

# Запускаем FastAPI вебсервер для Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
