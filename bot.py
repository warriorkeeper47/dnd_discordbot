
import discord
import os
from discord.ext import commands
import aiosqlite
import random
from datetime import datetime
from dotenv import load_dotenv

intents = discord.Intents.all()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command(name='roll')
async def roll(ctx, sides: int):
    """Rolls a dice with a specified number of sides from a fixed set."""
    allowed_sides = {20, 12, 10, 8, 6, 4}  # Allowed numbers of sides for the dice
    if sides not in allowed_sides:
        await ctx.send("Invalid number of sides! Please choose from 20, 12, 10, 8, 6, or 4.")
    else:
        result = random.randint(1, sides)
        await ctx.send(f"🎲 You rolled a {sides}-sided dice and got: {result}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

bot.run(TOKEN)

# @bot.event
# async def on_ready():
#     async with aiosqlite.connect('profiles.db') as db:
#         await db.execute('''
#             CREATE TABLE IF NOT EXISTS profiles (
#                 user_id INTEGER PRIMARY KEY, 
#                 username TEXT, 
#                 role TEXT DEFAULT 'player'
#             )
#         ''')
#         await db.execute('''
#             CREATE TABLE IF NOT EXISTS rolls (
#                 user_id INTEGER,
#                 dice_type TEXT,
#                 result INTEGER,
#                 timestamp TEXT,
#                 FOREIGN KEY(user_id) REFERENCES profiles(user_id)
#             )
#         ''')
#         await db.commit()

# @bot.command(name='createProfile')
# async def create_profile(ctx, role='player'):
#     async with aiosqlite.connect('profiles.db') as db:
#         await db.execute('''
#             INSERT INTO profiles (user_id, username, role) 
#             VALUES (?, ?, ?) 
#             ON CONFLICT(user_id) DO UPDATE SET role=excluded.role
#         ''', (ctx.author.id, ctx.author.name, role))
#         await db.commit()
#     await ctx.send(f'Profile created with role: {role}')

# @bot.command(name='roll')
# async def roll(ctx, dice: str):
#     if dice.lower() not in ['20', '12', '10', '8', '6', '4']:
#         await ctx.send("Invalid dice type. Use d4, d6, d8, d10, d12, or d20.")
#         return

#     sides = int(dice[1:])
#     result = random.randint(1, sides)

#     async with aiosqlite.connect('profiles.db') as db:
#         await db.execute('INSERT INTO rolls (user_id, dice_type, result, timestamp) VALUES (?, ?, ?, ?)', 
#                          (ctx.author.id, dice.upper(), result, datetime.now().isoformat()))
#         await db.commit()

#     await ctx.send(f"{dice.upper()} roll: {result}")

# @bot.command(name='history')
# async def history(ctx):
#     async with aiosqlite.connect('profiles.db') as db:
#         cursor = await db.execute('SELECT dice_type, result, timestamp FROM rolls WHERE user_id = ?', (ctx.author.id,))
#         rolls = await cursor.fetchall()
#         if rolls:
#             response = '\n'.join([f"{roll[0]}: {roll[1]} at {roll[2]}" for roll in rolls])
#             await ctx.send(f"Your roll history:\n{response}")
#         else:
#             await ctx.send("You have no recorded rolls.")

#bot.run('3b88d992468b1d347d10a7a8d51bccbbebd9b2550ccb2f1f5a346bb21525b0f3')
