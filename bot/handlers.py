import asyncio
import random
from bot.distribute_logic import send_message_async, \
    send_message_admin, delete_button, bot_send_message
from aiogram.utils.exceptions import InvalidQueryID
from asyncpg.exceptions import InvalidTextRepresentationError, \
    NumericValueOutOfRangeError
from bot.crm_file import create_lead
from aiogram import types
from aiogram.dispatcher import FSMContext
from config_pr import db, bot, admin_list, greetings, information
from statesform import UserStates, AdminStates
from bot.buttons import button_aggree, get_filters, get_nums, user_info_change
from bot.decorators import rate_limited


async def process_start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await UserStates.policy_confirmation.set()
    user = await db.get_user_id(user_id)
    if user is None:
        with open('../pics/Group.jpg', 'rb') as photo:
            await bot.send_photo(user_id, photo=photo, caption=greetings)
        await process_policy_command(message)
    else:
        await state.finish()


async def process_policy_command(message: types.Message):
    keyboard = await button_aggree(text="Согласен", call="policy_agree")
    await message.answer(information, reply_markup=keyboard)


async def process_policy_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == "policy_agree":
        await delete_button(callback_query)
        await db.set_user_id(user_id)
        await bot.answer_callback_query(
          callback_query.id,
          text="Вы согласились с пользовательским соглашением.",
          cache_time=3
        )
        keyboard = await button_aggree(text="Ввести данные", call="form")
        await UserStates.get_form.set()
        await bot_send_message(
            user_id,
            'Для продолжения укажите Ваши данные.',
            reply_markup=keyboard
        )


async def form_start(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_button(callback_query)
    await UserStates.name.set()
    await bot_send_message(callback_query.message.chat.id, 'Введите Ваше имя')


async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await UserStates.last_name.set()
    await message.answer('Введите Вашу фамилию')


async def get_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await UserStates.telephone.set()
    await message.answer('Введите Ваш номер телефона')


async def get_telephone_number(message: types.Message, state: FSMContext):
    context_data = await state.get_data()
    await state.finish()
    name, last_name, tel, user_id = context_data.get('name'), \
        context_data.get('last_name'), \
        message.text, \
        message.from_user.id
    await db.set_user_info(user_id, name, last_name, tel)
    keyboard = await get_nums()
    await UserStates.vacancy.set()
    await message.answer(
        'Сколько категорий Вас интересует? '
        'Можно выбрать от 1 до 6 или все категории.'
        '\nАстрологи\nПсихологи\nСтилисты\nЮристы'
        '\nНутрициологи\nКосметологи\nВрачи\n'
        'Тренеры\nДизайнеры\nФинансисты\nМаркетологи',
        reply_markup=keyboard
    )


async def all_categories(call: types.CallbackQuery, state: FSMContext):
    await delete_button(call)
    await state.finish()
    user_id = call.from_user.id
    await db.update_sub_true(user_id)
    await bot_send_message(user_id,
                           f'Вы подписались на рассылку по всем категориям.\n'
                           f'Для изменения личных данных'
                           f'или для смены рассылки, введите /settings.'
                           )


async def categories_num(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_button(callback_query)
    await state.update_data(nums=callback_query.data)
    await state.update_data(category=set())
    keyboard = await get_filters()
    await UserStates.categories.set()
    await bot_send_message(
        callback_query.from_user.id,
        'Выберите интересующие категории',
        reply_markup=keyboard
    )


async def choose_categories(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    try:
        text = callback_query.data
        data = await state.get_data()
        category_list = data.get('category')
        category_list.add(text)
        nums = int(data.get('nums'))
        nums -= 1
        await bot_send_message(
            user_id,
            f'Выбрана категория {text}, выберите еще {nums}'
        )
        if nums == 0:
            await state.finish()
            await delete_button(callback_query)
            await db.set_categories(category_list, user_id)
            await bot_send_message(
                user_id,
                f'Вы подписались на рассылку '
                f'по выбранным категориям.\n'
                f'Для изменения личных данных '
                f'или для смены рассылки, введите /settings.'
                )
            return
        await state.update_data(nums=nums)
        await state.update_data(category=category_list)
    except Exception:
        await state.finish()
        await bot_send_message(
            user_id,
            'Возникла ошибка, выбрано некорректное значение\n'
            'Для изменения личных данных '
            'или для смены рассылки, введите /settings.'
        )


async def distribute(message: types.Message, state: FSMContext):
    await model(message, 'Введите текст для рассылки', AdminStates.distribute)


async def get_category(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    keyboard_choosen = await get_filters()
    button_all = types.InlineKeyboardButton(
        'Общая рассылка',
        callback_data='Общая'
    )
    button_cancel = types.InlineKeyboardButton(
        'Отмена',
        callback_data='Отмена'
    )
    keyboard_choosen.add(button_all, button_cancel)
    await message.answer(
        'Выберите категорию по которой хотите сделать рассылку',
        reply_markup=keyboard_choosen
    )


async def choose_category_admin(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_button(callback_query)
    text = await state.get_data('text')
    await state.finish()
    user_id = callback_query.from_user.id
    error = 0
    count: int = 0
    type: str = callback_query.data
    if type == 'Общая':
        text = f'Общая рассылка\n{text.get("text")}'
        users_list = await db.get_users_list_to_distribute_for_all()
        if users_list:
            keyboard = await button_aggree(
                text='Откликнуться',
                call='response_app'
            )
            try:
                for user in users_list:
                    if await send_message_async(user, text, keyboard):
                        error += 1
                    else:
                        count += 1
                    await asyncio.sleep(0.1)
            finally:
                for admin in admin_list:
                    await bot_send_message(
                        admin,
                        f'Рассылка по категории {type} закончена\n'
                        f'Количество людей получивших рассылку: {count}\n'
                        f'Возникшие ошибки: {error}'
                        )
                    await asyncio.sleep(1)
        else:
            await bot_send_message(
                user_id,
                'Пользователи для общей рассылки не найдены'
            )
    elif type != 'Отмена' and type != 'Общая':
        text = f'{type}\n{text.get("text")}'
        users_list = await db.get_users_list_to_distribute_by_category(
            category=type
        )
        if users_list:
            keyboard = await button_aggree(
                text='Откликнуться',
                call='response_app'
            )
            try:
                for user in users_list:
                    if await send_message_async(user, text, keyboard):
                        error += 1
                    else:
                        count += 1
                    await asyncio.sleep(0.1)
            finally:
                for admin in admin_list:
                    await bot_send_message(
                        admin,
                        f'Рассылка по категории {type} закончена\n'
                        f'Количество людей получивших рассылку: {count}\n'
                        f'Возникшие ошибки: {error}'
                        )
                    await asyncio.sleep(1)
        else:
            await bot_send_message(
                user_id,
                'Пользователи с данной категорией не найдены'
            )


@rate_limited(27, 60)
async def response(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_button(callback_query)
    user_id = callback_query.from_user.id
    answer = await db.user_info_response(user_id)
    if answer[3] is not True:
        try:
            await callback_query.answer('Вы откликнулись на рассылку.')
        except InvalidQueryID:
            pass
        name, surname, telephone_number = answer[0], answer[1], answer[2]
        text = callback_query.message.text
        category, text = text.split('\n')[0], text.split('\n')[1:]
        text = '\n'.join(text)
        if callback_query.from_user.username is not None:
            url = f'https://t.me/{callback_query.from_user.username}'
        else:
            url = f'<a href="tg://user?id={user_id}"' \
                  f'>Ссылка на чат с пользователем</a>'
        await create_lead(
            name, surname, user_id,
            text, telephone_number, category
        )
        user_info = f'Откликнулся(ась): {name} {surname}' \
                    f'\nНомер телефона: {telephone_number}' \
                    f'\n{url}' \
                    f'\n\nТекст рассылки: {text}'
        for admin in admin_list:
            await send_message_admin(admin, user_info)
            await asyncio.sleep(random.choice([1, 2, 3]))
    else:
        await bot_send_message(
            user_id,
            'Вы были заблокированы.'
            '\nСвяжитесь с администратором для разблокировки'
        )


async def change_info(message: types.Message, state: FSMContext):
    await UserStates.choose_change.set()
    keyboard = await user_info_change()
    await message.answer(
        text='Выберите кнопку, соответствующую вашему запросу.',
        reply_markup=keyboard
    )


async def answer_to_name(call: types.CallbackQuery, state: FSMContext):
    await delete_button(call)
    user_id = call.from_user.id
    await UserStates.change_name.set()
    await bot_send_message(user_id, 'Введите Ваше имя.')


async def change_name(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    name = message.text
    await db.update_name(user_id, name)
    await message.answer('Имя изменено.')


async def answer_to_surname(call: types.CallbackQuery, state: FSMContext):
    await delete_button(call)
    await UserStates.change_surname.set()
    user_id = call.from_user.id
    await bot_send_message(user_id, 'Введите Вашу фамилию.')


async def change_surname(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    surname = message.text
    await db.update_surname(user_id, surname)
    await message.answer('Фамилия изменена.')


async def answer_to_telephone_number(call: types.CallbackQuery, state: FSMContext):
    await delete_button(call)
    await UserStates.change_telephone.set()
    user_id = call.from_user.id
    await bot_send_message(user_id, 'Введите Ваш номер телефона.')


async def change_telephone_number(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    number = message.text
    await db.update_tel_number(user_id, number)
    await message.answer('Номер телефона изменён.')


async def cancel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await delete_button(call)


async def category_count(call: types.CallbackQuery, state: FSMContext):
    await delete_button(call)
    user_id = call.from_user.id
    await db.update_sub_false(user_id)
    keyboard = await get_nums()
    await UserStates.vacancy.set()
    await bot_send_message(
        user_id,
        text='Сколько категорий Вас интересует? '
             'Можно выбрать от 1 до 6 или все категории.'
             '\nАстрологи\nПсихологи\nСтилисты'
             '\nЮристы\nНутрициологи\nКосметологи'
             '\nВрачи\nТренеры\nДизайнеры\nФинансисты'
             '\nМаркетологи',
        reply_markup=keyboard
    )


async def block_user(message: types.Message, state: FSMContext):
    await model(
        message,
        'Введите id пользователя для блокировки',
        AdminStates.block
    )


async def blocked(message: types.Message, state: FSMContext):
    await state.finish()
    id = message.text.split()
    try:
        user = await db.block_user(id[0])
        if user:
            await message.answer(
                'Пользователь с данным id заблокирован.'
                '\nДля разблокировки введите команду /unblock'
            )
        else:
            await message.answer('Пользователь с данным id не найден.')
    except InvalidTextRepresentationError:
        await message.answer('Некорректно указан id пользователя.')
    except NumericValueOutOfRangeError:
        await message.answer('Некорректно указан id пользователя.')


async def model(message: types.Message, word: str, station, keyboard=None):
    user_id = message.from_user.id
    if user_id in admin_list:
        await station.set()
        await message.answer(word, reply_markup=keyboard)


async def unblock_user(message: types.Message, state: FSMContext):
    await model(
        message,
        'Введите id пользователя для разблокировки',
        AdminStates.unblock
    )


async def unblocked(message: types.Message, state: FSMContext):
    await state.finish()
    id = message.text.split()
    try:
        user = await db.unblock_user(id[0])
        if user:
            await message.answer(
                'Пользователь с данным id разблокирован.'
                '\nДля блокировки введите команду /block'
            )
        else:
            await message.answer('Пользователь с данным id не найден.')
    except InvalidTextRepresentationError:
        await message.answer('Некорректно указан id пользователя.')
    except NumericValueOutOfRangeError:
        await message.answer('Некорректно указан id пользователя.')


async def status_user(message: types.Message, state: FSMContext):
    await model(
        message,
        'Введите id пользователя для уточнения статуса '
        '(заблокирован/разблокирован)',
        AdminStates.status
    )


async def get_status(message: types.Message, state: FSMContext):
    await state.finish()
    id = message.text.split()
    try:
        status = await db.get_status(id[0])
        if status is not None:
            if status is True:
                await message.answer('Пользователь с данным id заблокирован.')
            elif status is False:
                await message.answer(
                    'Пользователь с данным id не заблокирован.'
                )
        else:
            await message.answer('Пользователь с данным id не найден.')
    except InvalidTextRepresentationError:
        await message.answer('Некорректно указан id пользователя.')
    except NumericValueOutOfRangeError:
        await message.answer('Некорректно указан id пользователя.')


async def all_commands(message: types.Message):
    user_id = message.from_user.id
    if user_id in admin_list:
        await message.answer('/send - выполнить рассылку '
                             'по выбранным категориям\n'
                             '/block - заблокировать '
                             'пользователя по id\n'
                             '/unblock - разблокировать '
                             'пользователя по id\n'
                             '/status - узнать статус '
                             'блокировки пользователя\n'
                             '/delete - удалить свои данные '
                             'из базы данных, что бы не получать рассылку\n'
                             '/count - узнать кол-во '
                             'подписанных пользователей'
                             )


async def delete(message: types.Message):
    user_id = message.from_user.id
    if user_id in admin_list:
        await db.delete(user_id)
        await message.answer('Вы были удалены из базы данных.')


async def get_users_count(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in admin_list:
        await AdminStates.count_users.set()
        keyboard = await get_filters()
        button_all = types.InlineKeyboardButton(
            'Общее кол-во пользователей',
            callback_data='Total'
        )
        button_cancel = types.InlineKeyboardButton(
            'Отмена',
            callback_data='Отмена'
        )
        keyboard.add(button_all, button_cancel)
        await message.answer(
            'Выберите категорию по которой хотите узнать '
            'кол-во зарегестрированных пользоватлей',
            reply_markup=keyboard
        )


async def choose_count_admin(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_button(callback_query)
    await state.finish()
    user_id = callback_query.from_user.id
    type: str = callback_query.data
    if type == 'Total':
        count = await db.cout_all()
        await bot_send_message(
            user_id,
            f'Общее кол-во подписанных пользователей: {count}'
        )
    elif type != 'Отмена' and type != 'Total':
        count = await db.cout_category(type)
        await bot_send_message(
            user_id,
            f'Кол-во подписанных пользователей '
            f'по категории "{type}": {count}'
        )
