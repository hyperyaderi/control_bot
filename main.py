import os
import logging
import requests
from dotenv import load_dotenv
from aiogram.utils import executor
from aiogram import Bot, types, filters
from aiogram.dispatcher import Dispatcher

load_dotenv('.env')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ.get('TG_TOKEN'))
dp = Dispatcher(bot)
whitelist = [1888296065, 1999113390, 1618915689, 834381991]

@dp.message_handler(filters.Text(equals=['/stopices']))
async def stopices(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        await message.answer('Ices стопнут, можете врываться с радиобосса')
        os.system('/home/icecast/stopices')

@dp.message_handler(filters.Text(equals=['/startices']))
async def startices(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        await message.answer('Ices запущен, ведется поток плейлиста')
        os.system('/home/icecast/startices')

@dp.message_handler(filters.Text(equals=['/updateplaylist']))
async def updateplaylist(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        await message.answer('Плейлист обновлён! Теперь нужно перезапустить Ices')
        os.system('/home/icecast/updateplaylist')

@dp.message_handler(filters.Text(equals=['/restartices']))
async def restartices(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        await message.answer('Ices перезапущен!')
        os.system('/home/icecast/restartices')        

@dp.message_handler(filters.Text(equals=['/nowplaying']))
async def nowplaying(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        url = 'https://radio.hyperyaderi.ru/info.xsl'
        resp = requests.get(url=url)
        data = resp.json()
        nowplaying = data[0]['title']
        await message.answer(nowplaying)

if __name__ == '__main__':
    executor.start_polling(dp)
