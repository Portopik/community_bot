from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class KeyboardManager:
    @staticmethod
    def get_main_menu() -> InlineKeyboardMarkup:
        """Основное меню"""
        keyboard = [
            [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
            [InlineKeyboardButton("🎯 Задания", callback_data="quests")],
            [InlineKeyboardButton("🏆 Топ игроков", callback_data="top")],
            [InlineKeyboardButton("📜 Правила", callback_data="rules")],
            [InlineKeyboardButton("🛠️ Модерация", callback_data="moderation")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_join_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура для присоединения"""
        keyboard = [[
            InlineKeyboardButton(
                "✅ Присоединиться к сообществу", 
                callback_data="join_community"
            )
        ]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_moderation_menu(rank: int) -> InlineKeyboardMarkup:
        """Меню модерации в зависимости от ранга"""
        keyboard = []
        
        if rank >= 1:
            keyboard.append([
                InlineKeyboardButton("🔇 Мут 5 мин", callback_data="mute_5min"),
                InlineKeyboardButton("🆘 Помощь админа", callback_data="help_admin")
            ])
        
        if rank >= 4:
            keyboard.append([
                InlineKeyboardButton("⚠️ Варн", callback_data="warn"),
                InlineKeyboardButton("🔇 Мут 30 мин", callback_data="mute_30min")
            ])
        
        if rank >= 8:
            keyboard.append([
                InlineKeyboardButton("🚫 Бан", callback_data="ban"),
                InlineKeyboardButton("🔇 Мут 7 дней", callback_data="mute_7days")
            ])
            keyboard.append([
                InlineKeyboardButton("🔄 Амнистия", callback_data="amnesty"),
                InlineKeyboardButton("📊 Статистика", callback_data="mod_stats")
            ])
        
        keyboard.append([InlineKeyboardButton("↩️ Назад", callback_data="main_menu")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_reaction_keyboard(target_id: int) -> InlineKeyboardMarkup:
        """Клавиатура реакций"""
        keyboard = [
            [
                InlineKeyboardButton("❤️ +1 XP", callback_data=f"react_heart_{target_id}"),
                InlineKeyboardButton("👍 +5 XP", callback_data=f"react_thumbs_{target_id}"),
                InlineKeyboardButton("🤓 +10 XP", callback_data=f"react_nerd_{target_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
