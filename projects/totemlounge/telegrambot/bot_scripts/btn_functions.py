# bot_scripts/btn_functions.py
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot_scripts.phrases import WEEKDAY_EMOJIS, TIME_EMOJIS

# ➡️ Таблица столов: теперь диапазоны гостей (min, max)
TABLES = {
    1: ("Зона с цепями", (1, 8)),
    2: ("Зона", (1, 2)),
    3: ("Зона", (1, 2)),
    4: ("Зона с цепями", (1, 7)),
    5: ("Зона с цепями", (1, 4)),
    6: ("Зона с цепями", (1, 4)),
    7: ("Зона с цепями", (1, 4)),
    9: ("VIP", (1, 6)),
    10: ("VIP до", (1, 4)),
    11: ("Зона у камина", (1, 2)),
    12: ("VIP большая", (1, 12)),
    13: ("Зона с PS5", (1, 3)),
    14: ("Зона у окна", (1, 4)),
    15: ("Вип малая", (1, 2)),
    16: ("Зона Авиатор", (1, 4)),
    17: ("Зона", (1, 3)),
    18: ("Зона", (1, 2)),
    19: ("Железные ставни", (1, 4)),
    20: ("Железные ставни", (1, 4)),
    21: ("Зона с PS5", (1, 5))
}

# ➡️ Генерация 7 ближайших дат
def generate_dates():
    current_date = datetime.now()
    dates = []
    for i in range(7):
        day = current_date + timedelta(days=i)
        dates.append(day.strftime('%Y-%m-%d'))
    return dates

def create_dates() -> InlineKeyboardMarkup:
    dates = generate_dates()
    inline_buttons = []
    for date in dates:
        weekday = datetime.strptime(date, '%Y-%m-%d').weekday()
        emoji = WEEKDAY_EMOJIS[weekday]
        text = f"{date} {emoji}"
        cb = f"{'weekend' if weekday >= 4 else 'weekday'}_{date}"
        inline_buttons.append([InlineKeyboardButton(text=text, callback_data=cb)])
    inline_buttons.append([InlineKeyboardButton(text='↩️ Назад', callback_data='back_in_booking')])
    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)

# ➡️ Клавиатура выбора диапазона времени
def create_time(is_weekend=False) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text='☀️ Утро (10:00–12:00)', callback_data='time_morning')],
        [InlineKeyboardButton(text='🍽️ Обед (13:00–16:00)', callback_data='time_afternoon')],
        [InlineKeyboardButton(text='🌇 Вечер (17:00–21:00)', callback_data='time_evening')],
    ]
    if is_weekend:
        buttons.append([InlineKeyboardButton(text='🌙 Ночь (22:00–02:00)', callback_data='time_night_weekend')])
    else:
        buttons.append([InlineKeyboardButton(text='🌙 Ночь (22:00–00:00)', callback_data='time_night')])
    buttons.append([InlineKeyboardButton(text='↩️ Назад', callback_data='back_in_booking')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ➡️ Генерация слотов (шаг 30 мин) + кнопка назад
def generate_times(start_hour: str, end_hour: str) -> InlineKeyboardMarkup:
    buttons = []
    current = datetime.strptime(start_hour, "%H:%M")
    end = datetime.strptime(end_hour, "%H:%M")
    if end <= current:
        end += timedelta(days=1)
    while current <= end:
        h = current.strftime("%H")
        emoji = TIME_EMOJIS.get(h, "🕰️")
        label = f"{emoji} {current.strftime('%H:%M')}"
        buttons.append(InlineKeyboardButton(text=label, callback_data=f"time_{current.strftime('%H:%M')}"))
        current += timedelta(minutes=30)
    rows = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
    rows.append([InlineKeyboardButton(text='↩️ Назад', callback_data='back_in_booking')])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ➡️ Клавиатура столов + кнопка назад + "Любая зона"
def create_tables_keyboard(available_tables):
    buttons = []

    # Кнопка "Любая зона"
    buttons.append([InlineKeyboardButton(text="🔀 Любая зона", callback_data="table_auto")])

    for table_number, desc, guest_range in available_tables:
        min_g, max_g = guest_range
        if min_g == max_g:
            text = f"🪑 {desc} ({min_g} чел.)"
        else:
            text = f"🪑 {desc} ({min_g}-{max_g} чел.)"
        btn = InlineKeyboardButton(text=text, callback_data=f"table_{table_number}")
        buttons.append([btn])

    # Кнопка "Назад"
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_in_booking")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_admin_dates():
    today = datetime.now().date()
    keyboard = []

    for i in range(7):
        date = today + timedelta(days=i)
        callback_data = f"admin_date_{date.isoformat()}"
        text = date.strftime("%d.%m (%a)").replace('Mon', 'Пн').replace('Tue', 'Вт') \
                                         .replace('Wed', 'Ср').replace('Thu', 'Чт') \
                                         .replace('Fri', 'Пт').replace('Sat', 'Сб').replace('Sun', 'Вс')
        keyboard.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)