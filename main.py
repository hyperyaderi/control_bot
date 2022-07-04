from email import message
import os
import json
import shutil
import logging
import requests
from mutagen.mp3 import MP3
from dotenv import load_dotenv
from aiogram.utils import executor
from aiogram import Bot, types, filters
from aiogram.dispatcher import Dispatcher


load_dotenv('.env')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ.get('TG_TOKEN'))
dp = Dispatcher(bot)
musicfolder = '/home/icecast/music'
chatid = '-1001646996853'
whitelist = [1888296065, 1999113390, 1618915689, 834381991, 1279811417, 837236788]
admins = [1999113390, 1618915689]

def inline_removefile_keyboard(filename: str, userid: int):
	keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
	acceptbtn = types.InlineKeyboardButton('✅ Подтвердить', callback_data=f'acceptbtn|||{filename}|||{userid}')
	declinebtn = types.InlineKeyboardButton('❌ Отменить', callback_data=f'declinebtn|||{filename}|||{userid}')
	keyboard.add(acceptbtn)
	keyboard.add(declinebtn)
	return keyboard


@dp.message_handler(filters.Command('stopices'))
async def stopices(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        await message.answer('Ices стопнут, можете врываться с радиобосса')
        os.system('/home/icecast/stopices')

@dp.message_handler(filters.Command('startices'))
async def startices(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        await message.answer('Ices запущен, ведется поток плейлиста')
        os.system('/home/icecast/startices')

@dp.message_handler(filters.Command('updateplaylist'))
async def updateplaylist(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        await message.answer('Плейлист обновлён! Теперь нужно перезапустить Ices')
        os.system('/home/icecast/updateplaylist')

@dp.message_handler(filters.Command('restartices'))
async def restartices(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        await message.answer('Ices перезапущен!')
        os.system('/home/icecast/restartices')

@dp.message_handler(filters.Command('nowplaying'))
async def nowplaying(message: types.Message):
    url = 'https://radio.hyperyaderi.ru/status-json.xsl'
    resp = requests.get(url).text
    data = json.loads(resp)
    nowplaying = data['icestats']['source']['title']
    await message.answer(f'Сейчас играет: *{nowplaying}*', parse_mode='markdown')

@dp.message_handler(filters.Command('listeners'))
async def listeners(message: types.Message):
    url = 'https://radio.hyperyaderi.ru/status-json.xsl'
    resp = requests.get(url).text
    data = json.loads(resp)
    listeners = data['icestats']['source']['listeners']
    listener_peak = data['icestats']['source']['listener_peak']
    await message.answer(f'Сейчас радио слушают *{listeners}* чел.\nПик: *{listener_peak}* чел.', parse_mode='markdown')

@dp.message_handler(filters.Command('cleartags'))
async def cleartags(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        await message.reply('Начинаю процесс удаления тегов!')
        for root, dirs, files in os.walk(musicfolder):
            for file in files:
                if file.endswith('.mp3'):
                    f = os.path.join(root, file)
                    try:
                        mp3 = MP3(f)
                        mp3.delete()
                        mp3.save()
                    except:
                        print('no ID3 tag')
        await message.reply('Теги удалены!')

@dp.message_handler(filters.Command('deletetrack'))
async def deletetrack(message: types.Message):
    if message.from_user.id not in admins:
        await message.reply('Пошёл нахуй!')
    else:
        url = 'https://radio.hyperyaderi.ru/status-json.xsl'
        resp = requests.get(url).text
        data = json.loads(resp)
        userid = message.from_user.id
        nowplaying = data['icestats']['source']['title']
        inline_removefile_keyboard(nowplaying, userid)
        # await message.answer(f'{str(nowplaying)}, {int(userid)}')
        await message.answer(f'Вы действительно хотите удалить трек *{nowplaying}*?', reply_markup=inline_removefile_keyboard(str(nowplaying), int(userid)), parse_mode="markdown")

@dp.callback_query_handler(lambda c: c.data.startswith('accept'))
async def process_accept_button(callback_query: types.CallbackQuery):
    separator = '|||'
    data = callback_query.data.split(separator)
    zalupa = data[1]
    userid = int(data[2])
    username = callback_query.from_user.username
    if "_" in username:
        username = username.replace('_', '\_')
    if callback_query.from_user.id == userid:
        filename = f'{musicfolder}/{zalupa}.mp3'
        try:
            os.remove(filename)
        except FileNotFoundError:
            await bot.send_message(chatid, '🚫 Файл не найден')
        await bot.send_message(chatid, f'✅ Файл <code>{filename}</code>\n<b>был удалён</b>', parse_mode="html")
        await callback_query.message.delete_reply_markup()
        await callback_query.answer()
    elif int(callback_query.from_user.id) != userid:
        await bot.send_message(chatid, f'@{username}, 🚫 Эта кнопка не для тебя', parse_mode="markdown")
        return    

@dp.callback_query_handler(lambda c: c.data.startswith('decline'))
async def process_decline_button(callback_query: types.CallbackQuery):
    separator = '|||'
    data = callback_query.data.split(separator)
    userid = int(data[2])
    username = callback_query.from_user.username
    if "_" in username:
        username = username.replace('_', '\_')
    if int(callback_query.from_user.id) != userid:
        await bot.send_message(chatid, f'@{username}, 🚫 Эта кнопка не для тебя', parse_mode="markdown")
        return
    await callback_query.message.delete_reply_markup()
    await callback_query.answer()

if __name__ == '__main__':
    executor.start_polling(dp)
