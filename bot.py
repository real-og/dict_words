import os
import logging

from keyboards import menu_kb, choice_kb, big_start_kb

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
    checking = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nЯ помогаю следить за словарным запасом\n/help для списка всех комманд :)", reply_markup=menu_kb)


@dp.message_handler(regexp='Команды')
@dp.message_handler(commands=['commands','help'])
async def send_commands(message: types.Message):
    await message.reply("""/commands - Команды\n/add_song - Добавить песню целиком\n/add_word - Добавить слово\n/check_song - Добавить песню проверяя каждое слово\n/check_word - Проверить, если ли слово\n/count - Количество слов в базе""", reply_markup=menu_kb)


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
    await message.answer("Добавлено " + str(new_count) + " слов.")
    await message.answer('Вот они:\n' + new_words, reply_markup=menu_kb)
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

    
@dp.message_handler(regexp='Проверить слово')
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
async def add_song(message: types.Message):
    await message.answer("Введите сcылку на Genius:")
    await State.check_t.set()

@dp.message_handler(state=State.check_t)
async def check_track(message: types.Message, state: FSMContext):
    url = message.text.lower()
    words = LyricsParser(url).get_word_list()
    await message.answer("Всего в треке " + str(len(words)) + " слов.")
    new_words = list()
    for word in words:
        if not db.check_word(word) and (word not in new_words):
            new_words.append(word)
    if len(new_words) == 0:
        await message.answer("В этом треке все слова знакомы", reply_markup=menu_kb)
        await state.finish()
    await message.answer("Из них незнакомых " + str(len(new_words)) + "\nНажмите Начать, чтобы начать добавление по слову\nДа - знаю\nНет - не знаю.", reply_markup=big_start_kb)
    await state.update_data(words_to_check=new_words)
    await state.update_data(iter=0)
    await state.update_data(words_to_learn=list())
    await State.checking.set()

@dp.message_handler(state=State.checking)
async def check_(message: types.Message, state: FSMContext):
    data = await state.get_data()
    i = data['iter']
    new_words = data['words_to_check']
    to_learn_words = data['words_to_learn']
    
    if message.text.lower() == 'начать':
        pass
    elif message.text.lower() == 'да':
        db.add_word(new_words[i-1])
    elif message.text.lower() == 'нет':
        to_learn_words.append(new_words[i-1])
    else:
        await message.answer('Такого варианта нет, вышли в меню', reply_markup=menu_kb)
        await state.finish()
        return

    if i < len(new_words):
        await message.answer(new_words[i], reply_markup=choice_kb)
        i += 1
    else:
        await message.answer('Проверка окончена, слова которые нужно выучить:\n' + str(to_learn_words), reply_markup=menu_kb)
        await state.finish()
        return
    await state.update_data(words_to_learn=to_learn_words, iter=i)



    
    
    












@dp.message_handler(regexp='Количество слов')
@dp.message_handler(commands=['count'])
async def count(message: types.Message, state: FSMContext):
    await message.answer("В базе " + str(db.get_words_count()) + " слов.", reply_markup=menu_kb)


if __name__ == '__main__':
    print("Starting")
    executor.start_polling(dp, skip_updates=True)
    