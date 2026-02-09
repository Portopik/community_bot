import html
from datetime import datetime
from config import RANKS

class Utils:
    @staticmethod
    def escape_html(text: str) -> str:
        """Экранирует HTML символы"""
        return html.escape(text)
    
    @staticmethod
    def format_time(seconds: int) -> str:
        """Форматирует время в читаемый вид"""
        if seconds < 60:
            return f"{seconds} сек"
        elif seconds < 3600:
            return f"{seconds // 60} мин"
        elif seconds < 86400:
            return f"{seconds // 3600} час"
        else:
            return f"{seconds // 86400} дней"
    
    @staticmethod
    def create_profile_card(user_data: dict) -> str:
        """Создает карточку профиля"""
        rank_info = RankSystem.get_rank_info(user_data["xp"])
        
        card = f"""
{rank_info['symbols']} <b>{user_data.get('first_name', '')} {user_data.get('last_name', '')}</b>
@{user_data.get('username', 'Без username')}

<b>Ранг:</b> {rank_info['current_name']}
<b>Опыт:</b> {user_data['xp']} XP
<b>Прогресс:</b> {rank_info['progress']:.1f}% до {rank_info['next_name']}

<b>Сообщений:</b> {user_data['messages_count']}
<b>Реакций получено:</b> ❤️{user_data['reactions_received']['heart']} 👍{user_data['reactions_received']['thumbs_up']} 🤓{user_data['reactions_received']['nerd']}

<b>Дата присоединения:</b> {user_data['join_date'][:10]}
        """.strip()
        
        return card
    
    @staticmethod
    def create_top_users_list(top_users: list) -> str:
        """Создает список топ пользователей"""
        if not top_users:
            return "Пока нет статистики"
        
        top_text = "🏆 <b>ТОП-10 ИГРОКОВ</b>\n\n"
        
        for i, user in enumerate(top_users[:10], 1):
            rank_info = RankSystem.get_rank_info(user["xp"])
            username = user.get("username", "Без username")
            name = user.get("first_name", "")
            
            top_text += f"{i}. {rank_info['symbols']} <b>{name}</b> (@{username})\n"
            top_text += f"   ⭐ {user['xp']} XP | 📨 {user['messages_count']} сообщ.\n\n"
        
        return top_text
