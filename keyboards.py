from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Каталог")],
        [KeyboardButton(text="Корзина"),
        KeyboardButton(text="Контакты")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню"
)

catalog = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Nike", callback_data="brand_nike")],
        [InlineKeyboardButton(text="Adidas", callback_data="brand_adidas")],
        [InlineKeyboardButton(text="Reebook", callback_data="brand_reebook")],
    ]
)

get_number = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отправить номер телефона", request_contact=True)]
    ]
)