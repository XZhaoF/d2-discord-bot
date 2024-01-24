import logging
import discord
import time
import uuid
import asyncio
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import find

_Token = open("discordtokentest.txt", "r").readline()

# Set up logger and intent permissions
intents = discord.Intents.all()
intents.presences = False
intents.members = False
client = commands.Bot(command_prefix="-d2", intents=intents)
logging.basicConfig(filename='log.txt', level=logging.INFO)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)

# Set the default help embed
helpembed = discord.Embed(type="rich", title='Destiny 2 Raid/LFG Bot', description="A bot made for organizing events specifically for Destiny 2\n", color=0xd56969)
helpembed.add_field(name="/d2 [activity]", value="Slash command: select an activity to create an LFG post")
helpembed.add_field(name="-d2help", value="Brings up this help embed")
helpembed.set_thumbnail(url="https://styles.redditmedia.com/t5_39br0/styles/communityIcon_q7wf9pe92v671.jpg")
helpembed.url = "https://discord.com/api/oauth2/authorize?client_id=951290000861986857&permissions=541166365760&scope=bot"
client.remove_command("help")


@client.event
async def on_ready():
    print('Bot is online')
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        auto_delete_data.start()
        print(f"Log file set up successfully")
    except Exception as e:
        print(e)

@client.command()
async def raid(ctx, msg: str = None):
    await ctx.send("This command has moved into slash command /d2")
    

@client.tree.command(name="d2", description="Starts an LFG post")
@app_commands.describe(activity = "Choose the activity to LFG for")
@app_commands.choices(activity = [
    discord.app_commands.Choice(name="Crota's End", value=1),
    discord.app_commands.Choice(name="Root of Nightmares", value=2),
    discord.app_commands.Choice(name="King's Fall", value=3),
    discord.app_commands.Choice(name="Vow of the Disciple", value=4),
    discord.app_commands.Choice(name="Vault of Glass", value=5),
    discord.app_commands.Choice(name="Deep Stone Crypt", value=6),
    discord.app_commands.Choice(name="Garden of Salvation", value=7),
    discord.app_commands.Choice(name="Last Wish", value=8),
    discord.app_commands.Choice(name="Master King's Fall", value=9),
    discord.app_commands.Choice(name="Master Vow of the Disciple", value=10),
    discord.app_commands.Choice(name="Master Vault of Glass", value=11)
])
async def d2(interaction: discord.Interaction, activity: discord.app_commands.Choice[int]):

    def is_bot(user):
        return user == client.user

    votd_image = "https://cdn1.dotesports.com/wp-content/uploads/2022/03/05085411/Vow-of-the-Disciple-Entrance-scaled.jpg"
    lw_image = "https://arcadehaven.io/wp-content/uploads/2021/08/all-wishes-on-the-wall-of-wishes-last-wish-raid.jpg"
    vog_image = "https://www.pcgamesn.com/wp-content/uploads/2021/04/destiny-2-vault-of-glass.jpg"
    gos_image = "https://assets.rockpapershotgun.com/images/2019/10/destiny-2-garden-of-salvation-f.jpg"
    dsc_image = "https://i.imgur.com/0U7Ao0q.jpg"
    kf_image = "https://assets.reedpopcdn.com/destiny-2-king's-fall.jpg/BROK/resize/1920x1920%3E/format/jpg/quality/80/destiny-2-king's-fall.jpg"
    rn_image = "https://pbs.twimg.com/media/Fp_5gnkX0AULoRF?format=jpg&name=large"
    ce_image = "https://images.contentstack.io/v3/assets/blte410e3b15535c144/blt8023dab456754205/64f0c82d8c8fe96dfe98bbf8/16x9Standard_1920x1080.jpg"

    image = None
    raid_name = None
    activity = activity.name
    if activity == "Vow of the Disciple":
        image = votd_image
        raid_name = "Raid - Vow of The Disciple"
    elif activity == "Master Vow of the Disciple":
        image = votd_image
        raid_name = "Raid - Master Vow of the Disciple"
    elif activity == "Master Vault of Glass":
        image = vog_image
        raid_name = "Raid - Master Vault of Glass"
    elif activity == "Last Wish":
        image = lw_image
        raid_name = "Raid - Last Wish"
    elif activity == "Vault of Glass":
        image = vog_image
        raid_name = "Raid - Vault of Glass"
    elif activity == "Garden of Salvation":
        image = gos_image
        raid_name = "Raid - Garden of Salvation"
    elif activity == "Deep Stone Crypt":
        image = dsc_image
        raid_name = "Raid - Deep Stone Crypt"
    elif activity == "King's Fall":
        image = kf_image
        raid_name = "Raid - King's Fall"
    elif activity == "Master King's Fall":
        image = kf_image
        raid_name = "Raid - Master King's Fall"
    elif activity == "Root of Nightmares":
        image = rn_image
        raid_name = "Raid - Root of Nightmares"
    elif activity == "Crota's End":
        image = ce_image
        raid_name = "Raid - Crota's End"
    else:
        await interaction.response.send_message(f"No such activity, /d2 help for information", ephemeral=True)
        return


    _MAXRAIDPLAYERS = 6
    _MAXTIME = 3600
    userList = []
    creator = interaction.user
    color_int = (await client.fetch_user(creator.id))._accent_colour
    ctx = interaction.channel
    unique_id = uuid.uuid4().hex[:8]

    class embedButtons(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=_MAXTIME)

        @discord.ui.button(label="Join", style=discord.ButtonStyle.green)
        async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
            try:
                user = interaction.user
                if user not in userList and not is_bot(user) and len(userList) < _MAXRAIDPLAYERS:
                    await interaction.response.defer()
                    userList.append(user)
                    embed.title = raid_name + f' [{len(userList)}/{_MAXRAIDPLAYERS}]'
                    embed.add_field(name=f'Player', value=f'🔹 {user.display_name} (@{user.name})', inline=False)
                    await sentEmbed.edit(embed = embed)
                    if len(userList) >= _MAXRAIDPLAYERS:
                        embed.title = raid_name + " [Full - Closed]"
                        await sentEmbed.edit(embed = embed, view = None)
                        self.stop()
                        for user in userList:
                            if not is_bot(user):
                                await user.send('Raid team is now full', embed = embed)
                        logging.info(f'{time.asctime( time.localtime(time.time()) )}       [{unique_id}]            {creator}           {raid_name}         Full')
                else:
                    await interaction.response.send_message(f"You have already joined", ephemeral=True)
            except discord.errors.NotFound:
                logging.info(f'{time.asctime( time.localtime(time.time()) )}       [{unique_id}]            {creator}           {raid_name}         Deleted')

        @discord.ui.button(label="Leave", style=discord.ButtonStyle.red)
        async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
            try:
                user = interaction.user
                if user in userList and not is_bot(user):
                    await interaction.response.defer()
                    embed.remove_field(userList.index(user))
                    userList.remove(user)
                    embed.title = raid_name + f' [{len(userList)}/{_MAXRAIDPLAYERS}]'
                    await sentEmbed.edit(embed = embed)
                elif not user in userList and not is_bot(user):
                    await interaction.response.send_message(f"You are not in the team", ephemeral=True)
            except discord.errors.NotFound:
                logging.info(f'{time.asctime( time.localtime(time.time()) )}       [{unique_id}]            {creator}           {raid_name}         Deleted')

        @discord.ui.button(label="Cancel", style=discord.ButtonStyle.blurple)
        async def cancel(self, interaction: discord.Interaction, button:discord.ui.Button):
            try:
                user = interaction.user
                if user == creator and not is_bot(user):
                    await interaction.response.defer()
                    await sentEmbed.delete()
                    self.stop()
                    logging.info(f'{time.asctime( time.localtime(time.time()) )}       [{unique_id}]            {creator}           {raid_name}         Deleted')
                elif not user == creator and not is_bot(user):
                    await interaction.response.send_message(f"You can't cancel someone else's post", ephemeral=True)
            except discord.errors.NotFound:
                logging.info(f'{time.asctime( time.localtime(time.time()) )}       [{unique_id}]            {creator}           {raid_name}         Deleted')


    view = embedButtons()
    userList.append(creator)
    embed = discord.Embed(title=raid_name + f' [{len(userList)}/{_MAXRAIDPLAYERS}]', description="♦︎ Click the corresponding buttons to join, leave, or cancel the raid \n♦︎ Post will expire in 1 hour \n♦︎ Want to use me in another server? [click here](https://discord.com/api/oauth2/authorize?client_id=951290000861986857&permissions=541166365760&scope=bot)", color=color_int)
    embed.set_author(name=creator.display_name, icon_url=creator.display_avatar)
    embed.set_image(url=image)
    embed.add_field(name=f'Player', value=f'🔹 {creator.display_name} (@{creator.name})', inline=False)
    try:
        await interaction.response.send_message("Creating post...", delete_after=1, ephemeral=True)
        sentEmbed = await ctx.send(embed = embed, view = view)
        logging.info(f'{time.asctime( time.localtime(time.time()) )}       [{unique_id}]            {creator}           {raid_name}         Created')
        await asyncio.sleep(_MAXTIME)
        try:
            embed.title = raid_name + " [Expired - Closed]"
            view.stop()
            await sentEmbed.edit(embed = embed, view = None)
            logging.info(f'{time.asctime( time.localtime(time.time()) )}       [{unique_id}]            {creator}           {raid_name}         Timed Out')
        except discord.errors.NotFound:
            logging.info(f'{time.asctime( time.localtime(time.time()) )}       [{unique_id}]            {creator}           {raid_name}         Deleted')
        except discord.errors.Forbidden:
            return
    except discord.errors.Forbidden:
        await creator.send("It looks like I don't have permission in the channel you invoked a command in, please make sure I have both sufficient permissions.")
        return


@client.command()
async def help(ctx):
    creator = ctx.message.author
    try:
        await ctx.send(embed=helpembed)
    except discord.errors.Forbidden:
        await creator.send("It looks like I don't have permission in the channel you invoked a command in, please make sure I have both sufficient permissions.")
        return

@client.event
async def on_guild_join(guild):
    logging.info(f'{time.asctime( time.localtime(time.time()) )}       Joined          {guild.name}          ({guild.id})')
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send(embed=helpembed)

@client.event
async def on_guild_remove(guild):
    logging.info(f'{time.asctime( time.localtime(time.time()) )}       Left          {guild.name}          ({guild.id})')

@tasks.loop(hours=720)
async def auto_delete_data():
    with open('log.txt', 'w'):
        pass
    logging.info(f'{time.asctime( time.localtime(time.time()) )}       =========================== New Log Session Has Started ===========================')

client.run(_Token)



