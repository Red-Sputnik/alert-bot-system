from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import keyboards as kb
from states import Reg
from database import Database

db = Database()
user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Добро пожаловать!\n\nВведите ваше имя:",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(Reg.name)

@user_router.message(Command("alert"))
async def send_alert(message:Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет прав для отправки оповещений.")
        return

alert_text = (
        "⚠️ ВНИМАНИЕ!\n\n"
        "Зафиксирована чрезвычайная ситуация.\n"
        "Следуйте инструкциям экстренных служб.\n\n"
        "Дополнительная информация будет направлена позже."
    )

users = db.get_all_users()
sent = 0

for (telegram_id,) in users:
    try:
        await message.bot.send_message(
            chat_id=telegram_id,
            text=alert_text
        )
        sent += 1
    except Exception:
        continue

await message.answer(
    f"✅ Оповещение отправлено.\n"
    f"Получателей: {sent}"
)


@user_router.message(Reg.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("Имя слишком короткое. Повторите ввод.")
        return

    await state.update_data(name=name)

    await message.answer(
        "Теперь отправьте номер телефона:",
        reply_markup=kb.get_number
    )

    await state.set_state(Reg.phone)


@user_router.message(Reg.phone)
async def process_phone(message: Message, state: FSMContext):
    if not message.contact:
        await message.answer(
            "Пожалуйста, используйте кнопку для отправки номера телефона."
        )
        return

    phone = message.contact.phone_number

    data = await state.get_data()
    name = data["name"]

    db.add_user(
        telegram_id=message.from_user.id,
        name=name,
        phone=phone
    )

    await message.answer(
        "Регистрация завершена.\n\n"
        "Теперь вы будете получать оповещения в случае ЧС.",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.clear()

@user_router.callback_query(F.data.startswith("brand_"))
async def check_brand(callback: CallbackQuery):
    brand_name = callback.data.split("_", 1)[1]

    await callback.answer(
        f"Вы выбрали {brand_name.capitalize()}",
        show_alert=True
    )

    await callback.message.answer(
        f"Вы выбрали {brand_name.capitalize()}!"
    )


@user_router.message()
async def unknown_message(message: Message):
    await message.answer(
        "Команда не распознана. Используйте /start."
    )
