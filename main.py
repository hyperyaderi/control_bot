import os
import logging
import aiogram

from dotenv import load_dotenv
from aiogram.utils import executor
from aiogram import Bot, types, filters
from aiogram.dispatcher import Dispatcher

load_dotenv('.env')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ.get('TG_TOKEN'))
dp = Dispatcher(bot)
whitelist = [1888296065, 1999113390, 1618915689, 834381991]

@dp.message_handler(filters.Command('/stopices'))
async def stopices(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        os.system('/home/icecast/stopices')
        await message.reply('Ices стопнут, можете врываться с радиобосса')

@dp.message_handler(filters.Command('/startices'))
async def startices(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        os.system('/home/icecast/startices')
        await message.reply('Ices запущен, ведется поток плейлиста')

if __name__ == '__main__':
    executor.start_polling(dp)
