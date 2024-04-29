
import discord
import os
from discord.ext import commands
import aiosqlite # TODO store roles and profiles
import random
from datetime import datetime
from dotenv import load_dotenv

intents = discord.Intents.all()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='/', intents=intents)

### Global Variables ###
initOrder = []

####################
### DB FUNCTIONS ###
####################

async def setup_database():
    async with aiosqlite.connect('bot_database.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id INTEGER UNIQUE,
            name TEXT,
            role TEXT
        )''')
        await db.commit()

async def add_or_update_user(discord_id, name: str, role: str):
    async with aiosqlite.connect('bot_database.db') as db:
        cursor = await db.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,))
        result = await cursor.fetchone()
        if result:
            await db.execute('UPDATE users SET name = ?, role = ? WHERE discord_id = ?', (name, role, discord_id))
        else:
            await db.execute('INSERT INTO users (discord_id, name, role) VALUES (?, ?, ?)', (discord_id, name, role))
        await db.commit()

async def print_all_users():
    users = []
    async with aiosqlite.connect('bot_database.db') as db:
        cursor = await db.execute('SELECT discord_id, name FROM users')
        rows = await cursor.fetchall()
        if rows:
            for row in rows:
                users.append(f"ID: {row[0]}, Name: {row[1]}")
            return "\n".join(users)
        else:
            return "No users found in the database."

############################
##### Helper Functions #####
############################

# Roles and Permissions
async def assign_role(discord_id, role):
    async with aiosqlite.connect('bot_database.db') as db:
        await db.execute('UPDATE users SET role = ? WHERE discord_id = ?', (role, discord_id))
        await db.commit()

async def check_permission(ctx, memberID:str=""):
    async with aiosqlite.connect('bot_database.db') as db:
        cursor = await db.execute('SELECT role FROM users WHERE discord_id = ?', (memberID))
        role = await cursor.fetchone()
        if role:
            print(f"role: {role[0]}")
            return role[0]
        else:
            print("no role found")
            return None

# Dice Rolls
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

# Initiative
def sort_init():
    initOrder.sort(key=lambda x: x[1], reverse=True)

def show_init():
    sort_init()
    return f"Initiative order: {initOrder}"

def add_init(name, roll):
    global initOrder
    for i, (existing_name, _) in enumerate(initOrder):
        if existing_name == name:
            initOrder[i] = (name, roll)  # Update
            sort_init()
            return f"'{name}' already in initiative order. Updated number to {roll}."
    initOrder.append((name, roll))
    sort_init()
    return f"Added {name} with initiative {roll}."

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

# Character Building
def generate_name():
    return "John" #TODO update to include Faker library

####################
##### Commands #####
####################

@bot.command(name='setrole')
#@commands.has_permissions(administrator=True)
async def set_role(ctx, member: discord.Member, role: str="player"):
    await assign_role(member.id, role)
    await ctx.send(f"Role {role} assigned to {member.name}.")

@bot.command(name='getrole')
async def get_role(ctx, member: discord.Member):
    role = await check_permission(ctx, member.id)
    if role:
        await ctx.send(f"{member.name}'s role is {role}.")
    else:
        await ctx.send(f"{member.name} does not have a role assigned.")
    

@bot.command(name='myrole')
async def my_role(ctx):
    role = await check_permission(ctx, ctx.author.id)
    if role:
        await ctx.send(f"Your role is {role}.")
    else:
        await ctx.send("You do not have a role assigned.")

@bot.command(name='register')
async def register(ctx, role:str="player"): # TODO check if admin
    discord_id = ctx.author.id  # Discord ID
    name = ctx.author.name      # Discord username
    await add_or_update_user(discord_id, name, role)
    await ctx.send(f"{name}, you have been registered/updated with role: {role}.")

@bot.command(name='printUsers')
async def printUsers(ctx):
    message = await print_all_users()
    await ctx.send(message)

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
    elif com == "addnpc": #TODO not working as expected
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
    await setup_database()
    await update_database_schema()

async def column_exists(db, table_name, column_name):
    cursor = await db.execute(f"PRAGMA table_info({table_name})")
    columns = await cursor.fetchall()
    return any(column_name == column[1] for column in columns)

async def update_database_schema():
    async with aiosqlite.connect('bot_database.db') as db:
        if not await column_exists(db, 'users', 'role'):
            await db.execute('ALTER TABLE users ADD COLUMN role TEXT')
            await db.commit()

bot.run(TOKEN)
