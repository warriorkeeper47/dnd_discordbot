
import discord
import os
from discord.ext import commands
import aiosqlite # TODO store roles and profiles
import random
from datetime import datetime
from dotenv import load_dotenv

intents = discord.Intents.all()

load_dotenv()
TOKEN = "MTIzMjQ3NDkwODM0MTA0NzM3Nw.G0XG_a.88RFhXdZk5HB8NX_BTNVQOD4SFw_Lw8Qe6wN_o" 
#os.getenv('DISCORD_TOKEN')

bot = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='/', intents=intents)

### Global Variables ###
initOrder = []

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

# Initiative methods
def sort_init():
    initOrder.sort(key=lambda x: x[1], reverse=True)

def show_init():
    sort_init()
    return f"Initiative order: {initOrder}"

def add_init(name, roll):
    if name not in initOrder:
        initOrder.append((name, roll))
        sort_init()
        message=f"Added {name} with initiative {roll}."
    else:
        remove_init(name)
        add_init(name, roll)
        sort_init()
        message=f"'{name}' already in initiative order. Updated number {roll}"
    return message

def remove_init(name):
    global initOrder
    removedArr = [n for n in initOrder if n[0] != name]
    if removedArr == initOrder:
        message=f"Name '{name}' not found in initiative order."
    else:
        initOrder = removedArr
        message=f"Removed {name} from initiative order."    
    return message

def clear_init():
    initOrder.clear()
    return f"Initiative order has been cleared."

def generate_name():
    return "John" #TODO update to include Faker library

####################
##### Commands #####
####################

@bot.command(name='roll')
async def roll(ctx, dice: str):
    # input notation examples: '2d6', '1d4', 5d12'
    try:
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
    except ValueError:
        ctx.send("Invalid prompt.")

@bot.command(name='init')
async def init(ctx, com: str, name: str=None, roll: int=0):
    print("called init")
    print(f"initOrder before: {initOrder}")
    com = com.lower()
    print(f"com: {com}")
    if com == "add":
        if roll <= 0 or roll==None:
            await ctx.send("No number given for initiative order.")
        else:
            message = add_init(name, roll)
            await ctx.send(message)
    elif com == "addnpc":
        if roll == None or roll <= 0:
            roll = roll_dice(1, 20)
            await ctx.send("No dice roll found... Rolling dice for NPC...")
        if name == None or name == "":
            name = generate_name()
            await ctx.send("No name found... Generating name for NPC...")
        message = add_init(name, roll)
        await ctx.send(message)
    elif com == "remove":
        if name==None or name=="":
            await ctx.send("No name given to remove from initiative order.")
        else:
            message = remove_init(name)
            await ctx.send(message)
    elif com == "show":
        await ctx.send(show_init())
    elif com == "clear":
        message = clear_init()
        await ctx.send(message)
    else:
        await ctx.send("Command unknown for 'init'")
    print(f"initOrder after: {initOrder}")

##################
##### Events #####
##################

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

bot.run(TOKEN)
