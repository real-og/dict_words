import time
import os
import logging

from add_track import add_track
from LyricsParser import LyricsParser

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

from aiogram import Bot, Dispatcher, executor, types
import db

API_TOKEN = str(os.environ.get('BOT_TOKEN'))


logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class State(StatesGroup):
    command = State()
    check = State()

button_1 = KeyboardButton('/commands')
button_2 = KeyboardButton('/add_track')
button_3 = KeyboardButton('/add_word')
button_4 = KeyboardButton('/check_word')
button_5 = KeyboardButton('/check_track')
button_6 = KeyboardButton('/count')

greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
greet_kb.insert(button_1)
greet_kb.insert(button_2)
greet_kb.insert(button_3)
greet_kb.insert(button_4)
greet_kb.insert(button_5)
greet_kb.insert(button_6)


@dp.message_handler(state=State.command)
async def execute_command(message: types.Message, state: FSMContext):
    data = await state.get_data()
    command = data['name']

    if command == '/add_song':
        start = time.time()
        count_before = db.get_words_count()
        lenn = add_track(message.text.lower())
        count_after = db.get_words_count() - count_before
        await message.answer("Добавлено " + str(count_after) + " новых слов из " + str(lenn) + " возможных за " + str('%.3f' % (time.time() - start)) + " сек", reply_markup=greet_kb)
        await state.finish()

    if command == '/add_word':
        word = message.text.lower()
        db.add_word(word)
        await message.answer("Добавлено", reply_markup=greet_kb)
        await state.finish()

    if command == '/check_song':
        url = message.text.lower()
        words = LyricsParser(url).get_word_list()
        await State.check.set()
        await state.update_data(words)

    if command == '/check_word':
        word = message.text.lower()
        await message.answer(str(db.check_word(word)), reply_markup=greet_kb)
        await state.finish()

@dp.message_handler(state=State.check)
async def ask_word(message: types.Message, state: FSMContext):
    pass

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nЯ помогаю следить за словарным запасом\n/сommands для списка всех комманд :)", reply_markup=greet_kb)

@dp.message_handler(commands=['commands'])
async def send_commands(message: types.Message):
    await message.reply("""/add_song - Добавить песню целиком\n/add_word - Добавить слово\n/check_song - Добавить песню проверяя каждое слово\n/check_word - Проверить, если ли слово\n/count - Количество слов в базе\n/commands - Команды""", reply_markup=greet_kb)


@dp.message_handler(commands=['add_song'])
async def add_song(message: types.Message, state: FSMContext):
    await message.answer("Введите ссылку на genius:")
    await State.command.set()
    await state.update_data(name=message.text)

@dp.message_handler(commands=['add_word'])
async def add_word(message: types.Message, state: FSMContext):
    await message.answer("Введите слово:")
    await State.command.set()
    await state.update_data(name=message.text)

@dp.message_handler(commands=['check_song'])
async def check_song(message: types.Message, state: FSMContext):
    await message.answer("Введите ссылку на genius:")
    await State.command.set()
    await state.update_data(name=message.text)

@dp.message_handler(commands=['check_word'])
async def check_wordd(message: types.Message, state: FSMContext):
    await message.answer("Введите слово:")
    await State.command.set()
    await state.update_data(name=message.text)

@dp.message_handler(commands=['count'])
async def count(message: types.Message, state: FSMContext):
    await message.answer("В базе " + str(db.get_words_count()) + " слов.", reply_markup=greet_kb)


   

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)