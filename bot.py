import discord
from discord.ext import commands, tasks
import os
from datetime import timedelta
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv("PORT", 10000))

LOG_CHANNEL_ID = 1464584421205082215
ROLES_CHANNEL_ID = 1471485984372818025

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# 🔹 Keep alive (для Render)
# ========================

app = web.Application()
async def handle(request):
    return web.Response(text="Bot is alive!")

app.router.add_get("/", handle)

def start_webserver():
    runner = web.AppRunner(app)
    loop = bot.loop
    async def start():
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', PORT)
        await site.start()
    loop.create_task(start())

start_webserver()

# ========================
# 🔹 Приветствие
# ========================

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(
            f"✨ Welcome to **{member.guild.name}**, {member.mention}! 🎉\n"
            f"Glad to have you here. Check the rules and pick your roles!"
        )

# ========================
# 🔹 Авто-реакция в канале roles
# ========================

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.id == ROLES_CHANNEL_ID:
        await message.add_reaction("🟦")
    await bot.process_commands(message)

# ========================
# 🔹 Вспомогательная функция для логов
# ========================

async def send_log(ctx, action, member, reason="", duration=None):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return
    msg = f"**{action}**\n👤 User: {member}\n👮 Moderator: {ctx.author}\n"
    if duration:
        msg += f"⏳ Duration: {duration} minutes\n"
    if reason:
        msg += f"📄 Reason: {reason}"
    await channel.send(f"{ctx.author.mention} | {msg}")

# ========================
# 🔹 Команды модерации
# ========================

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
    # Таймаут
    await member.timeout(discord.utils.utcnow() + timedelta(minutes=minutes), reason=reason)
    # Лог
    await send_log(ctx, "User Muted", member, reason, minutes)
    # ЛС пользователю
    try:
        await member.send(f"⚠️ You have been muted in **{ctx.guild.name}** for {minutes} minutes.\nReason: {reason}")
    except: pass
    # Удаляем команду
    await ctx.message.delete()
    # Только модератор видит сообщение
    await ctx.author.send(f"✅ {member} muted for {minutes} minutes.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    await send_log(ctx, "User Warned", member, reason)
    try:
        await member.send(f"⚠️ You have received a warning in **{ctx.guild.name}**.\nReason: {reason}")
    except: pass
    await ctx.message.delete()
    await ctx.author.send(f"✅ {member} warned.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await send_log(ctx, "User Kicked", member, reason)
    await ctx.message.delete()
    await ctx.author.send(f"✅ {member} kicked.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await send_log(ctx, "User Banned", member, reason)
    await ctx.message.delete()
    await ctx.author.send(f"✅ {member} banned.")

# ========================
# 🔹 Запуск
# ========================

bot.run(TOKEN)
