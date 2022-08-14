import os
import logging

from keyboards import *

from LyricsParser import LyricsParser

import converter
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

from aiogram import Bot, Dispatcher, executor, types
import db

import initializer

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
    delete_w = State()
    choose_lvl = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("""*Привет!*\nЯ помогаю следить за словарным запасом\n
Для начала давай определим начальный набор слов, который добавим тебе в словарь! Выбирай свой примерный уровень:\n
Начальный - А1, A2
Средний - B1, B2
Продвинутый - С1\n
_вводи_ /help _для списка всех команд_""", reply_markup=choose_lvl_kb, parse_mode='Markdown')
    db.add_user(id_tg=message.from_user.id, username=message.from_user.username)
    await State.choose_lvl.set()

@dp.message_handler(state=State.choose_lvl)
async def add_track(message: types.Message, state: FSMContext):
    sum = 0
    if message.text.lower() in ('a1', 'a2', 'b1', 'b2', 'c1'):
        sum = initializer.init_user(id_tg=message.from_user.id, filename=message.text.lower() + '.txt')
        await message.answer('В словарь добавлено *' + str(sum) + '* слов.\nВы в меню.',
                            parse_mode='Markdown',
                            reply_markup=menu_kb)
        await state.finish()
    elif message.text.lower() == 'меню':
        await message.answer('Вы в меню!\nИспользуй кнопки\n/help - помощь', reply_markup=menu_kb)
        await state.finish()
    else: 
        await message.answer('Такого варианта нет. Нажмите меню, чтобы пропустить инициализацию или выберите свой уровень.',
                            reply_markup=choose_lvl_kb)
    

@dp.message_handler(regexp='Команды')
@dp.message_handler(commands=['commands','help'])
async def send_commands(message: types.Message):
    greeting = """/commands - Команды
/add_song - Добавить песню целиком
/add_word - Добавить слово
/check_song - Добавить песню проверяя каждое слово
/check_word - Проверить, если ли слово
/count - Количество слов в базе
/list - Получить .html файл со всеми изученными словами
/delete_word - Удалить слово"""
    await message.reply(greeting, reply_markup=menu_kb)


@dp.message_handler(regexp='Добавить трек')
@dp.message_handler(commands=['add_track'])
async def add_song(message: types.Message):
    await message.answer("Введите исполнителя и название трека через пробел без знаков препинания и апострофов '.\nЕсли это совместка, только основного исполнителя.\nЕсли возникли проблемы, введите сcылку на трек на Genius.com:")
    await State.add_t.set()

@dp.message_handler(state=State.add_t)
async def add_track(message: types.Message, state: FSMContext):
    url = converter.create_url(message.text.lower().replace('$', ' '))
    words = LyricsParser(url).get_word_list()
    if not len(words):
        await message.answer("Не смог найти трек ((\nПроверь данные...", reply_markup=menu_kb)
        await state.finish()
        return
    await message.answer("Всего в треке найдено " + str(len(words)) + " слов.\nИдёт добавление, ждём...")
    new_words = ''
    new_count = 0
    for word in words:
        if not db.check_word_by_user(id_tg=message.from_user.id, word=word):
            new_count += 1
            new_words += word + '\n'
            db.add_word_to_user(word=word, id_tg=message.from_user.id)
    if new_count:
        await message.answer("Добавлено *" + str(new_count) + "* новых слов.", parse_mode='Markdown')
        await message.answer('Вот они:\n' + new_words, reply_markup=menu_kb)
    else:
        await message.answer('Все слова знакомы', reply_markup=menu_kb)
    await state.finish()


@dp.message_handler(regexp='Удалить слово')
@dp.message_handler(commands=['delete_word'])
async def add_word(message: types.Message):
    await message.answer("Введите слово:")
    await State.delete_w.set()
    
@dp.message_handler(state=State.delete_w)
async def execute_command(message: types.Message, state: FSMContext):
    word = message.text.lower()
    if db.check_word_by_user(word=word, id_tg=message.from_user.id):
        db.delete_word_by_user(word=word, id_tg=message.from_user.id)
        await message.answer("Удалено", reply_markup=menu_kb)
    else:
        await message.answer("Такого слова не было", reply_markup=menu_kb)
    await state.finish()


@dp.message_handler(regexp='Добавить слово')
@dp.message_handler(commands=['add_word'])
async def add_word(message: types.Message):
    await message.answer("Введите слово:")
    await State.add_w.set()
    
@dp.message_handler(state=State.add_w)
async def execute_command(message: types.Message, state: FSMContext):
    word = message.text.lower()
    if db.check_word_by_user(word=word, id_tg=message.from_user.id):
        await message.answer("Это слово уже было", reply_markup=menu_kb)
    else:
        db.add_word_to_user(word=word, id_tg=message.from_user.id)
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
    if db.check_word_by_user(word=word, id_tg=message.from_user.id):
        await message.answer("Есть", reply_markup=menu_kb)
    else:
        await message.answer("Нет", reply_markup=menu_kb)
    await state.finish()


@dp.message_handler(regexp='Проверить трек')
@dp.message_handler(commands=['check_song'])
async def add_song(message: types.Message):
    await message.answer("Введите исполнителя затем название трека, разделяя все слова пробелом без знаков препинания и апострофов '.\nЛибо введите ссылку на трек на Genius.com")
    await State.check_t.set()

@dp.message_handler(state=State.check_t)
async def check_track(message: types.Message, state: FSMContext):
    await message.answer("Чуть-чуть подождите...")
    url = converter.create_url(message.text.lower().replace('$', ' '))
    words = LyricsParser(url).get_word_list()
    if not len(words):
        await message.answer("Не смог найти трек ((\nПроверь данные...", reply_markup=menu_kb)
        await state.finish()
        return
    await message.answer("Всего в треке " + str(len(words)) + " слов.\n")
    new_words = list()
    for word in words:
        if not db.check_word_by_user(word=word, id_tg=message.from_user.id) and (word not in new_words):
            new_words.append(word)
    if len(new_words) == 0:
        await message.answer("В этом треке все слова знакомы", reply_markup=menu_kb)
        await state.finish()
        return
    await message.answer("Из них незнакомых *" + str(len(new_words)) + "*\nНажмите Начать, чтобы начать добавление по слову\nДа - знаю\nНет - не знаю.",
                         reply_markup=big_start_kb,
                         parse_mode='Markdown')
    await State.checking.set()
    await state.update_data(words_to_check=new_words)
    await state.update_data(iter=0)
    await state.update_data(words_to_learn=list())
    await state.update_data(all_words=words)

@dp.message_handler(state=State.checking)
async def check_(message: types.Message, state: FSMContext):
    data = await state.get_data()
    i = data['iter']
    new_words = data['words_to_check']
    to_learn_words = data['words_to_learn']

    if message.text.lower() == 'начать' or message.text.lower() == 'закончить'or message.text.lower() == 'контекст':
        pass
    elif message.text.lower() == 'да':
        db.add_word_to_user(word=new_words[i], id_tg=message.from_user.id)
        i += 1
    elif message.text.lower() == 'нет':
        to_learn_words.append(new_words[i])
        i += 1
    else:
        await message.answer('Такого варианта нет, вышли в меню.\nНезнакомые слова (если есть):\n' + '\n'.join(to_learn_words), reply_markup=menu_kb)
        await state.finish()
        return

    if i >= len(new_words) or message.text.lower() == 'закончить':
        if len(to_learn_words):
            await message.answer('Проверка окончена, слова которые нужно выучить:\n' + '\n'.join(to_learn_words), reply_markup=menu_kb)
        else:
            await message.answer('Молодчина! Всё было знакомо!', reply_markup=menu_kb)
        await state.finish()
        return
    elif message.text.lower() == 'контекст':
        all_words = data['all_words']
        begin_i = max(0, all_words.index(new_words[i]) - 4)
        end_i = min(len(all_words) - 1, all_words.index(new_words[i]) + 5)
        words_to_print = all_words[begin_i:end_i]
        words_to_print[words_to_print.index(new_words[i])] = '_ *' + new_words[i] + '* _'
        await message.answer('..._' + ' '.join(words_to_print) + '_...', reply_markup=choice_kb, parse_mode='Markdown')
    elif i < len(new_words):
        await message.answer(new_words[i], reply_markup=choice_kb)
    
    await state.update_data(words_to_learn=to_learn_words, iter=i)

@dp.message_handler(regexp='Список')
@dp.message_handler(commands=['list'])
async def get_words(message: types.Message):
    id_td = message.from_user.id
    await message.answer("Секунду ... находим всё, что вы выучили ...")
    f = open('words_' + str(id_td) + '.html', 'w')
    f.write('<br>'.join(db.get_words_by_user(id_td)))
    f.close()
    f = open('words_' + str(id_td) + '.html', 'rb')
    await message.answer_document(document=f, reply_markup=menu_kb)
    f.close()


@dp.message_handler(regexp='Количество слов')
@dp.message_handler(commands=['count'])
async def count(message: types.Message, state: FSMContext):
    await message.answer("В базе " + str(db.get_words_count_by_user(id_tg=message.from_user.id)) + " слов.", reply_markup=menu_kb)

@dp.message_handler()
async def default_handler(message: types.Message, state: FSMContext):
    await message.answer('oopppssy...\nЯ понимаю только команды /help', reply_markup=menu_kb)


if __name__ == '__main__':
    print("Starting")
    executor.start_polling(dp, skip_updates=True)
    