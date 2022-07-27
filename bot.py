import time
import os
import logging

from add_track import add_track


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

class Command(StatesGroup):
    name = State()
    wait = State()


@dp.message_handler(state=Command.name)
async def execute_command(message: types.Message, state: FSMContext):
    data = await state.get_data()
    command = data['name']

    if command == '/add_song':
        start = time.time()
        count_before = db.get_words_count()
        lenn = add_track(message.text.lower())
        count_after = db.get_words_count() - count_before
        await message.answer("Добавлено " + str(count_after) + " новых слов из " + str(lenn) + " возможных за " + str('%.3f' % (time.time() - start)) + " сек")

    if command == '/add_word':
        word = message.text.lower()
        db.add_word(word)
        await message.answer("Добавлено")

    if command == '/check_song':
        pass

    if command == '/check_word':
        word = message.text.lower()
        await message.answer(str(db.check_word(word)))


    await state.finish()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nЯ помогаю следить за словарным запасом\n/сommands для списка всех комманд :)")

@dp.message_handler(commands=['commands'])
async def send_commands(message: types.Message):
    await message.reply("""/add_song - Добавить песню целиком\n/add_word - Добавить слово\n/check_song - Добавить песню проверяя каждое слово\n/check_word - Проверить, если ли слово\n/count - Количество слов в базе\n/commands - Команды""")


@dp.message_handler(commands=['add_song'])
async def add_song(message: types.Message, state: FSMContext):
    await message.answer("Введите ссылку на genius:")
    await Command.name.set()
    await state.update_data(name=message.text)

@dp.message_handler(commands=['add_word'])
async def add_word(message: types.Message, state: FSMContext):
    await message.answer("Введите слово:")
    await Command.name.set()
    await state.update_data(name=message.text)

@dp.message_handler(commands=['check_song'])
async def check_song(message: types.Message, state: FSMContext):
    await message.answer("Введите ссылку на genius:")
    await Command.name.set()
    await state.update_data(name=message.text)

@dp.message_handler(commands=['check_word'])
async def check_wordd(message: types.Message, state: FSMContext):
    await message.answer("Введите слово:")
    await Command.name.set()
    await state.update_data(name=message.text)

@dp.message_handler(commands=['count'])
async def count(message: types.Message, state: FSMContext):
    await message.answer("В базе " + str(db.get_words_count()) + " слов.")


   

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)