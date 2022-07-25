import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from db import *

API_TOKEN = str(os.environ.get('BOT_TOKEN'))


logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nЯ помогаю следить за словарным запасом\n/сommands для списка всех комманд :)")

@dp.message_handler(commands=['commands'])
async def send_commands(message: types.Message):
    await message.reply("""/add_song - Добавить песню целиком\n/add_word - Добавить слово\n/check_song - Добавить песню проверяя каждое слово\n/check_word - Проверить, если ли слово\n/count - Количество слов в базе\n/commands - Команды""")

@dp.message_handler(commands=['add_song'])
async def add_song(message: types.Message):
    await message.answer("Введите ссылку на genius:")

@dp.message_handler(commands=['add_word'])
async def add_word(message: types.Message):
    await message.answer("Введите слово:")

@dp.message_handler(commands=['check_song'])
async def check_song(message: types.Message):
    await message.answer("Введите ссылку на genius:")

@dp.message_handler(commands=['check_word'])
async def check_word(message: types.Message):
    await message.answer("Введите слово:")

@dp.message_handler(commands=['count'])
async def count(message: types.Message):
    await message.answer("В базе " + str(get_words_count()) + " слов.")

   

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)