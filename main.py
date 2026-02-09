#!/usr/bin/env python3
import os
import asyncio
import logging
from datetime import datetime, timedelta

from telegram import Update, ChatPermissions
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не установлен!")
    exit(1)

# База данных в памяти (для примера, позже замените на JSON)
users_db = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Сохраняем пользователя
    if user.id not in users_db:
        users_db[user.id] = {
            'id': user.id,
            'username': user.username or '',
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'xp': 0,
            'rank': 1,
            'messages': 0,
            'join_date': datetime.now().isoformat()
        }
    
    welcome_text = f"""
👋 Привет, {user.first_name}!

Я — бот для управления сообществом.

✨ <b>Доступные команды:</b>
/profile — Ваш профиль
/id — Ваш ID
/rules — Правила
/help — Помощь

🆔 <b>Ваш ID:</b> <code>{user.id}</code>
    """.strip()
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='HTML',
        disable_web_page_preview=True
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /profile"""
    user = update.effective_user
    
    if user.id not in users_db:
        await update.message.reply_text(
            "Сначала используйте /start для регистрации!",
            parse_mode='HTML'
        )
        return
    
    user_data = users_db[user.id]
    
    profile_text = f"""
👤 <b>ПРОФИЛЬ</b>

<b>Имя:</b> {user_data['first_name']} {user_data['last_name']}
<b>Username:</b> @{user_data['username'] or 'не установлен'}
<b>ID:</b> <code>{user.id}</code>

<b>Ранг:</b> Луркер 🕶️
<b>Опыт:</b> {user_data['xp']} XP
<b>Сообщений:</b> {user_data['messages']}

<b>В сообществе с:</b> {user_data['join_date'][:10]}
    """.strip()
    
    await update.message.reply_text(profile_text, parse_mode='HTML')

async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /id"""
    user = update.effective_user
    chat = update.effective_chat
    
    id_text = f"""
🆔 <b>ИНФОРМАЦИЯ ОБ ID</b>

<b>Ваш ID:</b> <code>{user.id}</code>
<b>Username:</b> @{user.username or 'не установлен'}
<b>Имя:</b> {user.first_name or ''}

<b>ID чата:</b> <code>{chat.id}</code>
<b>Тип чата:</b> {chat.type}
    """.strip()
    
    await update.message.reply_text(id_text, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
🆘 <b>ПОМОЩЬ ПО КОМАНДАМ</b>

<b>Основные команды:</b>
/start — Начать работу с ботом
/profile — Ваш профиль
/id — Показать ID
/top — Топ игроков
/rules — Правила сообщества

<b>Для модераторов:</b>
/mute — Замутить пользователя
/warn — Выдать предупреждение
/ban — Забанить пользователя

<b>Система рангов:</b>
1. Луркер 🕶️ (0 XP)
2. Ньюфаг 🐣 (50 XP)
3. Контактёр 📡 (150 XP)
... и так далее до Легенды 🏆
    """.strip()
    
    await update.message.reply_text(help_text, parse_mode='HTML')

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /rules"""
    rules_text = """
📜 <b>ПРАВИЛА СООБЩЕСТВА</b>

1. Уважайте друг друга
2. Не спамьте
3. Не нарушайте законы
4. Следуйте указаниям модераторов
5. Помогайте новичкам

За нарушения выдаются:
1. Предупреждение ⚠️
2. Мут 🔇
3. Бан 🚫
    """.strip()
    
    await update.message.reply_text(rules_text, parse_mode='HTML')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик обычных сообщений"""
    user = update.effective_user
    
    # Регистрируем пользователя если его нет
    if user.id not in users_db:
        users_db[user.id] = {
            'id': user.id,
            'username': user.username or '',
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'xp': 0,
            'rank': 1,
            'messages': 0,
            'join_date': datetime.now().isoformat()
        }
    
    # Увеличиваем счетчик сообщений
    users_db[user.id]['messages'] += 1
    users_db[user.id]['xp'] += 1  # 1 XP за сообщение
    
    # Логируем (для отладки)
    logger.info(f"Сообщение от {user.username or user.id}: {update.message.text[:50]}...")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    if update:
        try:
            await update.message.reply_text(
                "⚠️ Произошла ошибка. Разработчик уведомлен.",
                parse_mode='HTML'
            )
        except:
            pass

def main():
    """Основная функция запуска бота"""
    print("=== ЗАПУСК БОТА ===")
    print(f"Токен: {'Установлен' if BOT_TOKEN else 'НЕ УСТАНОВЛЕН!'}")
    
    if not BOT_TOKEN:
        print("ОШИБКА: BOT_TOKEN не найден в переменных окружения!")
        print("Добавьте его в настройках bothost.ru")
        exit(1)
    
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("id", show_id))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rules", rules))
    
    # Обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик ошибок
    app.add_error_handler(error_handler)
    
    print("Бот запускается...")
    print("Для остановки нажмите Ctrl+C")
    
    # Запускаем бота
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
