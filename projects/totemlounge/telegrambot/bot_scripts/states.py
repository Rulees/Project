from aiogram.fsm.state import StatesGroup, State

class Booking(StatesGroup):
    guest_counter     = State()
    guest_date        = State()
    guest_time        = State()
    exact_time        = State()
    guest_table       = State()
    guest_phone       = State()
    guest_name        = State()
    comment_decision  = State()
    guest_comment     = State()

class Idis(StatesGroup):
    mess_id = State()

class AdminPanel(StatesGroup):
    # Шаги для админ-панели
    choosing_action        = State()

    # Новая бронь
    new_name               = State()
    new_table              = State()
    new_date               = State()
    new_time               = State()
    new_guests             = State()  # 🛠 ВАЖНО: вот этого тебе не хватало
    new_phone              = State()

    # Снести бронь
    remove_date            = State()
    remove_table           = State()
    remove_choose_id       = State()

    # Продлить бронь
    extend_date            = State()
    extend_table           = State()
    extend_choose_id       = State()
    extend_hours           = State()

    # Текущие брони
    current_date           = State()
    current_table          = State()