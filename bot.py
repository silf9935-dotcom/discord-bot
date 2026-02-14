import discord
from discord.ext import commands
import os
from datetime import timedelta
import sqlite3
import re
import asyncio

TOKEN = os.getenv("TOKEN")

LOG_CHANNEL_ID = 1464584421205082215
ROLES_CHANNEL_ID = 1471485984372818025

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# 🔹 DATABASE (SQLite)
# =========================

conn = sqlite3.connect("warnings.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS warnings (
    user_id INTEGER,
    guild_id INTEGER,
    count INTEGER
)
""")
conn.commit()

def get_warns(user_id, guild_id):
    cursor.execute("SELECT count FROM warnings WHERE user_id=? AND guild_id=?", (user_id, guild_id))
    data = cursor.fetchone()
    return data[0] if data else 0

def add_warn(user_id, guild_id):
    warns = get_warns(user_id, guild_id)
    if warns == 0:
        cursor.execute("INSERT INTO warnings VALUES (?, ?, ?)", (user_id, guild_id, 1))
    else:
        cursor.execute("UPDATE warnings SET count=? WHERE user_id=? AND guild_id=?", (warns+1, user_id, guild_id))
    conn.commit()

# =========================
# 🔹 EMBED TEMPLATE
# =========================

def log_embed(title, member, moderator, reason, color):
    embed = discord.Embed(
        title=title,
        color=color
    )
    embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Moderator", value=f"{moderator}", inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    return embed

# =========================
# 🔹 MUTE
# =========================

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
    await ctx.message.delete()

    duration = timedelta(minutes=minutes)
    await member.timeout(discord.utils.utcnow() + duration, reason=reason)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    embed = log_embed("🔇 USER MUTED", member, ctx.author, reason, discord.Color.orange())
    embed.add_field(name="Duration", value=f"{minutes} minutes", inline=False)

    await log_channel.send(embed=embed)

# =========================
# 🔹 WARN (3 = AUTO MUTE)
# =========================

@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()

    add_warn(member.id, ctx.guild.id)
    warns = get_warns(member.id, ctx.guild.id)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    embed = log_embed("⚠ USER WARNED", member, ctx.author, reason, discord.Color.gold())
    embed.add_field(name="Total Warns", value=str(warns), inline=False)

    await log_channel.send(embed=embed)

    # Авто-мут после 3 варнов
    if warns >= 3:
        duration = timedelta(minutes=10)
        await member.timeout(discord.utils.utcnow() + duration, reason="3 Warnings")
        embed = log_embed("🔇 AUTO MUTE (3 WARNS)", member, bot.user, "Reached 3 warnings", discord.Color.red())
        await log_channel.send(embed=embed)

# =========================
# 🔹 KICK
# =========================

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()

    await member.kick(reason=reason)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    embed = log_embed("👢 USER KICKED", member, ctx.author, reason, discord.Color.red())
    await log_channel.send(embed=embed)

# =========================
# 🔹 BAN
# =========================

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()

    await member.ban(reason=reason)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    embed = log_embed("🔨 USER BANNED", member, ctx.author, reason, discord.Color.dark_red())
    await log_channel.send(embed=embed)

# =========================
# 🔹 ANTI-SPAM
# =========================

spam_tracker = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Авто реакция
    if message.channel.id == ROLES_CHANNEL_ID:
        await message.add_reaction("🟦")

    # Анти-линки
    if re.search(r"https?://", message.content):
        if not message.author.guild_permissions.manage_messages:
            await message.delete()
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            embed = discord.Embed(
                title="🚫 LINK DELETED",
                description=f"{message.author} posted a link.",
                color=discord.Color.red()
            )
            await log_channel.send(embed=embed)
            return

    # Анти-спам (5 сообщений за 5 секунд)
    user = message.author.id
    if user not in spam_tracker:
        spam_tracker[user] = []

    spam_tracker[user].append(message.created_at)

    if len(spam_tracker[user]) > 5:
        first = spam_tracker[user][0]
        last = spam_tracker[user][-1]
        if (last - first).seconds <= 5:
            await message.author.timeout(discord.utils.utcnow() + timedelta(minutes=5), reason="Spam")
            await message.channel.purge(limit=5)
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            embed = discord.Embed(
                title="🚨 AUTO SPAM MUTE",
                description=f"{message.author} muted for spam.",
                color=discord.Color.red()
            )
            await log_channel.send(embed=embed)
            spam_tracker[user] = []

    await bot.process_commands(message)

bot.run(TOKEN)
