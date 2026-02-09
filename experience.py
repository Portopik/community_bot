from datetime import datetime, timedelta
from config import EXPERIENCE_CONFIG

class ExperienceSystem:
    def __init__(self, db):
        self.db = db
    
    def can_give_reaction(self, user_id: int, reaction_type: str) -> dict:
        """Проверяет, можно ли дать реакцию"""
        user_data = self.db.get_user(user_id)
        config = EXPERIENCE_CONFIG[reaction_type]
        
        # Проверка ранга
        if user_data["rank"] < config["min_rank"]:
            return {"can": False, "reason": f"Доступно с {config['min_rank']} ранга"}
        
        # Проверка ежедневного лимита
        daily_count = user_data["daily_stats"]["reactions_given"][reaction_type]
        if daily_count >= config["daily_limit"]:
            return {"can": False, "reason": "Достигнут дневной лимит"}
        
        # Проверка кулдауна
        last_date_str = user_data["reactions_given"][reaction_type]["last_date"]
        if last_date_str and config["cooldown"] > 0:
            last_date = datetime.fromisoformat(last_date_str)
            if datetime.now() - last_date < timedelta(seconds=config["cooldown"]):
                return {"can": False, "reason": "Подождите перед следующей реакцией"}
        
        return {"can": True, "reason": ""}
    
    def give_reaction(self, from_user_id: int, to_user_id: int, reaction_type: str) -> dict:
        """Дает реакцию и начисляет опыт"""
        # Проверка отправителя
        check_result = self.can_give_reaction(from_user_id, reaction_type)
        if not check_result["can"]:
            return {"success": False, "message": check_result["reason"]}
        
        # Получаем данные пользователей
        from_user = self.db.get_user(from_user_id)
        to_user = self.db.get_user(to_user_id)
        
        # Начисляем опыт получателю
        xp_gain = EXPERIENCE_CONFIG[reaction_type]["xp"]
        to_user["xp"] += xp_gain
        to_user["reactions_received"][reaction_type] += 1
        
        # Обновляем статистику отправителя
        from_user["reactions_given"][reaction_type]["count"] += 1
        from_user["reactions_given"][reaction_type]["last_date"] = datetime.now().isoformat()
        from_user["daily_stats"]["reactions_given"][reaction_type] += 1
        
        # Проверяем повышение ранга
        to_user = RankSystem.update_rank(to_user)
        
        # Сохраняем изменения
        self.db.save_user(from_user_id, from_user)
        self.db.save_user(to_user_id, to_user)
        
        return {
            "success": True,
            "xp_gain": xp_gain,
            "from_user": from_user,
            "to_user": to_user
        }
    
    def add_message_xp(self, user_id: int) -> dict:
        """Начисляет опыт за сообщение"""
        user_data = self.db.get_user(user_id)
        
        # Базовый опыт за сообщение
        base_xp = 1
        
        # Бонус за длину сообщения
        user_data["messages_count"] += 1
        user_data["daily_stats"]["messages"] += 1
        user_data["xp"] += base_xp
        user_data["last_active"] = datetime.now().isoformat()
        
        # Проверяем повышение ранга
        user_data = RankSystem.update_rank(user_data)
        
        self.db.save_user(user_id, user_data)
        
        return {
            "xp_gain": base_xp,
            "new_xp": user_data["xp"],
            "rank_up": RankSystem.check_rank_up(user_data)
        }
