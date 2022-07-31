import time
import os
import logging

from keyboards import menu_kb

from add_track import add_track
from LyricsParser import LyricsParser


from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

from aiogram import Bot, Dispatcher, executor, types
import db

API_TOKEN = str(os.environ.get('BOT_TOKEN'))


logging.basicConfig(#filename="sample.log",
                    level=logging.INFO,
                    #filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

class State(StatesGroup):
    add_t = State()
    add_w = State()
    check_t = State()
    check_w = State()

    command = State()
    check = State()


@dp.message_handler(state=State.command)
async def execute_command(message: types.Message, state: FSMContext):
    data = await state.get_data()
    command = data['name']

    if command == '/add_song':
        start = time.time()
        count_before = db.get_words_count()
        lenn = add_track(message.text.lower())
        count_after = db.get_words_count() - count_before
        await message.answer("Добавлено " + str(count_after) + " новых слов из " + str(lenn) + " возможных за " + str('%.3f' % (time.time() - start)) + " сек", reply_markup=menu_kb)
        await state.finish()

   

    if command == '/check_song':
        url = message.text.lower()
        words = LyricsParser(url).get_word_list()
        await State.check.set()
        await state.update_data(words)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nЯ помогаю следить за словарным запасом\n/help для списка всех комманд :)", reply_markup=menu_kb)


@dp.message_handler(regexp='Команды')
@dp.message_handler(commands=['commands','help'])
async def send_commands(message: types.Message):
    await message.reply("""/add_song - Добавить песню целиком\n/add_word - Добавить слово\n/check_song - Добавить песню проверяя каждое слово\n/check_word - Проверить, если ли слово\n/count - Количество слов в базе\n/commands - Команды""", reply_markup=menu_kb)








@dp.message_handler(regexp='Добавить трек')
@dp.message_handler(commands=['add_song'])
async def add_song(message: types.Message):
    await message.answer("Введите сcылку на Genius:")
    await State.add_t.set()

@dp.message_handler(state=State.add_t)
async def add_track(message: types.Message, state: FSMContext):
    url = message.text.lower()
    words = LyricsParser(url).get_word_list()
    await message.answer("Всего в треке " + str(len(words)) + " слов.")
    new_words = ''
    new_count = 0
    for word in words:
        if not db.check_word(word):
            new_count += 1
            new_words += word + '\n'
            db.add_word(word)
    await message.answer("Добавлено " + str(new_count) + " слов.\nВот они:")
    await message.answer(new_words, reply_markup=menu_kb)
    await state.finish()








@dp.message_handler(regexp='Добавить слово')
@dp.message_handler(commands=['add_word'])
async def add_word(message: types.Message):
    await message.answer("Введите слово:")
    await State.add_w.set()
    
@dp.message_handler(state=State.add_w)
async def execute_command(message: types.Message, state: FSMContext):
    word = message.text.lower()
    if db.check_word(word):
        await message.answer("Это слово уже было", reply_markup=menu_kb)
    else:
        db.add_word(word)
        await message.answer("Добавлено", reply_markup=menu_kb)
    await state.finish()

    
@dp.message_handler(regexp='Есть ли слово')
@dp.message_handler(commands=['check_word'])
async def check_wordd(message: types.Message):
    await message.answer("Введите слово:")
    await State.check_w.set()

@dp.message_handler(state=State.check_w)
async def execute_command(message: types.Message, state: FSMContext):
    word = message.text.lower()
    if db.check_word(word):
        await message.answer("Есть", reply_markup=menu_kb)
    else:
        await message.answer("Нет", reply_markup=menu_kb)
    await state.finish()


@dp.message_handler(regexp='Проверить трек')
@dp.message_handler(commands=['check_song'])
async def check_song(message: types.Message, state: FSMContext):
    await message.answer("Введите ссылку на genius:")
    await State.command.set()
    await state.update_data(name=message.text)


@dp.message_handler(regexp='Количество слов')
@dp.message_handler(commands=['count'])
async def count(message: types.Message, state: FSMContext):
    await message.answer("В базе " + str(db.get_words_count()) + " слов.", reply_markup=menu_kb)

if __name__ == '__main__':
    print("Starting")
    executor.start_polling(dp, skip_updates=True)
    