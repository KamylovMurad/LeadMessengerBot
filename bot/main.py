import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from amocrm.v2 import tokens
from config_pr import db, bot, storage_token, \
    redirect_url, subdomain, client_secret, \
    client_id, button_nums, vacancy_list, vacancy_list_admin
from aiogram import Dispatcher
from bot.handlers import process_start_command, \
    form_start, get_name, get_last_name, \
    get_telephone_number, categories_num, \
    process_policy_confirmation, distribute, get_category, \
    choose_category_admin, choose_categories, response, \
    change_info, answer_to_name, \
    change_name, cancel, answer_to_surname, \
    answer_to_telephone_number, change_telephone_number, \
    change_surname, category_count, all_categories, block_user, \
    blocked, unblock_user, unblocked, status_user, \
    get_status, all_commands, delete, \
    get_users_count, choose_count_admin
from statesform import UserStates, AdminStates
from aiogram.dispatcher.filters import Command
import asyncio


async def main():
    await db.create_pool()
    await db.create_user_table()
    await db.create_sub_user_table()
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    tokens.default_token_manager(
        client_id=client_id,
        client_secret=client_secret,
        subdomain=subdomain,
        redirect_url=redirect_url,
        storage=tokens.FileTokensStorage(storage_token)
    )

    dp.register_message_handler(
        process_start_command,
        Command(commands=['start'])
    )
    dp.register_callback_query_handler(
        form_start,
        lambda c: c.data == 'form',
        state=UserStates.get_form
    )
    dp.register_message_handler(get_name, state=UserStates.name)
    dp.register_message_handler(get_last_name, state=UserStates.last_name)
    dp.register_message_handler(
        get_telephone_number,
        state=UserStates.telephone
    )
    dp.register_callback_query_handler(
        categories_num,
        lambda c: c.data in button_nums,
        state=UserStates.vacancy
    )
    dp.register_callback_query_handler(
        choose_categories,
        lambda c: c.data in vacancy_list,
        state=UserStates.categories
    )
    dp.register_callback_query_handler(
        process_policy_confirmation,
        lambda c: c.data == 'policy_agree',
        state=UserStates.policy_confirmation
    )
    dp.register_message_handler(distribute, commands=['send'])
    dp.register_message_handler(get_category, state=AdminStates.distribute)
    dp.register_callback_query_handler(
        choose_category_admin,
        lambda c: c.data in vacancy_list_admin,
        state=AdminStates.distribute
    )
    dp.register_callback_query_handler(
        response,
        lambda c: c.data == 'response_app'
    )
    dp.register_message_handler(
        change_info,
        Command(commands=['settings'])
    )
    dp.register_callback_query_handler(
        answer_to_name,
        lambda c: c.data == 'name',
        state=UserStates.choose_change
    )
    dp.register_message_handler(change_name, state=UserStates.change_name)
    dp.register_callback_query_handler(
        answer_to_surname,
        lambda c: c.data == 'surname',
        state=UserStates.choose_change
    )
    dp.register_message_handler(
        change_surname,
        state=UserStates.change_surname
    )
    dp.register_callback_query_handler(
        answer_to_telephone_number,
        lambda c: c.data == 'telephone_number',
        state=UserStates.choose_change
    )
    dp.register_message_handler(
        change_telephone_number,
        state=UserStates.change_telephone
    )
    dp.register_callback_query_handler(
        category_count,
        lambda c: c.data == 'theme_distribute',
        state=UserStates.choose_change
    )
    dp.register_callback_query_handler(
        cancel,
        lambda c: c.data == 'cancel',
        state=UserStates.choose_change
    )
    dp.register_callback_query_handler(
        all_categories,
        lambda c: c.data == 'all_categories',
        state=UserStates.vacancy
    )
    dp.register_message_handler(block_user, Command(commands=['block']))
    dp.register_message_handler(blocked, state=AdminStates.block)
    dp.register_message_handler(unblock_user, Command(commands=['unblock']))
    dp.register_message_handler(unblocked, state=AdminStates.unblock)
    dp.register_message_handler(status_user, Command(commands=['status']))
    dp.register_message_handler(get_status, state=AdminStates.status)
    dp.register_message_handler(all_commands, Command(commands=['commands']))
    dp.register_message_handler(delete, Command(commands=['delete']))
    dp.register_message_handler(get_users_count, Command(commands=['count']))
    dp.register_callback_query_handler(
        choose_count_admin,
        lambda c: c.data in vacancy_list_admin or c.data == 'Total',
        state=AdminStates.count_users
    )

    try:
        await dp.start_polling(bot)
    except Exception as ex:
        logging.error(f'[!!! Exception] - {ex}', exc_info=True)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
