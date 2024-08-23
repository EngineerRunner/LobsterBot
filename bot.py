import discord
from discord.ext import commands
import requests
import time
import dotenv
import os

intents = discord.Intents.default()
intents.message_content = True

description = '''a w take bot'''

dotenv.load_dotenv()

bot = commands.Bot(command_prefix='?', description=description, intents=intents, help_command=None)
bot.remove_command('help')
# WHEN THE APP GETS ACCEPTED
hypixel_api_key = os.getenv("APIKEY")


headers = {"API-Key":hypixel_api_key}

ranks = {
    "MVP_PLUS": "[MVP+]",
    "MVP": "[MVP]",
    "VIP_PLUS": "[VIP+]",
    "VIP": "[VIP]",
    "NONE": "[NOOB]"
}
def get_uuid(username):
    try:
        response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}").json()
        print(response)
        return response["id"]
    except:
        return None

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('engineer gaming')
    await bot.process_commands(message)

@bot.command()
async def user(ctx, username:str):
    """Gets info on a user"""
    uuid = get_uuid(username)
    if uuid == None:
        await ctx.send("Error: user not found")
        return
    userinfo = requests.get(f"https://api.hypixel.net/v2/player?uuid={uuid}", headers=headers).json()
    useractivity = requests.get(f"https://api.hypixel.net/v2/status?uuid={uuid}", headers=headers).json()
    gamenames = requests.get("https://api.hypixel.net/v2/resources/games", headers=headers).json()
    print(useractivity)
    if userinfo["success"] != True:
        await ctx.send("Error: user may have not played hypixel")
    if useractivity["session"]["online"] == True:
        userGame = useractivity["session"]["gameType"]
        prettifiedGame = gamenames["games"][userGame]["name"]
        try:

            userMode = useractivity["session"]["mode"]
            if userMode == "LOBBY":
                prettifiedMode = "Lobby"
            else:
                prettifiedMode = gamenames["games"][userGame]["modeNames"][userMode]
            try:
                usermap = useractivity["session"]["map"]
                activitymessage = f"is online, playing {prettifiedGame}, in mode {prettifiedMode}, on map {usermap}."
            except:
                activitymessage = f"is online, playing {prettifiedGame}, in mode {prettifiedMode}."
        except:
            activitymessage = f"is online, playing {prettifiedGame}."
    else:
        lastlogin = round(userinfo["player"]["lastLogin"] / 1000)
        activitymessage = f"is offline, and last logged in <t:{lastlogin}:R>"
    
    try:
        mvpplusplus = userinfo["player"]["monthlyPackageRank"] == "SUPERSTAR"
    except:
        mvpplusplus = False
    if mvpplusplus:
        rank = "[MVP++]"
    else:
        rank = ranks[userinfo["player"]["newPackageRank"]]
    await ctx.send(f"""
{rank}{username} {activitymessage}
[Body](https://api.mineatar.io/body/full/{uuid}?scale=32)
""")

@bot.command()
async def watchdog(ctx):
    """gets watchdog and the admins stats"""
    r = requests.get("https://api.hypixel.net/v2/punishmentstats", headers=headers).json()
    if r["success"]:
        stafftoday = r["staff_rollingDaily"]
        watchdogtoday = r["watchdog_rollingDaily"]
        if stafftoday > watchdogtoday:
            message = f"""W admins: Today, the Hypixel admins have punished {stafftoday} bozos, while Watchdog has only punished {watchdogtoday}."""
        elif watchdogtoday > stafftoday:
            message = f"""L admins: Today, the Hypixel admins have only punished {stafftoday} bozos, while Watchdog has banhammered {watchdogtoday}."""
        elif watchdogtoday == stafftoday:
            message = f"""Perfectly balanced?? Both the admins _and_ Watchdog have banned {stafftoday} noobs!?"""
        await ctx.send(message)
    else:
        await ctx.send("error: unknown error, ask @EngineerRunner")

@bot.command()
async def stats(ctx, username:str):
    """gets user stats"""
    uuid = get_uuid(username)
    if uuid == None:
        await ctx.send("Error: user not found")
        return
    userinfo = requests.get(f"https://api.hypixel.net/v2/player?uuid={uuid}", headers=headers).json()
    if userinfo["success"] == False:
        await ctx.send("Error: user has not played Hypixel")
        return
    stats = userinfo["player"]["stats"]["Bedwars"]
    kills = stats["kills_bedwars"]
    deaths = stats["deaths_bedwars"]
    finalkills = stats["final_kills_bedwars"]
    finaldeaths = stats["final_deaths_bedwars"]
    kdr = round(kills / deaths, 2)
    fkdr = round(finalkills / finaldeaths, 2)
    try:
        mvpplusplus = userinfo["player"]["monthlyPackageRank"] == "SUPERSTAR"
    except:
        mvpplusplus = False
    if mvpplusplus:
        rank = "[MVP++]"
    else:
        rank = ranks[userinfo["player"]["newPackageRank"]]
    await ctx.send(f"""
{rank}{username} has a KDR of {kdr} ({kills} kills, {deaths} deaths) and an FKDR of {fkdr} ({finalkills} final kills, {finaldeaths} final deaths).
[Body](https://api.mineatar.io/body/full/{uuid}?scale=32)""")

@bot.command()
async def help(ctx):
     await ctx.send("""
# LobsterBot <:lobter:1275711085399248917> v1.0.0
## Commands:
### ?help
Shows this menu.
### ?user [hypixel-username]
Gets some basic information about a user.
### ?stats [hypixel-username]
Gets a user's BedWars stats.
### ?watchdog
Compares Watchdog and the Hypixel Staff: who can ban the most noobs?
### ?dailygames [hypixel-username]
Tells you how many BedWars games a user plays per day.                

-# made by @EngineerRunner
""")

@bot.command()
async def dailygames(ctx, username):
    uuid = get_uuid(username)
    if uuid == None:
        await ctx.send("Error: user not found")
        return
    userinfo = requests.get(f"https://api.hypixel.net/v2/player?uuid={uuid}", headers=headers).json()
    if userinfo["success"] == False:
        await ctx.send("Error: user has not played Hypixel")
        return
    firstLogin = userinfo["player"]["firstLogin"] / 1000
    currenttime = time.time()
    secondsplayed = currenttime - firstLogin
    daysplayed = round(secondsplayed / 86400)
    gamesplayed = userinfo["player"]["stats"]["Bedwars"]["games_played_bedwars"]
    gamesperday = round(gamesplayed / daysplayed, 2)
    if gamesperday > 1 and gamesperday < 2:
        await ctx.send(f"{username} plays an average of {gamesperday} BedWars matches a day. They need to go touch some grass IMHO.")
    elif gamesperday < 1 and gamesperday:
        await ctx.send(f"{username} has played an average of only {gamesperday} BedWars matches per day. No sweatiness here!")
    elif gamesperday == 1:
        await ctx.send(f"{username} has played exactly {gamesperday} BedWars matches per day. They're perfectly balanced!")
    elif gamesperday > 2:
        await ctx.send(f"{username} plays an average of _{gamesperday} BedWars matches_ a day!? They need grass ASAP")



bot.run(os.getenv("BOTTOKEN"))