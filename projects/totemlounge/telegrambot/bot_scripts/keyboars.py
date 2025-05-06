from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


main_menu = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = '📞 Контакты'), KeyboardButton(text = '🍽 Меню')],
        [KeyboardButton(text = '🕒 Забронировать'), KeyboardButton(text = '💎 Лояльность')]
    ],
    resize_keyboard = True
)



back_btn = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = '↩️ Назад')]
    ],
    resize_keyboard = True
)

phone_request = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📱 Отправить номер телефона', request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)