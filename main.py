import asyncio
from datetime import datetime, timedelta
from telegram import Update, ChatPermissions
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.error import BadRequest

from config import BOT_TOKEN, DEVELOPER_ID
from database import Database
from ranks import RankSystem
from experience import ExperienceSystem
from quests import QuestSystem
from moderation import ModerationSystem
from keyboard import KeyboardManager
from utils import Utils

class CommunityBot:
    def __init__(self):
        self.db = Database()
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.exp_system = ExperienceSystem(self.db)
        self.quest_system = QuestSystem(self.db)
        self.keyboard_manager = KeyboardManager()
        self.utils = Utils()
        self.mod_system = None  # Инициализируем после создания бота
        
        # Регистрируем обработчики
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрирует все обработчики"""
        # Команды
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("profile", self.profile_command))
        self.app.add_handler(CommandHandler("top", self.top_command))
        self.app.add_handler(CommandHandler("quests", self.quests_command))
        self.app.add_handler(CommandHandler("rules", self.rules_command))
        
        # Команды модерации
        self.app.add_handler(CommandHandler("mute", self.mute_command))
        self.app.add_handler(CommandHandler("warn", self.warn_command))
        self.app.add_handler(CommandHandler("ban", self.ban_command))
        self.app.add_handler(CommandHandler("helpadmin", self.helpadmin_command))
        self.app.add_handler(CommandHandler("amnestiay", self.amnesty_command))
        
        # Обработчики сообщений
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(MessageHandler(filters.Sticker.ALL, self.handle_sticker))
        
        # Обработчики callback запросов
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Обработчики ошибок
        self.app.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        chat = update.effective_chat
        
        # Регистрируем пользователя
        user_data = self.db.get_user(user.id)
        
        # Обновляем информацию
        user_data["username"] = user.username or ""
        user_data["first_name"] = user.first_name or ""
        user_data["last_name"] = user.last_name or ""
        self.db.save_user(user.id, user_data)
        
        # Отправляем приветственное сообщение
        welcome_text = f"""
👋 Привет, {user.first_name}!

Добро пожаловать в наше сообщество! 
Я — бот для управления сообществом с системой рангов, опыта и заданий.

<b>Основные возможности:</b>
🏆 Система рангов (9 уровней)
⭐ Система опыта за активность
🎯 Ежедневные задания
⚖️ Система модерации
📊 Статистика и рейтинги

Нажмите кнопку ниже, чтобы присоединиться к сообществу!
        """.strip()
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='HTML',
            reply_markup=self.keyboard_manager.get_join_keyboard()
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user = update.effective_user
        message = update.effective_message
        
        # Проверяем, присоединился ли пользователь
        user_data = self.db.get_user(user.id)
        if "joined" not in user_data:
            await message.reply_text(
                "Сначала присоединитесь к сообществу!",
                reply_markup=self.keyboard_manager.get_join_keyboard()
            )
            return
        
        # Начисляем опыт за сообщение
        result = self.exp_system.add_message_xp(user.id)
        
        # Проверяем повышение ранга
        if result["rank_up"]:
            rank_info = RankSystem.get_rank_info(user_data["xp"])
            await message.reply_text(
                f"🎉 Поздравляем! {user.first_name} повысил ранг до "
                f"{rank_info['current_name']}!",
                parse_mode='HTML'
            )
        
        # Проверяем выполнение квестов
        available_quests = self.quest_system.get_available_quests(user.id)
        for quest in available_quests:
            if self.quest_system.check_quest_completion(user.id, quest):
                result = self.quest_system.complete_quest(user.id, quest)
                if result["success"]:
                    await message.reply_text(
                        f"🎯 {user.first_name} выполнил задание: {quest}\n"
                        f"Награда: +{result['xp_reward']} XP",
                        parse_mode='HTML'
                    )
    
    async def handle_sticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик стикеров"""
        user = update.effective_user
        chat = update.effective_chat
        message = update.effective_message
        
        # Проверяем спам стикерами
        if self.mod_system:
            is_spam = await self.mod_system.check_sticker_spam(user.id, chat.id)
            if is_spam:
                await message.delete()
                await message.reply_text(
                    f"⚠️ {user.first_name}, слишком много стикеров! Получено предупреждение."
                )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback запросов"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user = query.from_user
        
        if data == "join_community":
            # Присоединение к сообществу
            user_data = self.db.get_user(user.id)
            user_data["joined"] = True
            user_data["join_date"] = datetime.now().isoformat()
            self.db.save_user(user.id, user_data)
            
            await query.edit_message_text(
                f"✅ {user.first_name}, вы успешно присоединились к сообществу!\n"
                f"Ваш текущий ранг: Луркер 🕶️\n\n"
                f"Используйте /help для списка команд.",
                parse_mode='HTML',
                reply_markup=self.keyboard_manager.get_main_menu()
            )
        
        elif data == "profile":
            user_data = self.db.get_user(user.id)
            profile_card = self.utils.create_profile_card(user_data)
            await query.edit_message_text(
                profile_card,
                parse_mode='HTML',
                reply_markup=self.keyboard_manager.get_main_menu()
            )
        
        elif data == "top":
            top_users = self.db.get_top_users(10)
            top_list = self.utils.create_top_users_list(top_users)
            await query.edit_message_text(
                top_list,
                parse_mode='HTML',
                reply_markup=self.keyboard_manager.get_main_menu()
            )
        
        elif data.startswith("react_"):
            # Обработка реакций
            parts = data.split("_")
            if len(parts) == 3:
                react_type = parts[1]
                target_id = int(parts[2])
                
                result = self.exp_system.give_reaction(user.id, target_id, react_type)
                
                if result["success"]:
                    await query.edit_message_text(
                        f"✅ Вы отправили реакцию!\n"
                        f"Пользователь получил +{result['xp_gain']} XP",
                        parse_mode='HTML'
                    )
                else:
                    await query.edit_message_text(
                        f"❌ {result['message']}",
                        parse_mode='HTML'
                    )
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /profile"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        profile_card = self.utils.create_profile_card(user_data)
        
        await update.message.reply_text(
            profile_card,
            parse_mode='HTML',
            reply_markup=self.keyboard_manager.get_main_menu()
        )
    
    async def top_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /top"""
        top_users = self.db.get_top_users(10)
        top_list = self.utils.create_top_users_list(top_users)
        
        await update.message.reply_text(
            top_list,
            parse_mode='HTML',
            reply_markup=self.keyboard_manager.get_main_menu()
        )
    
    async def mute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /mute"""
        if not self.mod_system:
            self.mod_system = ModerationSystem(self.db, self.app.bot)
        
        # Логика команды mute
        # ... реализация
    
    async def warn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /warn"""
        if not self.mod_system:
            self.mod_system = ModerationSystem(self.db, self.app.bot)
        
        # Логика команды warn
        # ... реализация
    
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /ban"""
        if not self.mod_system:
            self.mod_system = ModerationSystem(self.db, self.app.bot)
        
        # Логика команды ban
        # ... реализация
    
    async def helpadmin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /helpadmin"""
        # Уведомление админов
        # ... реализация
    
    async def amnesty_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /amnestiay"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        if user_data["rank"] >= 8 or user.id == DEVELOPER_ID:
            # Логика амнистии
            # ... реализация
            pass
    
    async def rules_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /rules"""
        rules_text = """
📜 <b>ПРАВИЛА СООБЩЕСТВА</b>

1. Уважайте друг друга
2. Не спамьте
3. Не нарушайте законы
4. Следуйте указаниям модераторов

Полный список правил: ссылка_на_правила
        """.strip()
        
        await update.message.reply_text(rules_text, parse_mode='HTML')
    
    async def quests_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /quests"""
        user = update.effective_user
        available_quests = self.quest_system.get_available_quests(user.id)
        
        if not available_quests:
            quests_text = "🎯 У вас пока нет доступных заданий."
        else:
            quests_text = "🎯 <b>ДОСТУПНЫЕ ЗАДАНИЯ</b>\n\n"
            for i, quest in enumerate(available_quests, 1):
                quests_text += f"{i}. {quest}\n"
        
        await update.message.reply_text(quests_text, parse_mode='HTML')
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        print(f"Ошибка: {context.error}")
    
    def run(self):
        """Запускает бота"""
        print("Бот запущен...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

async def daily_reset_task(app: Application):
    """Ежедневный сброс статистики"""
    while True:
        now = datetime.now()
        # Сброс в 00:00
        target_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now > target_time:
            target_time += timedelta(days=1)
        
        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        
        # Сбрасываем статистику
        db = Database()
        db.reset_daily_stats()
        print(f"Ежедневный сброс выполнен: {datetime.now()}")

if __name__ == "__main__":
    bot = CommunityBot()
    
    # Запускаем задачу ежедневного сброса
    loop = asyncio.get_event_loop()
    loop.create_task(daily_reset_task(bot.app))
    
    bot.run()
