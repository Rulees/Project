# bot_scripts/inlines.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Меню «🍽 Перейти в меню»
menu_site = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🍽 Перейти в меню", url="https://totemlounge.ru/menu")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back")]
    ]
)

# Меню «💎 Лояльность»
loyalty_bot = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Подробнее", url="https://totemlounge.ru/loyalty")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back")]
    ]
)

# Счётчик гостей (готово, кнопка «↩️ Назад» уже была)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
countrilka = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='1', callback_data='1'),
            InlineKeyboardButton(text='2', callback_data='2'),
            InlineKeyboardButton(text='3', callback_data='3')
        ],
        [
            InlineKeyboardButton(text='4', callback_data='4'),
            InlineKeyboardButton(text='5', callback_data='5'),
            InlineKeyboardButton(text='6', callback_data='6')
        ],
        [
            InlineKeyboardButton(text='7', callback_data='7'),
            InlineKeyboardButton(text='8', callback_data='8'),
            InlineKeyboardButton(text='9', callback_data='9')
        ],
        [
            InlineKeyboardButton(text='️10', callback_data='10'),
            InlineKeyboardButton(text='11', callback_data='11'),
            InlineKeyboardButton(text='12', callback_data='12'),
        ],
        [
            InlineKeyboardButton(text='↩️ Назад', callback_data='back')
        ]
    ]
)

admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🆕 Новая бронь",      callback_data="admin_new")],
    [InlineKeyboardButton(text="❌ Снести бронь",     callback_data="admin_remove")],
    [InlineKeyboardButton(text="⏳ Продлить бронь",   callback_data="admin_extend")],
    [InlineKeyboardButton(text="📋 Текущие",          callback_data="admin_current")],
    [InlineKeyboardButton(text="❎ Закрыть панель",   callback_data="admin_close")],
])

def confirm_booking_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{booking_id}"),
        InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{booking_id}")
    ]])