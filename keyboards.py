from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

alert_response_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Я в безопасности",
                callback_data="status_safe"
            )
        ],
        [
            InlineKeyboardButton(
                text="🆘 Нужна помощь",
                callback_data="status_help"
            )
        ]
    ]
)

get_number = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отправить номер телефона", request_contact=True)]
    ],
    resize_keyboard=True,
    input_field_placeholder="Нажмите кнопку для отправки номера"
)

get_location_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📍 Отправить геолокацию",
                request_location=True
            )
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Отправьте ваше местоположение"
)