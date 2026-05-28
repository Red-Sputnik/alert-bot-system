from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

import keyboards as kb
from states import Reg
from database import Database
from config import ADMIN_IDS, DEMO_MODE
from notifier import process_event
from logger import logger
from regions import REGIONS

db = Database()
user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    if db.user_exists(message.from_user.id):
        await message.answer(
            "Вы уже зарегистрированы и получаете оповещения."
        )
        return

    await state.clear()

    await message.answer(
        "Добро пожаловать!\n\nВведите ваше имя:",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(Reg.name)

@user_router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "ℹ️ *Справка по системе оповещения*\n\n"
        "Данный Telegram-бот предназначен для информирования населения "
        "о чрезвычайных ситуациях на территории Российской Федерации "
        "на основе официальных данных.\n\n"

        "*Основные возможности:*\n"
        "• регистрация пользователей в системе оповещения\n"
        "• выбор субъекта Российской Федерации\n"
        "• автоматическое получение предупреждений МЧС\n"
        "• адресная рассылка уведомлений по регионам\n"
        "• сбор обратной связи от населения\n\n"

        "*Доступные команды:*\n"
        "/start — регистрация в системе\n"
        "/help — справочная информация\n\n"

        "*Как работает система:*\n"
        "1️⃣ пользователь регистрируется и выбирает регион\n"
        "2️⃣ система автоматически отслеживает предупреждения МЧС\n"
        "3️⃣ при возникновении ЧС пользователь получает уведомление\n"
        "4️⃣ пользователь указывает свой статус с помощью кнопок\n\n"

        "*Статус пользователя:*\n"
        "• «В безопасности» — угрозы для жизни нет\n"
        "• «Нужна помощь» — требуется реагирование экстренных служб\n\n"

        "*Демонстрационный режим:*\n"
        "Для демонстрации работы системы предусмотрен специальный режим, "
        "позволяющий эмулировать экстренное предупреждение "
        "без ожидания реальной чрезвычайной ситуации.\n\n"

        "Будьте внимательны и соблюдайте рекомендации экстренных служб.",
        parse_mode="Markdown"
    )

@user_router.message(Command("demo_alert"))
async def demo_alert(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет прав для запуска демонстрации.")
        return

    if not DEMO_MODE:
        await message.answer("⚙️ Демонстрационный режим отключён.")
        return

    demo_event = {
        "title": "ДЕМО: Экстренное предупреждение МЧС",
        "link": "https://mchs.gov.ru/",
        "regions": ["Москва"],
        "is_demo": True
    }

    await process_event(message.bot, db, demo_event)

    await message.answer(
        "🧪 Демонстрационное оповещение отправлено.\n"
        "Событие сохранено в истории системы."
    )

@user_router.message(Command("id"))
async def my_id(message: Message):
    await message.answer(f"Ваш Telegram ID: {message.from_user.id}")


@user_router.message(Command("alert"))
async def send_alert(message:Message):
    if message.from_user.id not in ADMIN_IDS:
        logger.warning(
            f"Попытка несанкционированного оповещения: "
            f"telegram_id={message.from_user.id}"
        )
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
                text=alert_text + "\n\nУкажите ваш статус:",
                reply_markup=kb.alert_response_kb
            )
            sent += 1
        except Exception:
            continue

    await message.answer(
        f"✅ Оповещение отправлено.\n"
        f"Получателей: {sent}"
    )

    logger.warning(
        f"Оповещение ЧС отправлено. "
        f"Инициатор={message.from_user.id}, "
        f"Получателей={sent}"
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

    logger.info(
        f"Регистрация пользователя: "
        f"telegram_id={message.from_user.id}, "
        f"name={name}, phone={phone}"
    )

    await message.answer(
        "Регистрация почти завершена.\n\n"
        "Пожалуйста, выберите субъект Российской Федерации:",
        reply_markup=kb.regions_keyboard(page=0)
    )   

    await state.clear()

@user_router.callback_query(F.data.startswith("status_"))
async def handle_status(callback: CallbackQuery):
    status = callback.data.split("_", 1)[1]

    if status == "safe":
        db.update_status(
            telegram_id=callback.from_user.id,
            status="safe"
        )

        await callback.answer("Статус сохранён")
        await callback.message.answer(
            "✅ Спасибо за ответ.\nОтмечено, что вы в безопасности."
        )

    elif status == "help":
        db.update_status(
            telegram_id=callback.from_user.id,
            status="help"
        )

        await callback.answer("Запрос принят")
        await callback.message.answer(
            "🆘 Ваш запрос о помощи принят.\n"
            "Службы экстренного реагирования уведомлены."
        )

    logger.info(
    f"Статус пользователя: "
    f"telegram_id={callback.from_user.id}, "
    f"status={status}"
    )

@user_router.message(Command("my_status"))
async def my_status(message: Message):
    status = db.get_status(message.from_user.id)

    text = {
        "safe": "✅ Вы отметили, что в безопасности",
        "help": "🆘 Вы запросили помощь",
        None: "❓ Статус не задан"
    }.get(status, "❓ Статус не задан")

    await message.answer(text)

@user_router.callback_query(F.data.startswith("region_page:"))
async def change_region_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])

    await callback.message.edit_reply_markup(
        reply_markup=kb.regions_keyboard(page)
    )

    await callback.answer()

@user_router.callback_query(F.data.startswith("region_pick:"))
async def pick_region(callback: CallbackQuery):
    code = callback.data.split(":")[1]
    region = REGIONS.get(code)

    if not region:
        await callback.answer("Ошибка выбора региона")
        return

    db.update_region(
        telegram_id=callback.from_user.id,
        region=region
    )

    await callback.answer("Регион сохранён")

    await callback.message.answer(
        f"📍 Выбран регион: {region}\n"
        "Теперь вы будете автоматически получать оповещения МЧС.",
        reply_markup=ReplyKeyboardRemove()
    )

@user_router.message(Command("stats"))
async def show_stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        logger.warning(
        f"Попытка несанкционированного доступа к статистике: "
        f"telegram_id={message.from_user.id}"
        )
        
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет прав для просмотра статистики.")
        return
    total = db.count_users()
    status_data = db.count_by_status()

    safe = status_data.get("safe", 0)
    help_ = status_data.get("help", 0)
    no_response = total - safe - help_

    await message.answer(
        "📊 Статистика системы оповещения:\n\n"
        f"👥 Всего зарегистрировано: {total}\n"
        f"✅ В безопасности: {safe}\n"
        f"🆘 Нужна помощь: {help_}\n"
        f"❓ Не ответили: {no_response}\n\n"
    )

@user_router.message()
async def unknown_message(message: Message):
    await message.answer(
        "Команда не распознана. Используйте команду /start."
    )
