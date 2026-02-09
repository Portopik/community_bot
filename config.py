import os
from dotenv import load_dotenv

load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
DEVELOPER_ID = int(os.getenv('DEVELOPER_ID', 0))  # Ваш ID в Telegram

# Настройки рангов
RANKS = {
    1: {"name": "Луркер", "emoji": "🕶️", "xp_required": 0, "symbols": "?"},
    2: {"name": "Ньюфаг", "emoji": "🐣", "xp_required": 50, "symbols": "??"},
    3: {"name": "Контактёр", "emoji": "📡", "xp_required": 150, "symbols": "???"},
    4: {"name": "Мемолог", "emoji": "🎭", "xp_required": 300, "symbols": "????"},
    5: {"name": "Гуру", "emoji": "🧠", "xp_required": 500, "symbols": "?????"},
    6: {"name": "Криэйтор", "emoji": "✨", "xp_required": 800, "symbols": "??????"},
    7: {"name": "Модератор", "emoji": "⚖️", "xp_required": 1200, "symbols": "???????"},
    8: {"name": "Интегратор", "emoji": "🔗", "xp_required": 1700, "symbols": "????????"},
    9: {"name": "Легенда", "emoji": "🏆", "xp_required": 2300, "symbols": "?????????"},
    10: {"name": "Разработчик", "emoji": "👨‍💻", "xp_required": 999999, "symbols": "⭐"}
}

# Настройки опыта
EXPERIENCE_CONFIG = {
    "heart": {"xp": 1, "daily_limit": 10, "cooldown": 60, "min_rank": 1},
    "thumbs_up": {"xp": 5, "daily_limit": 2, "cooldown": 300, "min_rank": 3},
    "nerd": {"xp": 10, "daily_limit": 1, "cooldown": 0, "min_rank": 7}
}

# Настройки модерации
MODERATION = {
    "max_stickers_per_minute": 5,
    "warns_before_ban": 3,
    "mute_durations": {
        "low": 300,      # 5 минут
        "medium": 1800,  # 30 минут
        "high": 604800   # 7 дней
    }
}

# Настройки заданий
QUESTS_BY_RANK = {
    "1-3": ["Общительный 💬", "Оценщик ❤️", "Послушатель 😇"],
    "4-7": ["Добряк 👍", "Надзиратель ⚠️"],
    "7-9": ["Мудрец 🤓", "Контент-мейкер 🎨", "Лидер сообщества 👑"]
}
