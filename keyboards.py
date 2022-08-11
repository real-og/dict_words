from secrets import choice
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

commands = KeyboardButton('Команды')
add_t = KeyboardButton('Добавить трек')
add_w = KeyboardButton('Добавить слово')
check_w = KeyboardButton('Проверить слово')
check_t = KeyboardButton('Проверить трек')
count = KeyboardButton('Количество слов')
list = KeyboardButton('Список')
delete_w = KeyboardButton('Удалить слово')

menu_kb.insert(commands)
menu_kb.insert(add_t)
menu_kb.insert(check_t)
menu_kb.insert(count)
menu_kb.insert(add_w)
menu_kb.insert(check_w)
menu_kb.insert(list)
menu_kb.insert(delete_w)


choice_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

yes = KeyboardButton('Да')
no = KeyboardButton('Нет')
context = KeyboardButton('Контекст')
finish =KeyboardButton('Закончить')

choice_kb.insert(yes)
choice_kb.insert(no)
choice_kb.insert(finish)
choice_kb.insert(context)


big_start_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

start = KeyboardButton('Начать')

big_start_kb.insert(start)
