import os
import json
import logging
import hashlib
import requests

from mutagen.mp3 import MP3
from dotenv import load_dotenv
from aiogram import Bot, filters
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardMarkup, Message, CallbackQuery, InlineKeyboardButton


load_dotenv('.env')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ.get('TG_TOKEN'))
dp = Dispatcher(bot)
musicfolder = '/home/icecast/music'
chatid = '-1001646996853'
logsid = '-629518744'
whitelist = [1888296065, 1999113390, 1618915689, 834381991, 1279811417, 837236788]
admins = [1888296065, 1999113390, 1618915689]

@dp.message_handler(filters.Command('stopices'))
async def stopices(message: Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        username = message.from_user.username
        if "_" in username:
            username = username.replace('_', '\_')
        await message.answer('Ices стопнут, можете врываться с радиобосса')
        os.system('/home/icecast/stopices')
        await bot.send_message(logsid, f'#stopices\nuser: @{username}', parse_mode='markdown')

@dp.message_handler(filters.Command('startices'))
async def startices(message: Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        username = message.from_user.username
        if "_" in username:
            username = username.replace('_', '\_')
        await message.answer('Ices запущен, ведется поток плейлиста')
        os.system('/home/icecast/startices')
        await bot.send_message(logsid, f'#startices\nuser: @{username}', parse_mode='markdown')

@dp.message_handler(filters.Command('updateplaylist'))
async def updateplaylist(message: Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        username = message.from_user.username
        if "_" in username:
            username = username.replace('_', '\_')
        await message.answer('Плейлист обновлён! Теперь нужно перезапустить Ices')
        os.system('/home/icecast/updateplaylist')
        await bot.send_message(logsid, f'#updateplaylist\nuser: @{username}', parse_mode='markdown')

@dp.message_handler(filters.Command('restartices'))
async def restartices(message: Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        username = message.from_user.username
        if "_" in username:
            username = username.replace('_', '\_')
        await message.answer('Ices перезапущен!')
        os.system('/home/icecast/restartices')
        await bot.send_message(logsid, f'#restartices\nuser: @{username}', parse_mode='markdown')

@dp.message_handler(filters.Command('nowplaying'))
async def nowplaying(message: Message):
    url = 'https://radio.hyperyaderi.ru/status-json.xsl'
    resp = requests.get(url).text
    data = json.loads(resp)
    nowplaying = data['icestats']['source']['title']
    await message.answer(f'Сейчас играет: *{nowplaying}*', parse_mode='markdown')

@dp.message_handler(filters.Command('listeners'))
async def listeners(message: Message):
    url = 'https://radio.hyperyaderi.ru/status-json.xsl'
    resp = requests.get(url).text
    data = json.loads(resp)
    listeners = data['icestats']['source']['listeners']
    listener_peak = data['icestats']['source']['listener_peak']
    await message.answer(f'Сейчас радио слушают *{listeners}* чел.\nПик: *{listener_peak}* чел.', parse_mode='markdown')

@dp.message_handler(filters.Command('cleartags'))
async def cleartags(message: Message):
    if message.from_user.id not in whitelist:
        await message.reply('Пошёл нахуй!')
    else:
        username = message.from_user.username
        if "_" in username:
            username = username.replace('_', '\_')
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
        await bot.send_message(logsid, f'#cleartags\nuser: @{username}', parse_mode='markdown')

@dp.message_handler(filters.Command('deletetrack'))
async def deletetrack(message: Message):
    arguments = message.get_args()
    if message.from_user.id not in admins:
        await message.reply('Пошёл нахуй!')
    else:
        if arguments:
            await process_deletetrack(arguments, message)
            return
        else:    
            arguments = message.get_args()  
            url = 'https://radio.hyperyaderi.ru/status-json.xsl'
            resp = requests.get(url).text
            data = json.loads(resp)
            nowplaying = data['icestats']['source']['title']
            await message.answer(f'Вы действительно хотите удалить трек *{nowplaying}*?\nПодтвердите действие командой\n`/deletetrack {nowplaying}`', parse_mode="markdown")

async def process_deletetrack(zalupa, message):
    username = message.from_user.username
    if "_" in username:
        username = username.replace('_', '\_')
    filename = f'{musicfolder}/{zalupa}.mp3'
    caption = f'#deletetrack\nuser: @{username}\n{filename}'
    with open(filename, "rb") as file:
        await bot.send_audio(logsid, file, caption=caption, parse_mode='markdown')
        file.close()
    try:
        os.remove(filename)
    except FileNotFoundError:
        await bot.send_message(chatid, '🚫 Файл не найден')
    await bot.send_message(chatid, f'✅ Файл <code>{filename}</code>\n<b>был удалён</b>', parse_mode="html")

@dp.inline_handler()
async def inline_nowplaying(inline_query: InlineQuery):
    url = 'https://radio.hyperyaderi.ru/status-json.xsl'
    resp = requests.get(url).text
    data = json.loads(resp)
    text = inline_query.query or 'np'
    match text:
        case 'np':
            input_content = InputTextMessageContent(text)
            result_id: str = hashlib.md5(text.encode()).hexdigest()
            nowplaying = data['icestats']['source']['title']
            item = InlineQueryResultArticle(
                                        id=result_id,
                                        title=f'Отправить трек играющий сейчас на радио',
                                        input_message_content=InputTextMessageContent(
                                            message_text=f'Сейчас играет: *{nowplaying}*',
                                            parse_mode='markdown'
                                        )
                                    )
        case 'ls':
            input_content = InputTextMessageContent(text)
            result_id: str = hashlib.md5(text.encode()).hexdigest()
            listeners = data['icestats']['source']['listeners']
            listener_peak = data['icestats']['source']['listener_peak']
            item = InlineQueryResultArticle(
                                        id=result_id,
                                        title=f'Количество слушателей',
                                        input_message_content=InputTextMessageContent(
                                            message_text=f'Радио слушают *{listeners}* чел.',
                                            parse_mode='markdown'
                                        )
                                    )
        case _:
            input_content = InputTextMessageContent(text)
            result_id: str = hashlib.md5(text.encode()).hexdigest()
            item = InlineQueryResultArticle(
                                        id=result_id,
                                        title=f'Неизвестная команда\nНажмите для того чтобы увидеть список команд',
                                        input_message_content=InputTextMessageContent(
                                            message_text=f'Список команд:\n*np* - текущий трек на радио\n*ls* - узнать кол-во слушателей',
                                            parse_mode='markdown'
                                        )
                                    )
    await bot.answer_inline_query(inline_query.id, item, cache_time=1)

if __name__ == '__main__':
    executor.start_polling(dp)
