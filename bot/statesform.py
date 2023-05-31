from aiogram.dispatcher.filters.state import State, StatesGroup


class UserStates(StatesGroup):
    policy_confirmation = State()
    get_form = State()
    name = State()
    last_name = State()
    telephone = State()
    vacancy = State()
    categories = State()
    choose_change = State()
    change_name = State()
    change_surname = State()
    change_telephone = State()


class AdminStates(StatesGroup):
    distribute = State()
    block = State()
    unblock = State()
    status = State()
    count_users = State()
