
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

bot = commands.Bot(command_prefix='!', intents=intents)

############################
##### Helper Functions #####
############################
def parse_dice_roll(notation):
    try:
        num_dice, sides = notation.lower().split('d')
        num_dice = int(num_dice)
        sides = int(sides)
        return num_dice, sides
    except ValueError:
        return None

# Function to perform the dice rolls
def roll_dice(num_dice, sides):
    if sides not in {4, 6, 8, 10, 12, 20}:
        return None, "Invalid number of sides! Please choose from 4, 6, 8, 10, 12, or 20."
    results = [random.randint(1, sides) for _ in range(num_dice)]
    total = sum(results)
    return results, f"You rolled {num_dice}d{sides}: {results} Total: {total}"

####################
##### Commands #####
####################

@bot.command(name='roll')
async def roll(ctx, dice: str):
    # input notation examples: '2d6', '1d4', 5d12'
    parsed = parse_dice_roll(dice)
    if parsed:
        num_dice, sides = parsed
        results, message = roll_dice(num_dice, sides)
        if results is not None:
            await ctx.send(message)
        else:
            await ctx.send(message)
    else:
        await ctx.send("Invalid dice notation! Use the format 'NdS' where N is number of dice and S is sides.")

##################
##### Events #####
##################

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

bot.run(TOKEN)