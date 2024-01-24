import logging
import asyncio
from discord.ext import commands, tasks


logging.basicConfig(filename='log.txt', encoding='utf-8', level=logging.DEBUG)
logging.info("Test")

@tasks.loop(seconds=20)
async def auto_delete_data():
    with open('log.txt', 'w'):
        print("Deleted Data")

auto_delete_data.start()

        

