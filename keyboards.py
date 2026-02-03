from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from regions import REGIONS

REGIONS_PER_PAGE = 8

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

def regions_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    regions_items = list(REGIONS.items())
    total_pages = (len(regions_items) - 1) // REGIONS_PER_PAGE

    start = page * REGIONS_PER_PAGE
    end = start + REGIONS_PER_PAGE
    page_items = regions_items[start:end]

    keyboard = []

    # Кнопки регионов
    for code, name in page_items:
        keyboard.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"region_pick:{code}"
            )
        ])

    # Навигация
    nav_buttons = []

    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"region_page:{page - 1}"
            )
        )

    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️ Вперёд",
                callback_data=f"region_page:{page + 1}"
            )
        )

    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)