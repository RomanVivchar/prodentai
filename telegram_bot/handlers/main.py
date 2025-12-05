"""
Main handlers for Telegram Bot
"""

from typing import Optional

import httpx
from config import Config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user

    # Register user in backend
    async with httpx.AsyncClient() as client:
        try:
            api_endpoints = Config.get_api_endpoints()
            response = await client.post(
                f"{api_endpoints['auth']}/register",
                json={
                    "telegram_id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            )
            user_data = response.json()
        except Exception as e:
            print(f"Error registering user: {e}")
            user_data = {"id": user.id}

    # Clear all states when returning to main menu
    context.user_data.pop("psychology_chat_active", None)
    # context.user_data.pop('waiting_for_food', None)  # Закомментировано - анализ питания отключен
    # context.user_data.pop('waiting_for_photo', None)  # Закомментировано - анализ питания отключен

    # Create main menu
    keyboard = [
        # [InlineKeyboardButton("🍎 Анализ питания", callback_data="nutrition")],  # Закомментировано - анализ питания отключен
        [InlineKeyboardButton("⏰ Напоминания", callback_data="reminders")],
        [InlineKeyboardButton("💡 Факт о гигиене", callback_data="fact")],
        [
            InlineKeyboardButton(
                "💬 Психологическая поддержка", callback_data="psychology"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = f"""
🦷 Добро пожаловать в ProDentAI, {user.first_name}!

Я ваш персональный ИИ-компаньон для поддержания стоматологического здоровья.

Выберите действие:
"""

    # Handle both message and callback query
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text, reply_markup=reply_markup
        )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🦷 *ProDentAI - Помощник по стоматологическому здоровью*

*📋 Доступные команды:*

/start - Открыть главное меню
/menu - Открыть главное меню
# /nutrition - Анализ питания  # Закомментировано - анализ питания отключен
/psychology - Психологическая поддержка
/reminders - Настройка напоминаний
/fact - Случайный факт о гигиене
/help - Эта справка

*📖 Как пользоваться ботом:*

# 1️⃣ *Анализ питания* 🍎  # Закомментировано - анализ питания отключен
#    • Выберите "📝 Описать еду" и напишите, что вы съели
#    • Или выберите "📸 Анализ фото" и отправьте фото еды
#    • Бот проанализирует влияние на здоровье зубов

1️⃣ *Психологическая поддержка* 💬
   • Выберите "💬 Начать диалог" для общения с ИИ
   • Или "💡 Советы" для получения полезных рекомендаций
   • Поможет справиться с тревогой перед визитом к стоматологу

2️⃣ *Напоминания* ⏰
   • Добавьте напоминания о гигиене
   • Настройте время уведомлений
   • Управляйте активными напоминаниями

3️⃣ *Факты о гигиене* 💡
   • Получайте интересные факты о стоматологии
   • Нажмите "💡 Еще факт" для нового факта

*💡 Совет:* Используйте кнопки меню для удобной навигации. Все функции доступны через главное меню!

*🔗 Сайт:* [ProDentAI](https://your-domain.com)
"""

    keyboard = [
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Handle both message and callback query
    if update.message:
        await update.message.reply_text(
            help_text, reply_markup=reply_markup, parse_mode="Markdown"
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            help_text, reply_markup=reply_markup, parse_mode="Markdown"
        )


# Закомментировано - анализ питания отключен
# async def nutrition_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle /nutrition command"""
#     keyboard = [
#         [InlineKeyboardButton("📝 Описать еду", callback_data="describe_food")],
#         [InlineKeyboardButton("📸 Анализ фото", callback_data="photo_analysis")],
#         [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#
#     text = """
# 🍎 Анализ питания
#
# Выберите способ анализа:
# • Описать еду текстом
# • Отправить фото еды
# """
#
#     # Handle both message and callback query
#     if update.message:
#         await update.message.reply_text(text, reply_markup=reply_markup)
#     elif update.callback_query:
#         await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


async def psychology_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /psychology command"""
    keyboard = [
        [InlineKeyboardButton("💬 Начать диалог", callback_data="start_psychology")],
        [InlineKeyboardButton("💡 Советы", callback_data="psychology_tips")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = """
💬 Психологическая поддержка

Я помогу вам справиться с тревогой перед визитом к стоматологу.

Выберите действие:
• Начать диалог
• Получить советы
"""

    # Handle both message and callback query
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


async def reminders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reminders command"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить напоминание", callback_data="add_reminder")],
        [InlineKeyboardButton("📋 Мои напоминания", callback_data="my_reminders")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = """
⏰ Напоминания о гигиене

Настройте напоминания для формирования здоровых привычек:
• Добавить новое напоминание
• Посмотреть мои напоминания
"""

    # Handle both message and callback query
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


async def facts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /fact command"""
    # Category translations
    category_translations = {
        "hygiene": "Гигиена",
        "history": "История",
        "nutrition": "Питание",
        "technology": "Технологии",
        "health": "Здоровье",
        "science": "Наука",
        "tips": "Советы",
        "myths": "Мифы",
    }

    # Get random fact from backend
    async with httpx.AsyncClient() as client:
        try:
            api_endpoints = Config.get_api_endpoints()
            response = await client.get(f"{api_endpoints['facts']}/random")
            fact_data = response.json()

            category = fact_data.get("category", "")
            category_ru = category_translations.get(category, category)

            text = f"""
💡 {fact_data['title']}

{fact_data['content']}

Категория: {category_ru}
"""
        except Exception as e:
            print(f"Error fetching fact: {e}")
            text = """
💡 Интересный факт о гигиене

Первая зубная щетка была изобретена в Китае в 1498 году и была сделана из щетины кабана.

Категория: История
"""

    keyboard = [
        [InlineKeyboardButton("💡 Еще факт", callback_data="fact")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Handle both message and callback query
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


async def get_user_id_from_telegram(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[int]:
    """Get user ID from backend by telegram_id"""
    user = update.effective_user
    if not user:
        return None

    async with httpx.AsyncClient() as client:
        try:
            api_endpoints = Config.get_api_endpoints()
            # Try to get user by telegram_id
            response = await client.post(
                f"{api_endpoints['auth']}/register",
                json={
                    "telegram_id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            )
            if response.status_code == 200:
                user_data = response.json()
                return user_data.get("id")
        except Exception as e:
            print(f"Error getting user ID: {e}")
    return None


# Закомментировано - анализ питания отключен
# async def describe_food_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle food description request"""
#     # Clear other states when entering nutrition analysis
#     context.user_data.pop('psychology_chat_active', None)
#     context.user_data.pop('waiting_for_photo', None)
#
#     text = """📝 Описать еду
#
# Напишите, что вы съели или планируете съесть, и я проанализирую влияние на здоровье ваших зубов.
#
# Пример: "Я съел яблоко и выпил кофе с сахаром"
#
# Просто отправьте описание еды текстом."""
#
#     keyboard = [
#         [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#
#     await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
#
#     # Store state for food description
#     context.user_data['waiting_for_food'] = True


# Закомментировано - анализ питания отключен
# async def photo_analysis_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle photo analysis request"""
#     # Clear other states when entering nutrition analysis
#     context.user_data.pop('psychology_chat_active', None)
#     context.user_data.pop('waiting_for_food', None)
#
#     text = """📸 Анализ фото еды
#
# Отправьте фото еды, и я проанализирую её влияние на здоровье зубов.
#
# Просто отправьте фото как обычное сообщение."""
#
#     keyboard = [
#         [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#
#     await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
#
#     # Store state for photo
#     context.user_data['waiting_for_photo'] = True


async def start_psychology_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start psychology chat"""
    # Clear other states when entering psychology chat
    # context.user_data.pop('waiting_for_food', None)  # Закомментировано - анализ питания отключен
    # context.user_data.pop('waiting_for_photo', None)  # Закомментировано - анализ питания отключен

    text = """💬 Психологическая поддержка

Я здесь, чтобы помочь вам справиться с тревогой перед визитом к стоматологу.

Просто напишите мне о ваших переживаниях, страхах или вопросах, и я поддержу вас.

Например:
• "Я боюсь идти к стоматологу"
• "Что делать, если будет больно?"
• "Как справиться с тревогой?"

Напишите ваше сообщение текстом."""

    keyboard = [
        [InlineKeyboardButton("💡 Советы", callback_data="psychology_tips")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

    # Store state for psychology chat
    context.user_data["psychology_chat_active"] = True


async def psychology_tips_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle psychology tips request"""
    async with httpx.AsyncClient() as client:
        try:
            api_endpoints = Config.get_api_endpoints()
            response = await client.get(f"{api_endpoints['psychology']}/tips")
            if response.status_code == 200:
                data = response.json()
                tips = data.get("tips", [])
                text = "💡 Советы по снижению тревоги\n\n"
                for tip in tips:
                    text += f"• {tip.get('title', '')}\n"
                    text += f"  {tip.get('content', '')}\n\n"
            else:
                text = "💡 Советы по снижению тревоги\n\n"
                text += "• Дышите глубоко и медленно\n"
                text += "• Слушайте музыку во время процедуры\n"
                text += "• Общайтесь с врачом о своих страхах\n"
                text += "• Начните с простого осмотра"
        except Exception as e:
            print(f"Error in psychology tips: {e}")
            text = "💡 Советы по снижению тревоги\n\n"
            text += "• Дышите глубоко и медленно\n"
            text += "• Слушайте музыку во время процедуры\n"
            text += "• Общайтесь с врачом о своих страхах"

    keyboard = [
        [InlineKeyboardButton("💬 Начать диалог", callback_data="start_psychology")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


async def add_reminder_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add reminder request"""
    text = """➕ *Добавить напоминание*

Выберите тип напоминания:

🌅 *Утренняя гигиена*
   Напоминание о чистке зубов утром

🌙 *Вечерняя гигиена*
   Напоминание о чистке зубов вечером

🦷 *Визит к стоматологу*
   Напоминание о запланированном визите

🧵 *Использование зубной нити*
   Напоминание о чистке межзубных промежутков"""

    keyboard = [
        [InlineKeyboardButton("🌅 Утренняя гигиена", callback_data="reminder_morning")],
        [InlineKeyboardButton("🌙 Вечерняя гигиена", callback_data="reminder_evening")],
        [
            InlineKeyboardButton(
                "🦷 Визит к стоматологу", callback_data="reminder_dental"
            )
        ],
        [InlineKeyboardButton("🧵 Зубная нить", callback_data="reminder_floss")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode="MarkdownV2"
    )


async def my_reminders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle my reminders request"""
    user_id = await get_user_id_from_telegram(update, context)
    if not user_id:
        await update.callback_query.edit_message_text(
            "Ошибка: не удалось определить пользователя. Попробуйте /start"
        )
        return

    # Map reminder types to emojis and names
    reminder_type_map = {
        "morning_hygiene": ("🌅", "Утренняя гигиена"),
        "evening_hygiene": ("🌙", "Вечерняя гигиена"),
        "dental_visit": ("🦷", "Визит к стоматологу"),
        "floss": ("🧵", "Использование зубной нити"),
    }

    async with httpx.AsyncClient() as client:
        try:
            api_endpoints = Config.get_api_endpoints()
            response = await client.get(f"{api_endpoints['reminders']}/user/{user_id}")
            if response.status_code == 200:
                reminders = response.json()
                if reminders:
                    text = "📋 *Мои напоминания*\n\n"
                    for i, reminder in enumerate(reminders, 1):
                        status = "✅" if reminder.get("is_active") else "❌"
                        reminder_type = reminder.get("reminder_type", "")
                        time_str = reminder.get("time", "")
                        message = reminder.get("message", "")

                        # Get emoji and name for reminder type
                        emoji, name = reminder_type_map.get(
                            reminder_type, ("⏰", reminder_type)
                        )

                        # Escape name for MarkdownV2
                        name_escaped = (
                            name.replace("_", "\\_")
                            .replace("*", "\\*")
                            .replace("[", "\\[")
                            .replace("]", "\\]")
                            .replace("(", "\\(")
                            .replace(")", "\\)")
                            .replace("~", "\\~")
                            .replace("`", "\\`")
                            .replace(">", "\\>")
                            .replace("#", "\\#")
                            .replace("+", "\\+")
                            .replace("-", "\\-")
                            .replace("=", "\\=")
                            .replace("|", "\\|")
                            .replace("{", "\\{")
                            .replace("}", "\\}")
                            .replace(".", "\\.")
                            .replace("!", "\\!")
                        )

                        text += f"{i}\\. {status} *{name_escaped}* {emoji}\n"
                        text += f"   🕐 Время: {time_str}\n"
                        if reminder.get("date"):
                            date_str = reminder.get("date", "")
                            # Format date for display (MarkdownV2 requires escaping dots)
                            try:
                                from datetime import datetime

                                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                                formatted_date = date_obj.strftime("%d.%m.%Y")
                                # Escape dots for MarkdownV2
                                formatted_date_escaped = formatted_date.replace(
                                    ".", "\\."
                                )
                                text += f"   📅 Дата: {formatted_date_escaped}\n"
                            except:
                                # Escape dots for MarkdownV2
                                date_str_escaped = date_str.replace(".", "\\.")
                                text += f"   📅 Дата: {date_str_escaped}\n"
                        if message:
                            # Escape special characters for MarkdownV2
                            message_escaped = (
                                message.replace("_", "\\_")
                                .replace("*", "\\*")
                                .replace("[", "\\[")
                                .replace("]", "\\]")
                                .replace("(", "\\(")
                                .replace(")", "\\)")
                                .replace("~", "\\~")
                                .replace("`", "\\`")
                                .replace(">", "\\>")
                                .replace("#", "\\#")
                                .replace("+", "\\+")
                                .replace("-", "\\-")
                                .replace("=", "\\=")
                                .replace("|", "\\|")
                                .replace("{", "\\{")
                                .replace("}", "\\}")
                                .replace(".", "\\.")
                                .replace("!", "\\!")
                            )
                            text += f"   💬 {message_escaped}\n"
                        text += "\n"
                else:
                    text = '📋 *Мои напоминания*\n\nУ вас пока нет напоминаний.\n\nНажмите "➕ Добавить", чтобы создать первое напоминание.'
            else:
                text = "❌ Ошибка при получении напоминаний."
        except Exception as e:
            print(f"Error in my reminders: {e}")
            text = "❌ Ошибка при получении напоминаний."

    keyboard = [
        [InlineKeyboardButton("➕ Добавить", callback_data="add_reminder")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode="MarkdownV2"
    )


async def reminder_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle reminder type selection"""
    from datetime import datetime, timedelta

    reminder_type_map = {
        "reminder_morning": ("morning_hygiene", "08:00", "🌅 Утренняя гигиена", None),
        "reminder_evening": ("evening_hygiene", "22:00", "🌙 Вечерняя гигиена", None),
        "reminder_dental": (
            "dental_visit",
            "10:00",
            "🦷 Визит к стоматологу",
            (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        ),
        "reminder_floss": ("floss", "21:00", "🧵 Использование зубной нити", None),
    }

    callback_data = update.callback_query.data
    if callback_data not in reminder_type_map:
        await update.callback_query.answer("Неизвестный тип напоминания")
        return

    reminder_type, default_time, name, default_date = reminder_type_map[callback_data]
    user_id = await get_user_id_from_telegram(update, context)

    if not user_id:
        await update.callback_query.edit_message_text(
            "Ошибка: не удалось определить пользователя. Попробуйте /start"
        )
        return

    # For dental_visit, we need to ask for date, so store state and ask
    if reminder_type == "dental_visit":
        context.user_data["creating_reminder"] = {
            "type": reminder_type,
            "time": default_time,
            "name": name,
        }
        text = f"""📅 *{name}*

Введите дату визита в формате ДД\\.ММ\\.ГГГГ
Например: 15\\.12\\.2024

Или нажмите кнопку для выбора даты:"""

        # Create date selection buttons (next 7 days)
        keyboard = []
        today = datetime.now()
        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime("%d.%m.%Y")
            date_api = date.strftime("%Y-%m-%d")
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"📅 {date_str}", callback_data=f"reminder_date_{date_api}"
                    )
                ]
            )

        keyboard.append(
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode="MarkdownV2"
        )
        return

    # For other types, create immediately
    async with httpx.AsyncClient() as client:
        try:
            api_endpoints = Config.get_api_endpoints()
            response = await client.post(
                f"{api_endpoints['reminders']}/create",
                json={
                    "user_id": user_id,
                    "reminder_type": reminder_type,
                    "time": default_time,
                },
            )
            if response.status_code == 200:
                # Escape name for MarkdownV2
                name_escaped = (
                    name.replace("_", "\\_")
                    .replace("*", "\\*")
                    .replace("[", "\\[")
                    .replace("]", "\\]")
                    .replace("(", "\\(")
                    .replace(")", "\\)")
                    .replace("~", "\\~")
                    .replace("`", "\\`")
                    .replace(">", "\\>")
                    .replace("#", "\\#")
                    .replace("+", "\\+")
                    .replace("-", "\\-")
                    .replace("=", "\\=")
                    .replace("|", "\\|")
                    .replace("{", "\\{")
                    .replace("}", "\\}")
                    .replace(".", "\\.")
                    .replace("!", "\\!")
                )
                text = f"✅ Напоминание *{name_escaped}* создано\\!\n\n🕐 Время: {default_time}\n\nВы будете получать уведомления\\."
            else:
                text = "❌ Ошибка при создании напоминания\\."
        except Exception as e:
            print(f"Error creating reminder: {e}")
            text = "❌ Ошибка при создании напоминания\\."

    keyboard = [
        [InlineKeyboardButton("📋 Мои напоминания", callback_data="my_reminders")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode="MarkdownV2"
    )


async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query

    if not query:
        return

    await query.answer()

    try:
        if query.data == "main_menu":
            await start_handler(update, context)
        elif query.data == "fact":
            await facts_handler(update, context)
        # elif query.data == "nutrition":  # Закомментировано - анализ питания отключен
        #     await nutrition_handler(update, context)
        elif query.data == "psychology":
            await psychology_handler(update, context)
        elif query.data == "reminders":
            await reminders_handler(update, context)
        # Nutrition handlers - закомментировано - анализ питания отключен
        # elif query.data == "describe_food":
        #     await describe_food_handler(update, context)
        # elif query.data == "photo_analysis":
        #     await photo_analysis_handler(update, context)
        # Psychology handlers
        elif query.data == "start_psychology":
            await start_psychology_handler(update, context)
        elif query.data == "psychology_tips":
            await psychology_tips_handler(update, context)
        # Reminders handlers
        elif query.data == "add_reminder":
            await add_reminder_handler(update, context)
        elif query.data == "my_reminders":
            await my_reminders_handler(update, context)
        elif query.data in [
            "reminder_morning",
            "reminder_evening",
            "reminder_dental",
            "reminder_floss",
        ]:
            await reminder_type_handler(update, context)
        elif query.data.startswith("reminder_edit_"):
            # Handle reminder edit
            reminder_id = int(query.data.replace("reminder_edit_", ""))
            await edit_reminder_handler(update, context, reminder_id)
        elif query.data.startswith("reminder_toggle_"):
            # Toggle reminder active status
            reminder_id = int(query.data.replace("reminder_toggle_", ""))
            await toggle_reminder_handler(update, context, reminder_id)
        elif query.data.startswith("reminder_delete_"):
            # Delete reminder
            reminder_id = int(query.data.replace("reminder_delete_", ""))
            await delete_reminder_handler(update, context, reminder_id)
        elif query.data.startswith("reminder_date_"):
            # Handle date selection for dental visit
            date_str = query.data.replace("reminder_date_", "")
            creating_reminder = context.user_data.get("creating_reminder")
            if creating_reminder:
                user_id = await get_user_id_from_telegram(update, context)
                if user_id:
                    async with httpx.AsyncClient() as client:
                        try:
                            api_endpoints = Config.get_api_endpoints()
                            response = await client.post(
                                f"{api_endpoints['reminders']}/create",
                                json={
                                    "user_id": user_id,
                                    "reminder_type": creating_reminder["type"],
                                    "time": creating_reminder["time"],
                                    "date": date_str,
                                },
                            )
                            if response.status_code == 200:
                                # Format date for MarkdownV2 (escape dots)
                                formatted_date = date_str.replace("-", ".")
                                # Escape name for MarkdownV2
                                name_escaped = (
                                    creating_reminder["name"]
                                    .replace("_", "\\_")
                                    .replace("*", "\\*")
                                    .replace("[", "\\[")
                                    .replace("]", "\\]")
                                    .replace("(", "\\(")
                                    .replace(")", "\\)")
                                    .replace("~", "\\~")
                                    .replace("`", "\\`")
                                    .replace(">", "\\>")
                                    .replace("#", "\\#")
                                    .replace("+", "\\+")
                                    .replace("-", "\\-")
                                    .replace("=", "\\=")
                                    .replace("|", "\\|")
                                    .replace("{", "\\{")
                                    .replace("}", "\\}")
                                    .replace(".", "\\.")
                                    .replace("!", "\\!")
                                )
                                text = f"✅ Напоминание *{name_escaped}* создано\\!\n\n📅 Дата: {formatted_date}\n🕐 Время: {creating_reminder['time']}\n\nВы будете получать уведомления\\."
                            else:
                                text = "❌ Ошибка при создании напоминания\\."
                        except Exception as e:
                            print(f"Error creating reminder: {e}")
                            text = "❌ Ошибка при создании напоминания\\."

                    keyboard = [
                        [
                            InlineKeyboardButton(
                                "📋 Мои напоминания", callback_data="my_reminders"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "🔙 Главное меню", callback_data="main_menu"
                            )
                        ],
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.callback_query.edit_message_text(
                        text, reply_markup=reply_markup, parse_mode="MarkdownV2"
                    )
                    context.user_data.pop("creating_reminder", None)
                else:
                    await update.callback_query.answer(
                        "Ошибка: не удалось определить пользователя"
                    )
            else:
                await update.callback_query.answer(
                    "Ошибка: данные напоминания не найдены"
                )
        else:
            await query.edit_message_text("Функция в разработке...")
    except Exception as e:
        print(f"Error handling callback {query.data}: {e}")
        await query.edit_message_text("Произошла ошибка. Попробуйте еще раз.")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    if not update.message or not update.message.text:
        return

    text = update.message.text
    user_id = await get_user_id_from_telegram(update, context)

    try:
        # Check if user is in psychology chat
        if context.user_data.get("psychology_chat_active"):
            if user_id:
                # Show typing indicator
                await update.message.chat.send_action(ChatAction.TYPING)

                async with httpx.AsyncClient() as client:
                    try:
                        api_endpoints = Config.get_api_endpoints()
                        response = await client.post(
                            f"{api_endpoints['psychology']}/chat",
                            json={
                                "user_id": user_id,
                                "message": text,
                                "session_type": "general",
                            },
                        )
                        if response.status_code == 200:
                            data = response.json()
                            ai_response = data.get(
                                "ai_response", "Извините, не могу ответить сейчас."
                            )

                            keyboard = [
                                [
                                    InlineKeyboardButton(
                                        "🔙 Главное меню", callback_data="main_menu"
                                    )
                                ],
                            ]
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            await update.message.reply_text(
                                ai_response, reply_markup=reply_markup
                            )
                        else:
                            await update.message.reply_text(
                                "Ошибка при обработке сообщения. Попробуйте позже."
                            )
                    except Exception as e:
                        print(f"Error in psychology chat: {e}")
                        await update.message.reply_text(
                            "Ошибка при обработке сообщения. Попробуйте позже."
                        )
            else:
                await update.message.reply_text(
                    "Ошибка: не удалось определить пользователя. Попробуйте /start"
                )
            return

        # Закомментировано - анализ питания отключен
        # # Check if user is waiting for food description
        # if context.user_data.get('waiting_for_food'):
        #     if user_id:
        #         # Отправляем сообщение о начале анализа
        #         analyzing_msg = await update.message.reply_text("⏳ Провожу анализ...")
        #
        #         async with httpx.AsyncClient(timeout=120.0) as client:
        #             try:
        #                 api_endpoints = Config.get_api_endpoints()
        #                 response = await client.post(
        #                     f"{api_endpoints['nutrition']}/analyze",
        #                     json={
        #                         "user_id": user_id,
        #                         "food_description": text
        #                     }
        #                 )
        #                 if response.status_code == 200:
        #                     data = response.json()
        #                     analysis = data.get("analysis_result", {})
        #                     recommendations_raw = data.get("recommendations", "")
        #                     summary = data.get("summary", "")
        #
        #                     # Обработка recommendations - может быть строкой или списком
        #                     if isinstance(recommendations_raw, list):
        #                         recommendations = "\n".join([f"• {r}" for r in recommendations_raw])
        #                     elif isinstance(recommendations_raw, str):
        #                         recommendations = recommendations_raw
        #                     else:
        #                         recommendations = ""
        #
        #                     reply_text = f"🍎 Анализ питания\n\n"
        #                     if summary:
        #                         reply_text += f"📝 {summary}\n\n"
        #                     else:
        #                         reply_text += f"📝 Описание: {text}\n\n"
        #
        #                     if data.get("sugar_content") is not None:
        #                         reply_text += f"🍬 Сахар: {data.get('sugar_content', 0):.1f}г\n"
        #                     if data.get("acidity_level") is not None:
        #                         reply_text += f"🧪 Кислотность: {data.get('acidity_level', 7.0):.1f} pH\n"
        #                     if recommendations:
        #                         reply_text += f"\n💡 Рекомендации:\n{recommendations}"
        #
        #                     keyboard = [
        #                         [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
        #                     ]
        #                     reply_markup = InlineKeyboardMarkup(keyboard)
        #                     # Удаляем сообщение "Провожу анализ..." и отправляем результат
        #                     try:
        #                         await analyzing_msg.delete()
        #                     except:
        #                         pass
        #                     await update.message.reply_text(reply_text, reply_markup=reply_markup)
        #                     context.user_data.pop('waiting_for_food', None)
        #                 else:
        #                     # Удаляем сообщение "Провожу анализ..."
        #                     try:
        #                         await analyzing_msg.delete()
        #                     except:
        #                         pass
        #                     error_detail = ""
        #                     try:
        #                         error_data = response.json()
        #                         error_detail = error_data.get("detail", str(response.status_code))
        #                     except:
        #                         error_detail = str(response.status_code)
        #                     await update.message.reply_text(f"Ошибка при анализе (код: {error_detail}). Попробуйте позже.")
        #             except Exception as e:
        #                 print(f"Error in nutrition analysis: {e}")
        #                 import traceback
        #                 traceback.print_exc()
        #                 # Удаляем сообщение "Провожу анализ..."
        #                 try:
        #                     await analyzing_msg.delete()
        #                 except:
        #                     pass
        #                 await update.message.reply_text(f"Ошибка при анализе: {str(e)}\n\nПопробуйте позже.")
        #     else:
        #         await update.message.reply_text("Ошибка: не удалось определить пользователя. Попробуйте /start")
        #     return

        # Simple keyword-based responses
        if any(word in text.lower() for word in ["привет", "hello", "hi"]):
            await update.message.reply_text(
                "Привет! Как дела? Чем могу помочь с вашим стоматологическим здоровьем?"
            )
        elif any(word in text.lower() for word in ["спасибо", "thanks", "thank you"]):
            await update.message.reply_text("Пожалуйста! Рад помочь! 😊")
        else:
            await update.message.reply_text(
                "Не совсем понял. Попробуйте использовать команды или меню!"
            )
    except Exception as e:
        print(f"Error handling message: {e}")
        try:
            await update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")
        except:
            pass


# Закомментировано - анализ питания отключен
# async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle photo messages for nutrition analysis"""
#     if not update.message or not update.message.photo:
#         return
#
#     user_id = await get_user_id_from_telegram(update, context)
#     if not user_id:
#         await update.message.reply_text("Ошибка: не удалось определить пользователя. Попробуйте /start")
#         return
#
#     # Check if user is waiting for photo
#     if not context.user_data.get('waiting_for_photo'):
#         await update.message.reply_text("Для анализа фото выберите '📸 Анализ фото' в меню питания.")
#         return
#
#     # Отправляем сообщение о начале анализа
#     analyzing_msg = await update.message.reply_text("⏳ Провожу анализ фото...")
#
#     # Show typing indicator
#     await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
#
#     # Get the largest photo
#     photo = update.message.photo[-1]
#
#     # Download photo
#     file = await photo.get_file()
#     photo_bytes = await file.download_as_bytearray()
#
#     # Send to backend for analysis
#     async with httpx.AsyncClient(timeout=120.0) as client:
#         try:
#             api_endpoints = Config.get_api_endpoints()
#             # Convert bytearray to bytes for upload
#             files = {"file": ("photo.jpg", bytes(photo_bytes), "image/jpeg")}
#
#             # user_id должен быть в query параметрах, а не в form data
#             response = await client.post(
#                 f"{api_endpoints['nutrition']}/analyze-image?user_id={user_id}",
#                 files=files
#             )
#
#             if response.status_code == 200:
#                 result = response.json()
#                 analysis = result.get("analysis_result", {})
#                 recommendations_raw = result.get("recommendations", "")
#                 summary = result.get("summary", "")
#
#                 # Обработка recommendations - может быть строкой или списком
#                 if isinstance(recommendations_raw, list):
#                     recommendations = "\n".join([f"• {r}" for r in recommendations_raw])
#                 elif isinstance(recommendations_raw, str):
#                     recommendations = recommendations_raw
#                 else:
#                     recommendations = ""
#
#                 reply_text = "🍎 Анализ фото еды\n\n"
#                 if summary:
#                     reply_text += f"📝 {summary}\n\n"
#                 if result.get("sugar_content") is not None:
#                     reply_text += f"🍬 Сахар: {result.get('sugar_content', 0):.1f}г\n"
#                 if result.get("acidity_level") is not None:
#                     reply_text += f"🧪 Кислотность: {result.get('acidity_level', 7.0):.1f} pH\n"
#                 if recommendations:
#                     reply_text += f"\n💡 Рекомендации:\n{recommendations}"
#
#                 keyboard = [
#                     [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
#                 ]
#                 reply_markup = InlineKeyboardMarkup(keyboard)
#                 # Удаляем сообщение "Провожу анализ..." и отправляем результат
#                 try:
#                     await analyzing_msg.delete()
#                 except:
#                     pass
#                 await update.message.reply_text(reply_text, reply_markup=reply_markup)
#                 context.user_data.pop('waiting_for_photo', None)
#             else:
#                 error_detail = ""
#                 try:
#                     error_data = response.json()
#                     error_detail = error_data.get("detail", "")
#                 except:
#                     pass
#
#                 error_msg = "Ошибка при анализе фото. Попробуйте позже."
#                 if error_detail:
#                     error_msg += f"\n\nДетали: {error_detail}"
#
#                 # Удаляем сообщение "Провожу анализ..."
#                 try:
#                     await analyzing_msg.delete()
#                 except:
#                     pass
#
#                 keyboard = [
#                     [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
#                 ]
#                 reply_markup = InlineKeyboardMarkup(keyboard)
#                 await update.message.reply_text(error_msg, reply_markup=reply_markup)
#         except Exception as e:
#             print(f"Error in photo analysis: {e}")
#             import traceback
#             traceback.print_exc()
#
#             # Удаляем сообщение "Провожу анализ..."
#             try:
#                 await analyzing_msg.delete()
#             except:
#                 pass
#
#             error_msg = f"Ошибка при анализе фото: {str(e)}\n\nПопробуйте:\n• Проверить качество фото\n• Убедиться, что фото содержит еду\n• Попробовать позже"
#
#             keyboard = [
#                 [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
#             ]
#             reply_markup = InlineKeyboardMarkup(keyboard)
#             await update.message.reply_text(error_msg, reply_markup=reply_markup)


async def edit_reminder_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, reminder_id: int
):
    """Handle reminder editing"""
    user_id = await get_user_id_from_telegram(update, context)
    if not user_id:
        await update.callback_query.answer("Ошибка: не удалось определить пользователя")
        return

    async with httpx.AsyncClient() as client:
        try:
            api_endpoints = Config.get_api_endpoints()
            response = await client.get(f"{api_endpoints['reminders']}/user/{user_id}")
            if response.status_code == 200:
                reminders = response.json()
                reminder = next(
                    (r for r in reminders if r.get("id") == reminder_id), None
                )

                if reminder:
                    reminder_type_map = {
                        "morning_hygiene": ("🌅", "Утренняя гигиена"),
                        "evening_hygiene": ("🌙", "Вечерняя гигиена"),
                        "dental_visit": ("🦷", "Визит к стоматологу"),
                        "floss": ("🧵", "Использование зубной нити"),
                    }

                    reminder_type = reminder.get("reminder_type", "")
                    emoji, name = reminder_type_map.get(
                        reminder_type, ("⏰", reminder_type)
                    )
                    is_active = reminder.get("is_active", True)
                    time_str = reminder.get("time", "")
                    message = reminder.get("message", "")

                    # Escape for MarkdownV2
                    name_escaped = (
                        name.replace("_", "\\_").replace("*", "\\*").replace(".", "\\.")
                    )
                    message_escaped = (
                        message.replace("_", "\\_")
                        .replace("*", "\\*")
                        .replace(".", "\\.")
                        if message
                        else ""
                    )

                    text = f"⚙️ *Редактирование напоминания*\n\n"
                    text += f"{emoji} *{name_escaped}*\n"
                    text += f"🕐 Время: {time_str}\n"
                    if message_escaped:
                        text += f"💬 Сообщение: {message_escaped}\n"
                    text += f"Статус: {'✅ Активно' if is_active else '❌ Неактивно'}\n"

                    keyboard = [
                        [
                            InlineKeyboardButton(
                                f"{'❌ Отключить' if is_active else '✅ Включить'}",
                                callback_data=f"reminder_toggle_{reminder_id}",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "🗑 Удалить",
                                callback_data=f"reminder_delete_{reminder_id}",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "🔙 Главное меню", callback_data="main_menu"
                            )
                        ],
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.callback_query.edit_message_text(
                        text, reply_markup=reply_markup, parse_mode="MarkdownV2"
                    )
                else:
                    await update.callback_query.answer("Напоминание не найдено")
        except Exception as e:
            print(f"Error editing reminder: {e}")
            await update.callback_query.answer("Ошибка при редактировании")


async def toggle_reminder_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, reminder_id: int
):
    """Toggle reminder active status"""
    user_id = await get_user_id_from_telegram(update, context)
    if not user_id:
        await update.callback_query.answer("Ошибка: не удалось определить пользователя")
        return

    async with httpx.AsyncClient() as client:
        try:
            api_endpoints = Config.get_api_endpoints()
            # Get current reminder status
            response = await client.get(f"{api_endpoints['reminders']}/user/{user_id}")
            if response.status_code == 200:
                reminders = response.json()
                reminder = next(
                    (r for r in reminders if r.get("id") == reminder_id), None
                )

                if reminder:
                    new_status = not reminder.get("is_active", True)
                    toggle_response = await client.put(
                        f"{api_endpoints['reminders']}/{reminder_id}/toggle",
                        json={"is_active": new_status},
                    )

                    if toggle_response.status_code == 200:
                        await update.callback_query.answer(
                            "✅ Напоминание включено"
                            if new_status
                            else "❌ Напоминание отключено"
                        )
                        await edit_reminder_handler(update, context, reminder_id)
                    else:
                        await update.callback_query.answer(
                            "Ошибка при изменении статуса"
                        )
                else:
                    await update.callback_query.answer("Напоминание не найдено")
        except Exception as e:
            print(f"Error toggling reminder: {e}")
            await update.callback_query.answer("Ошибка при изменении статуса")


async def delete_reminder_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, reminder_id: int
):
    """Delete reminder"""
    user_id = await get_user_id_from_telegram(update, context)
    if not user_id:
        await update.callback_query.answer("Ошибка: не удалось определить пользователя")
        return

    async with httpx.AsyncClient() as client:
        try:
            api_endpoints = Config.get_api_endpoints()
            response = await client.delete(
                f"{api_endpoints['reminders']}/{reminder_id}"
            )

            if response.status_code == 200:
                await update.callback_query.answer("✅ Напоминание удалено")
                await my_reminders_handler(update, context)
            else:
                await update.callback_query.answer("Ошибка при удалении")
        except Exception as e:
            print(f"Error deleting reminder: {e}")
            await update.callback_query.answer("Ошибка при удалении")
