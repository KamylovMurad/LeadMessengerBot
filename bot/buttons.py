from aiogram import types


async def button_aggree(text, call):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    agree_button = types.InlineKeyboardButton(text=text, callback_data=call)
    keyboard.add(agree_button)
    return keyboard


async def get_filters():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton('Астрологи', callback_data='Астролог')
    button2 = types.InlineKeyboardButton('Психологи', callback_data='Психолог')
    button3 = types.InlineKeyboardButton('Стилисты', callback_data='Стилист')
    button4 = types.InlineKeyboardButton('Юристы', callback_data='Юрист')
    button5 = types.InlineKeyboardButton(
        'Нутрициологи',
        callback_data='Нутрициолог'
    )
    button12 = types.InlineKeyboardButton(
        'Косметологи',
        callback_data='Косметолог'
    )
    button6 = types.InlineKeyboardButton('Врачи', callback_data='Врач')
    button7 = types.InlineKeyboardButton('Тренеры', callback_data='Тренер')
    button8 = types.InlineKeyboardButton('Дизайнеры', callback_data='Дизайнер')
    button9 = types.InlineKeyboardButton(
        'Финансисты',
        callback_data='Финансист'
    )
    button11 = types.InlineKeyboardButton(
        'Маркетологи',
        callback_data='Маркетолог'
    )
    keyboard.add(
        button1, button2, button3,
        button4, button5, button6,
        button7, button8, button9,
        button11, button12
        )
    return keyboard


async def get_nums():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton('1', callback_data='1')
    button2 = types.InlineKeyboardButton('2', callback_data='2')
    button3 = types.InlineKeyboardButton('3', callback_data='3')
    button4 = types.InlineKeyboardButton('4', callback_data='4')
    button5 = types.InlineKeyboardButton('5', callback_data='5')
    button6 = types.InlineKeyboardButton('6', callback_data='6')
    button7 = types.InlineKeyboardButton(
        'Все категории',
        callback_data='all_categories'
    )
    keyboard.add(button1, button2, button3, button4, button5, button6, button7)
    return keyboard


async def user_info_change():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton('Изменить имя', callback_data='name')
    button2 = types.InlineKeyboardButton(
        'Изменить фамилию',
        callback_data='surname'
    )
    button3 = types.InlineKeyboardButton(
        'Изменить номер телефона',
        callback_data='telephone_number'
    )
    button4 = types.InlineKeyboardButton(
        'Изменить категории для рассылки',
        callback_data='theme_distribute'
    )
    button5 = types.InlineKeyboardButton('Отмена', callback_data='cancel')
    keyboard.add(button1, button2, button3, button4, button5)
    return keyboard
