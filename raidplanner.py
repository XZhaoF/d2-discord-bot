import asyncio
import logging
import discord
import time
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.utils import find

#_Token = open("discordtoken.txt", "r").readline()
_Token = open("discordtokentest.txt", "r").readline()

# Set up logger and intent permissions
intents = discord.Intents.all()
intents.presences = False
intents.members = False
client = commands.Bot(command_prefix="-d2test", intents=intents)
logging.basicConfig(filename='log.txt', level=logging.INFO)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)

# Set the default help embed
helpembed = discord.Embed(type="rich", title='Destiny 2 Raid/LFG Bot', description="A bot made for organizing events specifically for Destiny 2\n", color=0xd56969)
helpembed.add_field(name="-d2raid [raid_name]", value="Creates an LFG planner, all available raids:\n\nVow of the Disciple - votd\nMaster Vow of the Disciple - mvotd\nVault of Glass - vog\nMaster Vault of Glass - mvog\nDeep Stone Crypt - dsc\nGarden of Salvation - gos\nLast Wish - lw\nKing's Fall - kf\n\nExample:    -d2raid votd")
helpembed.add_field(name="-d2help", value="Brings up this help embed")
helpembed.set_thumbnail(url="https://styles.redditmedia.com/t5_39br0/styles/communityIcon_q7wf9pe92v671.jpg")
helpembed.url = "https://discord.com/api/oauth2/authorize?client_id=951290000861986857&permissions=541166365760&scope=bot"
client.remove_command("help")

@client.event
async def on_ready():
    print('Bot is online')

@client.command()
async def raid(ctx, msg: str = None):

    votd_image = "https://cdn1.dotesports.com/wp-content/uploads/2022/03/05085411/Vow-of-the-Disciple-Entrance-scaled.jpg"
    lw_image = "https://images.gnwcdn.com/2018/articles/2018-09-14-13-49/destiny-2-last-wish-raid-start-time-rewards-5382-1536929323933.jpg/EG11/resize/1200x-1/destiny-2-last-wish-raid-start-time-rewards-5382-1536929323933.jpg"
    vog_image = "https://www.pcgamesn.com/wp-content/uploads/2021/04/destiny-2-vault-of-glass.jpg"
    gos_image = "https://assets.rockpapershotgun.com/images/2019/10/destiny-2-garden-of-salvation-f.jpg"
    dsc_image = "https://i.imgur.com/0U7Ao0q.jpg"
    kf_image = "https://assets.reedpopcdn.com/destiny-2-king's-fall.jpg/BROK/resize/1920x1920%3E/format/jpg/quality/80/destiny-2-king's-fall.jpg"

    image = None
    raid_name = None
    if msg == None:
        await ctx.send(f"No raid selected, -d2help to see all available raids")
        return
    if msg == "votd":
        image = votd_image
        raid_name = "Raid - Vow of The Disciple"
    elif msg == "mvotd":
        image = votd_image
        raid_name = "Raid - Master Vow of the Disciple"
    elif msg == "mvog":
        image = vog_image
        raid_name = "Raid - Master Vault of Glass"
    elif msg == "lw":
        image = lw_image
        raid_name = "Raid - Last Wish"
    elif msg == "vog":
        image = vog_image
        raid_name = "Raid - Vault of Glass"
    elif msg == "gos":
        image = gos_image
        raid_name = "Raid - Garden of Salvation"
    elif msg == "dsc":
        image = dsc_image
        raid_name = "Raid - Deep Stone Crypt"
    elif msg == "kf":
        image = kf_image
        raid_name = "Raid - King's Fall"
    else:
        await ctx.send(f"No such raid, -d2help to see all available raids")
        return


    _MAXRAIDPLAYERS = 6
    _STARTTIME, _MAXTIME, = time.time(), 3600,
    userList = []
    creator = ctx.message.author
    global is_deleted
    is_deleted = False

    userList.append(creator)
    embed = discord.Embed(title=raid_name + f' [{len(userList)}/{_MAXRAIDPLAYERS}]', description="♦︎ React to ☑️ to list yourself in the raid, remove to undo \n♦︎ Creator can remove post by reacting to ⛔ \n♦︎ Planner will timeout in 1 hour \n♦︎ You will be notified via DM when team is ready \n♦︎ Want to use me in another server? [click here](https://discord.com/api/oauth2/authorize?client_id=951290000861986857&permissions=541166365760&scope=bot)", color=discord.Color.purple())
    embed.set_author(name=creator.name, icon_url=creator.avatar_url)
    embed.set_image(url=image)
    embed.add_field(name=f'Player', value=f'🔹 {creator.name} (@{creator})', inline=False)
    try:
        sentEmbed = await ctx.send(embed=embed) 
        await ctx.message.delete()
    except discord.errors.Forbidden:
        await creator.send("It looks like I don't have permission in the channel you invoked a command in, please make sure I have both sufficient permissions.")
        return
    await sentEmbed.add_reaction("☑️")
    await sentEmbed.add_reaction("⛔")
    logging.info(f'{time.asctime( time.localtime(time.time()) )}       New session started with {creator}, {raid_name}')

    def is_active():
        return len(userList) < _MAXRAIDPLAYERS and not is_passhour() and not is_deleted

    def is_passhour():
        current_time = time.time()
        return current_time-_STARTTIME > _MAXTIME

    def is_bot(user):
        return user == client.user

    async def add_user_loop():
        try:
            while is_active():
                try:
                    payload = await client.wait_for('raw_reaction_add', timeout = 5.0, check= lambda payload: str(payload.emoji) == "☑️" and payload.message_id == sentEmbed.id)
                    guild = await client.fetch_guild(payload.guild_id)
                    user = await guild.fetch_member(payload.user_id)
                    if user not in userList and not is_bot(user):
                        userList.append(user)
                        embed.title = raid_name + f' [{len(userList)}/{_MAXRAIDPLAYERS}]'
                        embed.add_field(name=f'Player', value=f'🔹 {user.name} (@{user})', inline=False)
                        await sentEmbed.edit(embed=embed)
                    if len(userList) == _MAXRAIDPLAYERS:
                        await asyncio.sleep(2)
                    await ctx.fetch_message(sentEmbed.id)
                except asyncio.TimeoutError:
                    pass
                except discord.errors.NotFound:
                    logging.info(f'{time.asctime( time.localtime(time.time()) )}       Session with {creator}, {raid_name} was deleted')
                    return
            if len(userList) >= _MAXRAIDPLAYERS:
                embed.title = raid_name + " [Full - Closed]"
                await sentEmbed.edit(embed=embed)
                for user in userList:
                    if not is_bot(user):
                        await user.send('Raid team is now full', embed = embed)
                logging.info(f'{time.asctime( time.localtime(time.time()) )}       Session with {creator}, {raid_name} is full and completed')
            elif is_passhour():
                embed.title = raid_name + " [Expired - Closed]"
                await sentEmbed.edit(embed=embed)
                logging.info(f'{time.asctime( time.localtime(time.time()) )}       Session with {creator}, {raid_name} was expired and timed out')
        except discord.errors.NotFound:
            logging.info(f'{time.asctime( time.localtime(time.time()) )}       Session with {creator}, {raid_name} was deleted')
        except discord.errors.Forbidden:
            await creator.send("It looks like I don't have permission in the channel you invoked a command in, please make sure I have sufficient permissions.")



    async def remove_user_loop():
         while is_active():
            try:
                payload = await client.wait_for('raw_reaction_remove', timeout = 5.0, check= lambda payload: str(payload.emoji) == "☑️" and payload.message_id == sentEmbed.id)
                guild = await client.fetch_guild(payload.guild_id)
                user = await guild.fetch_member(payload.user_id)
                if user in userList and user != client.user:
                    embed.remove_field(userList.index(user))
                    userList.remove(user)
                    embed.title = raid_name + f' [{len(userList)}/{_MAXRAIDPLAYERS}]'
                    await sentEmbed.edit(embed=embed)
                await ctx.fetch_message(sentEmbed.id)
            except asyncio.TimeoutError:
                pass
            except discord.errors.NotFound:
                return

    async def creator_delete_loop():
        while is_active():
            try:
                payload = await client.wait_for('raw_reaction_add', timeout = 5.0, check= lambda payload: str(payload.emoji) == "⛔" and payload.message_id == sentEmbed.id)
                guild = await client.fetch_guild(payload.guild_id)
                user = await guild.fetch_member(payload.user_id)
                if user == creator and not is_bot(user):
                    global is_deleted
                    is_deleted = True
                    await sentEmbed.delete()
                    logging.info(f'{time.asctime( time.localtime(time.time()) )}       Session with {creator}, {raid_name} was deleted')
            except asyncio.TimeoutError:
                pass
            except discord.errors.NotFound:
                logging.info(f'{time.asctime( time.localtime(time.time()) )}       Session with {creator}, {raid_name} was deleted')
                return

    
    asyncio.create_task(add_user_loop())
    asyncio.create_task(remove_user_loop())
    asyncio.create_task(creator_delete_loop())

@client.command()
async def help(ctx):
    creator = ctx.message.author
    try:
        sentEmbed = await ctx.send(embed=helpembed)
    except discord.errors.Forbidden:
        await creator.send("It looks like I don't have permission in the channel you invoked a command in, please make sure I have both sufficient permissions.")
        return

@client.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send(embed=helpembed)

@tasks.loop(hours=720)
async def auto_delete_data():
    with open('log.txt', 'w'):
        pass
    logging.info(f'{time.asctime( time.localtime(time.time()) )}       New Log Session Has Started')

auto_delete_data.start()
client.run(_Token)

