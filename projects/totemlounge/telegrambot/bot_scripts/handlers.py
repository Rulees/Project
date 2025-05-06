# bot_scripts/handlers.py
import os
import asyncio
from random import choice
from datetime import datetime, timedelta

import aiosqlite
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from aiogram.fsm.context import FSMContext

from bot_scripts import keyboards as kb
from bot_scripts import inlines as inl
from bot_scripts.phrases import loading
from bot_scripts.states import Booking, Idis, AdminPanel
from bot_scripts.btn_functions import (
    create_time, create_dates, generate_times,
    TABLES, create_tables_keyboard, create_admin_dates
)
from bot_scripts.db import save_booking, get_booked_tables, db_fetchall, db_execute
import dotenv

dotenv.load_dotenv()
router = Router()
DB_NAME = "bookings.db"
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
ADMIN_MENU = int(os.getenv("ADMIN_MENU", "0"))

# «Назад в админ-панель»
admin_back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад в админ-панель", callback_data="admin_back")]
])

################
# Старт и главное меню
################

@router.message(Command('start'))
@router.message(Command('start'))
async def start_command(message: Message, state: FSMContext):
    # Проверяем, если сообщение от пользователя не первое
    prev_message_id = (await state.get_data()).get('mess_id')
    if prev_message_id:
        try:
            # Удаляем старое сообщение
            await message.bot.delete_message(message.chat.id, prev_message_id)
        except Exception as e:
            # Логируем ошибку, если не удалось удалить
            print(f"Ошибка при удалении старого сообщения: {e}")

    await state.set_state(Idis.mess_id)
    if message.chat.type == 'private':
        sent = await message.reply(
            '🌟 Добро пожаловать в Totem Lounge! Выберите действие:',
            reply_markup=kb.main_menu
        )
        await state.update_data(mess_id=sent.message_id)
    else:
        await message.reply('Не лезь 🤬')

@router.message(Command('info'))
async def info_command(message: Message):
    if message.chat.type == 'private':
        await message.answer('ℹ️ Доступные команды:\n\n/start - Начало работы\n/help - Список команд\n')
    else:
        await message.answer('не лезь 🤬')

@router.message(F.text == '📞 Контакты')
async def contacts(message: Message):
    await message.reply(
        "📱 WhatsApp: [Перейти](https://wa.me/79139598888)\n"
        "📢 Канал: [Перейти](https://t.me/Totemhookahbar)\n"
        "🌎 Сайт: [Перейти](https://totemlounge.ru/)\n"
        "📷 Instagram: [Перейти](https://www.instagram.com/totem.hookah.bar)",
        disable_web_page_preview=True,
        parse_mode='Markdown'
    )

@router.message(F.text == '🍽 Меню')
async def show_menu(message: Message, state: FSMContext):
    data = await state.get_data()
    prev = data.get('mess_id')
    if prev:
        await message.bot.delete_message(message.chat.id, prev)
    sent = await message.answer('🎁 Наше меню:', reply_markup=inl.menu_site)
    await state.update_data(mess_id=sent.message_id)

@router.message(F.text == '💎 Лояльность')
async def send_loyalty(message: Message, state: FSMContext):
    data = await state.get_data()
    prev = data.get('mess_id')
    if prev:
        await message.bot.delete_message(message.chat.id, prev)
    sent = await message.answer('🎁 Наша программа лояльности:', reply_markup=inl.loyalty_bot)
    await state.update_data(mess_id=sent.message_id)

@router.callback_query(F.data == 'back')
async def back_to_main(query: CallbackQuery, state: FSMContext):
    await query.answer()
    data = await state.get_data()
    prev_message_id = data.get('mess_id')
    if prev_message_id:
        try:
            # Удаляем старое сообщение
            await query.bot.delete_message(query.message.chat.id, prev_message_id)
        except Exception as e:
            # Логируем ошибку, если не удалось удалить
            print(f"Ошибка при удалении сообщения: {e}")

    sent = await query.message.answer(choice(loading))
    await asyncio.sleep(0.5)
    await query.bot.delete_message(sent.chat.id, sent.message_id)

    menu = await query.message.answer('🏠 Главное меню:', reply_markup=kb.main_menu)
    await state.update_data(mess_id=menu.message_id)

#############################
# Бронирование пользователя #
#############################

@router.message(F.text == '🕒 Забронировать')
async def bron(message: Message, state: FSMContext):
    sent = await message.answer(choice(loading))
    await asyncio.sleep(0.5)
    await message.bot.delete_message(sent.chat.id, sent.message_id)
    prev = (await state.get_data()).get('mess_id')
    if prev:
        await message.bot.delete_message(message.chat.id, prev)
    await state.set_state(Booking.guest_counter)
    sent = await message.answer('👥 Выберите число гостей:', reply_markup=inl.countrilka)
    await state.update_data(mess_id=sent.message_id)

@router.callback_query(F.data.in_([str(i) for i in range(1, 13)]))
async def guest_count(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    sent = await query.message.answer(choice(loading))
    await asyncio.sleep(0.5)
    await query.bot.delete_message(sent.chat.id, sent.message_id)
    await state.update_data(guest_count=int(query.data))
    sent = await query.message.answer('📅 Выберите дату:', reply_markup=create_dates())
    await state.update_data(mess_id=sent.message_id)
    await state.set_state(Booking.guest_date)

@router.callback_query(F.data.startswith(('weekday_', 'weekend_')))
async def user_date_choice(query: CallbackQuery, state: FSMContext):
    if await state.get_state() != Booking.guest_date.state:
        return
    await query.answer()
    await query.message.delete()
    sent = await query.message.answer(choice(loading))
    await asyncio.sleep(0.5)
    await query.bot.delete_message(sent.chat.id, sent.message_id)
    date = query.data.split('_', 1)[1]
    await state.update_data(guest_date=date)
    is_weekend = query.data.startswith('weekend_')
    sent = await query.message.answer("🕰 В какое время хотите прийти?", reply_markup=create_time(is_weekend))
    await state.update_data(mess_id=sent.message_id)
    await state.set_state(Booking.guest_time)

@router.callback_query(F.data.startswith('time_') & ~F.data.contains(':'))
async def time_range_choice(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    sent = await query.message.answer(choice(loading))
    await asyncio.sleep(0.5)
    await query.bot.delete_message(sent.chat.id, sent.message_id)
    rng = query.data.removeprefix('time_')
    await state.update_data(time_range=rng)
    if rng == 'morning':
        markup = generate_times("10:00", "12:00")
    elif rng == 'afternoon':
        markup = generate_times("13:00", "16:00")
    elif rng == 'evening':
        markup = generate_times("17:00", "21:00")
    elif rng == 'night':
        markup = generate_times("22:00", "00:00")
    else:
        markup = generate_times("22:00", "02:00")
    sent = await query.message.answer("⏰ Выберите конкретное время:", reply_markup=markup)
    await state.update_data(mess_id=sent.message_id)
    await state.set_state(Booking.exact_time)

@router.callback_query(F.data.startswith('time_') & F.data.contains(':'))
async def exact_time_choice(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    selected = query.data.split('_', 1)[1]
    await state.update_data(exact_time=selected)

    data = await state.get_data()
    guest_date = data['guest_date']
    guest_count = data['guest_count']

    sent = await query.message.answer(choice(loading))
    await asyncio.sleep(0.5)
    await query.bot.delete_message(sent.chat.id, sent.message_id)

    booked = await get_booked_tables(guest_date, selected)
    avail = [
        (tn, desc, (min_g, max_g))
        for tn, (desc, (min_g, max_g)) in TABLES.items()
        if tn not in booked and min_g <= guest_count <= max_g
    ]

    if not avail:
        await query.message.answer(
            "😔 Нет свободных столиков.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard =[ [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="back_in_booking")
            ]])
        )
        return

    sent = await query.message.answer("🪑 Выберите столик:", reply_markup=create_tables_keyboard(avail))
    await state.update_data(mess_id=sent.message_id)
    await state.set_state(Booking.guest_table)

@router.callback_query(F.data == 'table_auto')
async def auto_select_table(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    data = await state.get_data()
    booked = await get_booked_tables(data['guest_date'], data['exact_time'])
    guest_count = data['guest_count']

    candidates = [
        (tn, desc, min_g, max_g)
        for tn, (desc, (min_g, max_g)) in TABLES.items()
        if tn not in booked and min_g <= guest_count <= max_g
    ]

    if not candidates:
        await query.message.answer(
            "😔 Нет подходящих столов.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_in_booking")]]))
        return

    tn, desc, min_g, max_g = sorted(candidates, key=lambda x: (x[2], x[3]))[0]
    await state.update_data(guest_table=tn)
    await query.message.answer(
        f"🤖 Предлагаю стол {tn}: {desc} ({min_g}-{max_g} чел.)\nПодходит?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да", callback_data="table_confirm")],
            [InlineKeyboardButton(text="❌ Вручную", callback_data="table_manual")]
        ])
    )

@router.callback_query(F.data == 'table_confirm')
async def confirm_auto_table(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    sent = await query.message.answer("📱 Отправьте номер телефона:", reply_markup=kb.phone_request)
    await state.update_data(mess_id=sent.message_id)
    await state.set_state(Booking.guest_phone)

@router.callback_query(F.data == 'table_manual')
async def manual_table_select(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    data = await state.get_data()
    booked = await get_booked_tables(data['guest_date'], data['exact_time'])
    avail = [
        (tn, desc, (min_g, max_g))
        for tn, (desc, (min_g, max_g)) in TABLES.items()
        if tn not in booked and min_g <= data['guest_count'] <= max_g
    ]
    sent = await query.message.answer("🪑 Выберите столик:", reply_markup=create_tables_keyboard(avail))
    await state.update_data(mess_id=sent.message_id)
    await state.set_state(Booking.guest_table)

@router.callback_query(F.data.startswith('table_'))
async def table_choice(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    num = int(query.data.split('_', 1)[1])
    await state.update_data(guest_table=num)
    sent = await query.message.answer(choice(loading))
    await asyncio.sleep(0.5)
    await query.bot.delete_message(sent.chat.id, sent.message_id)
    sent = await query.message.answer('📱 Отправьте номер телефона:', reply_markup=kb.phone_request)
    await state.update_data(mess_id=sent.message_id)
    await state.set_state(Booking.guest_phone)

@router.message(F.contact)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(guest_phone=message.contact.phone_number)
    sent = await message.answer('👤 Введите ваше имя:')
    await state.update_data(mess_id=sent.message_id)
    await state.set_state(Booking.guest_name)

@router.message(Booking.guest_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(guest_name=message.text.strip())
    kb_comment = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Оставить", callback_data="add_comment"),
            InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_comment")
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_in_booking")]
    ])
    sent = await message.answer('Хотите оставить комментарий?', reply_markup=kb_comment)
    await state.update_data(mess_id=sent.message_id)
    await state.set_state(Booking.comment_decision)

@router.callback_query(F.data == "add_comment")
async def add_comment(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    sent = await query.message.answer(choice(loading))
    await asyncio.sleep(0.5)
    await query.bot.delete_message(sent.chat.id, sent.message_id)
    sent = await query.message.answer("✏️ Напишите комментарий:")
    await state.update_data(mess_id=sent.message_id)
    await state.set_state(Booking.guest_comment)

@router.callback_query(F.data == "skip_comment")
async def skip_comment(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    data = await state.get_data()
    await finish_booking(query.message, data, comment=None)
    await state.clear()

@router.message(Booking.guest_comment)
async def save_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    await finish_booking(message, data, comment=message.text.strip())
    await state.clear()

async def finish_booking(message, booking_data, comment=None):
    await save_booking(
        date=booking_data['guest_date'],
        time=booking_data['exact_time'],
        guest_count=booking_data['guest_count'],
        table_number=booking_data['guest_table'],
        phone_number=booking_data['guest_phone'],
        guest_name=booking_data['guest_name'],
        comment=comment,
        duration=2
    )
    from datetime import timedelta

    # Преобразуем exact_time в datetime, если это строка
    if isinstance(booking_data['exact_time'], str):
        booking_data['exact_time'] = datetime.strptime(booking_data['exact_time'], '%H:%M')

    # Формирование текста для админа
    admin_text = (
        f"📣 <b>Новая бронь</b>\n"
        f"👥 {booking_data['guest_count']} гостей\n"
        f"📅 {booking_data['guest_date']}\n"
        f"🕰 {booking_data['exact_time'].strftime('%H:%M')} - {(booking_data['exact_time'] + timedelta(hours=2)).strftime('%H:%M')}\n"
        f"🪑 Стол {booking_data['guest_table']}\n"
        f"📱 {booking_data['guest_phone']}\n"
        f"👤 {booking_data['guest_name']}\n"
    )

    if comment:
        admin_text += f"📝 {comment}\n"

    await message.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="HTML")

    # Формирование текста для пользователя
    user_text = (
        "✅ Ваша бронь оформлена!\n\n"
        f"👥 {booking_data['guest_count']} гостей\n"
        f"📅 {booking_data['guest_date']}\n"
        f"🕰 {booking_data['exact_time'].strftime('%H:%M')} - {(booking_data['exact_time'] + timedelta(hours=2)).strftime('%H:%M')}\n"
        f"🪑 Стол {booking_data['guest_table']}\n"
        f"📱 {booking_data['guest_phone']}\n"
        f"👤 {booking_data['guest_name']}\n"
    )
    if comment:
        user_text += f"📝 {comment}\n"
    user_text += "\n💌 Бронь сохраняется 15 минут.\n❗Сообщите об отмене или задержке!"
    await message.answer(user_text, reply_markup=kb.main_menu)
# ===============================
# 🔒 АДМИНСКАЯ ПАНЕЛЬ
# ===============================

@router.message(Command('admin'))
async def open_admin_panel(message: Message, state: FSMContext):
    if message.chat.id == ADMIN_MENU:
        await state.set_state(AdminPanel.choosing_action)
        await message.answer("🔒 Админ-панель открыта:", reply_markup=inl.admin_menu)
    else:
        await message.answer("❌ У вас нет доступа к админ-панели.")


@router.callback_query(F.data == "admin_back", F.message.chat.id == ADMIN_MENU)
async def back_to_admin_panel(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(AdminPanel.choosing_action)
    await query.message.edit_text("🔒 Админ-панель:", reply_markup=inl.admin_menu)


@router.callback_query(F.data == "admin_close", F.message.chat.id == ADMIN_MENU)
async def close_admin_panel(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    await query.message.answer("🔒 Админ-панель закрыта.")
    await state.clear()

# ===== Новая бронь =====

@router.callback_query(F.data == "admin_new", F.message.chat.id == ADMIN_MENU)
async def admin_new_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.edit_text("🆕 Введите имя клиента:", reply_markup=admin_back)
    await state.set_state(AdminPanel.new_name)

@router.message(AdminPanel.new_name, F.chat.id == ADMIN_MENU)
async def admin_new_name(message: Message, state: FSMContext):
    if not message.text:
        return await message.answer("❌ Введите текст сообщением.", reply_markup=admin_back)
    await state.update_data(new_name=message.text.strip())
    await message.answer("Укажите номер столика:", reply_markup=admin_back)
    await state.set_state(AdminPanel.new_table)


@router.callback_query(F.data == "back_in_booking")
async def back_in_booking_process(query: CallbackQuery, state: FSMContext):
    await query.answer()
    current_state = await state.get_state()

    await query.message.delete()

    if current_state == Booking.guest_table.state:
        # Возврат к выбору времени
        data = await state.get_data()
        is_weekend = "weekend_" in data['guest_date']
        sent = await query.message.answer(
            "🕰 В какое время хотите прийти?",
            reply_markup=create_time(is_weekend)
        )
        await state.update_data(mess_id=sent.message_id)
        await state.set_state(Booking.guest_time)

    elif current_state == Booking.exact_time.state:
        # Возврат к выбору диапазона времени
        data = await state.get_data()
        is_weekend = "weekend_" in data['guest_date']
        sent = await query.message.answer(
            "🕰 Выберите временной диапазон:",
            reply_markup=create_time(is_weekend)
        )
        await state.update_data(mess_id=sent.message_id)
        await state.set_state(Booking.guest_time)

    elif current_state == Booking.guest_time.state:
        # Возврат к выбору даты
        sent = await query.message.answer(
            "📅 Выберите дату:",
            reply_markup=create_dates()
        )
        await state.update_data(mess_id=sent.message_id)
        await state.set_state(Booking.guest_date)

    elif current_state == Booking.guest_date.state:
        # Возврат к выбору количества гостей
        sent = await query.message.answer(
            "👥 Выберите число гостей:",
            reply_markup=inl.countrilka
        )
        await state.update_data(mess_id=sent.message_id)
        await state.set_state(Booking.guest_counter)

    elif current_state == Booking.guest_counter.state:
        # Выход в главное меню
        await state.clear()
        sent = await query.message.answer(
            "🏠 Главное меню:",
            reply_markup=kb.main_menu
        )
        await state.update_data(mess_id=sent.message_id)

    elif current_state == Booking.comment_decision.state:
        # Возврат к вводу имени
        sent = await query.message.answer("👤 Введите ваше имя:")
        await state.update_data(mess_id=sent.message_id)
        await state.set_state(Booking.guest_name)

    else:
        # Дефолтный сценарий
        await state.clear()
        await query.message.answer(
            "🏠 Главное меню:",
            reply_markup=kb.main_menu
        )

@router.message(AdminPanel.new_table, F.chat.id == ADMIN_MENU)
async def admin_new_table(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        return await message.answer("❌ Введите номер столика цифрами.", reply_markup=admin_back)
    await state.update_data(new_table=int(message.text.strip()))
    await message.answer("Укажите дату брони (YYYY-MM-DD):", reply_markup=admin_back)
    await state.set_state(AdminPanel.new_date)

@router.message(AdminPanel.new_date, F.chat.id == ADMIN_MENU)
async def admin_new_date(message: Message, state: FSMContext):
    try:
        chosen_date = datetime.strptime(message.text.strip(), "%Y-%m-%d").date()
        if chosen_date > datetime.now().date() + timedelta(days=30):
            return await message.answer("❌ Можно бронировать только на ближайшие 30 дней.", reply_markup=admin_back)
    except ValueError:
        return await message.answer("❌ Введите дату в формате YYYY-MM-DD.", reply_markup=admin_back)

    await state.update_data(new_date=message.text.strip())
    await message.answer("Укажите время брони (HH:MM):", reply_markup=admin_back)
    await state.set_state(AdminPanel.new_time)

@router.message(AdminPanel.new_time, F.chat.id == ADMIN_MENU)
async def admin_new_time(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text.strip(), "%H:%M")
    except ValueError:
        return await message.answer("❌ Введите время в формате HH:MM (например, 18:30).", reply_markup=admin_back)

    await state.update_data(new_time=message.text.strip())
    await message.answer("Сколько гостей будет?", reply_markup=admin_back)
    await state.set_state(AdminPanel.new_guests)

@router.message(AdminPanel.new_guests, F.chat.id == ADMIN_MENU)
async def admin_new_guests(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        return await message.answer("❌ Введите количество гостей цифрами.", reply_markup=admin_back)
    await state.update_data(new_guest_count=int(message.text.strip()))
    await message.answer("Введите телефон клиента:", reply_markup=admin_back)
    await state.set_state(AdminPanel.new_phone)

@router.message(AdminPanel.new_phone, F.chat.id == ADMIN_MENU)
async def admin_new_phone(message: Message, state: FSMContext):
    if not message.text:
        return await message.answer("❌ Введите телефон текстом.", reply_markup=admin_back)
    data = await state.get_data()
    await admin_save_booking(data, message.text)
    await message.answer("✅ Бронь успешно создана.")
    await message.answer("🔒 Админ-панель:", reply_markup=inl.admin_menu)
    await state.set_state(AdminPanel.choosing_action)

# ===== Текущие брони =====

@router.callback_query(F.data == "admin_current", F.message.chat.id == ADMIN_MENU)
async def admin_current_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.edit_text("📅 Выберите дату:", reply_markup=create_admin_dates())
    await state.set_state(AdminPanel.current_date)

@router.callback_query(AdminPanel.current_date, F.data.startswith('admin_date_'))
async def admin_current_date_choice(query: CallbackQuery, state: FSMContext):
    await query.answer()
    date = query.data.split('_')[2]
    await state.update_data(current_date=date)

    rows = await db_fetchall(
        "SELECT id, time, duration, guest_name, table_number FROM bookings WHERE date=? ORDER BY time",
        (date,)
    )

    if not rows:
        await query.message.edit_text(f"❌ Нет броней на {date}.", reply_markup=admin_back)
    else:
        text = f"📋 Брони на {date}:\n\n"
        text += "ID — Время — Длительность — Имя — Стол\n"
        text += "\n".join(f"{r[0]} — {r[1]} — {r[2]}ч — {r[3]} — Стол {r[4]}" for r in rows)
        await query.message.edit_text(text)

    await state.set_state(AdminPanel.choosing_action)
    await query.message.answer("🔒 Админ-панель:", reply_markup=inl.admin_menu)

# ===== Удаление =====

@router.callback_query(F.data == "admin_remove", F.message.chat.id == ADMIN_MENU)
async def admin_remove_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.edit_text("❌ Выберите дату для удаления:", reply_markup=create_admin_dates())
    await state.set_state(AdminPanel.remove_date)

@router.callback_query(AdminPanel.remove_date, F.data.startswith('admin_date_'))
async def admin_remove_date_choice(query: CallbackQuery, state: FSMContext):
    await query.answer()
    date = query.data.split('_')[2]
    await state.update_data(remove_date=date)
    await query.message.edit_text("Введите номер столика:", reply_markup=admin_back)
    await state.set_state(AdminPanel.remove_table)

# ===== Продление =====

@router.callback_query(F.data == "admin_extend", F.message.chat.id == ADMIN_MENU)
async def admin_extend_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.edit_text("⏳ Выберите дату для продления:", reply_markup=create_admin_dates())
    await state.set_state(AdminPanel.extend_date)

@router.callback_query(AdminPanel.extend_date, F.data.startswith('admin_date_'))
async def admin_extend_date_choice(query: CallbackQuery, state: FSMContext):
    await query.answer()
    date = query.data.split('_')[2]
    await state.update_data(extend_date=date)
    await query.message.edit_text("Введите номер столика:", reply_markup=admin_back)
    await state.set_state(AdminPanel.extend_table)



@router.message(AdminPanel.current_table, F.chat.id == ADMIN_MENU)
async def admin_current_table(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("❌ Введите номер столика цифрами.", reply_markup=admin_back)
        return
    table_no = int(message.text.strip())
    data = await state.get_data()
    rows = await db_fetchall(
        "SELECT id, time, duration, guest_name FROM bookings WHERE date=? AND table_number=? ORDER BY time",
        (data['current_date'], table_no)
    )
    if not rows:
        await message.answer("❌ Нет броней.", reply_markup=admin_back)
    else:
        text = "ID — Время — Длительность — Имя\n" + "\n\n".join(f"{r[0]} — {r[1]} — {r[2]}ч — {r[3]}" for r in rows)
        await message.answer(text)
    await message.answer("🔒 Админ-панель:", reply_markup=inl.admin_menu)
    await state.set_state(AdminPanel.choosing_action)

@router.message(AdminPanel.remove_date, F.chat.id == ADMIN_MENU)
async def admin_remove_date(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Введите дату.", reply_markup=admin_back)
        return
    await state.update_data(remove_date=message.text.strip())
    await message.answer("Укажите номер столика:", reply_markup=admin_back)
    await state.set_state(AdminPanel.remove_table)

@router.message(AdminPanel.remove_table, F.chat.id == ADMIN_MENU)
async def admin_remove_table(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("❌ Введите номер столика цифрами.", reply_markup=admin_back)
        return
    await state.update_data(remove_table=int(message.text.strip()))
    data = await state.get_data()
    rows = await db_fetchall(
        "SELECT id, time, guest_name FROM bookings WHERE date=? AND table_number=? ORDER BY time",
        (data['remove_date'], data['remove_table'])
    )
    if not rows:
        await message.answer("❌ Нет броней.", reply_markup=admin_back)
    else:
        text = "ID — Время — Имя\n" + "\n".join(f"{r[0]} — {r[1]} — {r[2]}" for r in rows)
        await message.answer(text + "\n\nВведите ID для удаления:", reply_markup=admin_back)
    await state.set_state(AdminPanel.remove_choose_id)

@router.message(AdminPanel.remove_choose_id, F.chat.id == ADMIN_MENU)
async def admin_remove_confirm(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("❌ Введите ID цифрами.", reply_markup=admin_back)
        return
    bid = int(message.text.strip())
    await db_execute("DELETE FROM bookings WHERE id=?", (bid,))
    await message.answer(f"✅ Бронь ID {bid} удалена.")
    await message.answer("🔒 Админ-панель:", reply_markup=inl.admin_menu)
    await state.set_state(AdminPanel.choosing_action)


@router.message(AdminPanel.extend_date, F.chat.id == ADMIN_MENU)
async def admin_extend_date(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Введите дату.", reply_markup=admin_back)
        return
    await state.update_data(extend_date=message.text.strip())
    await message.answer("Укажите номер столика:", reply_markup=admin_back)
    await state.set_state(AdminPanel.extend_table)

@router.message(AdminPanel.extend_table, F.chat.id == ADMIN_MENU)
async def admin_extend_table(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("❌ Введите номер столика цифрами.", reply_markup=admin_back)
        return
    await state.update_data(extend_table=int(message.text.strip()))
    data = await state.get_data()
    rows = await db_fetchall(
        "SELECT id, time, duration, guest_name FROM bookings WHERE date=? AND table_number=? ORDER BY time",
        (data['extend_date'], data['extend_table'])
    )
    if not rows:
        await message.answer("❌ Нет броней.", reply_markup=admin_back)
    else:
        text = "ID — Время — Длительность — Имя\n\n" + "\n".join(f"{r[0]} — {r[1]} — {r[2]}ч — {r[3]}" for r in rows)
        await message.answer(text + "\n\nВведите ID для продления:", reply_markup=admin_back)
    await state.set_state(AdminPanel.extend_choose_id)

@router.message(AdminPanel.extend_choose_id, F.chat.id == ADMIN_MENU)
async def admin_extend_choose(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("❌ Введите ID цифрами.", reply_markup=admin_back)
        return
    await state.update_data(extend_id=int(message.text.strip()))
    await message.answer("На сколько часов продлить?", reply_markup=admin_back)
    await state.set_state(AdminPanel.extend_hours)

@router.message(AdminPanel.extend_hours, F.chat.id == ADMIN_MENU)
async def admin_extend_hours(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("❌ Введите количество часов цифрами.", reply_markup=admin_back)
        return
    hours = int(message.text.strip())
    data = await state.get_data()
    await db_execute(
        "UPDATE bookings SET duration = duration + ? WHERE id = ?",
        (hours, data['extend_id'])
    )
    await message.answer(f"✅ Продлено на {hours} ч.")
    await message.answer("🔒 Админ-панель:", reply_markup=inl.admin_menu)
    await state.set_state(AdminPanel.choosing_action)

async def admin_save_booking(data, phone_number):
    await save_booking(
        date=data['new_date'],
        time=data['new_time'],
        guest_count=data['new_guest_count'],
        table_number=data['new_table'],
        phone_number=phone_number.strip(),
        guest_name=data['new_name'],
        comment=None,
        duration=2,
        by_admin=1
    )

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
async def reminder_task(bot):
    while True:
        now = datetime.now()
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute("""
                SELECT id, chat_id, guest_name, date, time
                FROM bookings
                WHERE review_notification_sent = 0
            """)
            bookings = await cursor.fetchall()

        for booking in bookings:
            booking_id, chat_id, guest_name, date_str, time_str = booking

            booking_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            remind_time = booking_time - timedelta(hours=1)

            if remind_time <= now <= booking_time:
                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"⚡ Привет, {guest_name}!\nНапоминаем о вашей брони сегодня в {time_str}. Пожалуйста, подтвердите присутствие!",
                        reply_markup=inl.confirm_booking_keyboard(booking_id)
                    )
                except Exception as e:
                    with open("bot_errors.log", "a", encoding="utf-8") as f:
                        f.write(f"{datetime.now()}: Ошибка отправки напоминания: {e}\n")

        await asyncio.sleep(60)  # Проверять каждую минуту

async def send_review_link_task(bot):
    while True:
        now = datetime.now()
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute("""
                SELECT id, chat_id, guest_name, date, time, duration, review_notification_sent
                FROM bookings
                WHERE review_notification_sent = 0
            """)
            bookings = await cursor.fetchall()

        for booking in bookings:
            booking_id, chat_id, guest_name, date_str, time_str, duration, review_sent = booking

            booking_start = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            booking_end = booking_start + timedelta(hours=duration)

            # Ждём час после окончания брони
            if booking_end - booking_end <= now:
                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"⭐ Спасибо, {guest_name}, что были у нас!\n\n"
                             f"Если всё понравилось, пожалуйста, оставьте отзыв о Totem Lounge: [Оценить в 2ГИС](https://2gis.ru/novosibirsk/firm/70000001067832773)",
                        parse_mode="Markdown",
                    )

                    # Помечаем бронь как "отзыв отправлен"
                    async with aiosqlite.connect(DB_NAME) as db:
                        await db.execute(
                            "UPDATE bookings SET review_notification_sent = 1 WHERE id = ?",
                            (booking_id,)
                        )
                        await db.commit()

                except Exception as e:
                    with open("bot_errors.log", "a", encoding="utf-8") as f:
                        f.write(f"{datetime.now()}: Ошибка отправки отзыва: {e}\n")

        await asyncio.sleep(300)  # Проверять каждые 5 минут




