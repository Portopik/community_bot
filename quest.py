from datetime import datetime
from config import QUESTS_BY_RANK

class QuestSystem:
    def __init__(self, db):
        self.db = db
    
    def get_available_quests(self, user_id: int) -> list:
        """Получает доступные квесты для пользователя"""
        user_data = self.db.get_user(user_id)
        rank = user_data["rank"]
        
        available_quests = []
        
        # Определяем группу квестов по рангу
        if rank <= 3:
            quest_groups = ["1-3"]
        elif rank <= 7:
            quest_groups = ["1-3", "4-7"]
        else:
            quest_groups = ["1-3", "4-7", "7-9"]
        
        # Собираем все доступные квесты
        for group in quest_groups:
            available_quests.extend(QUESTS_BY_RANK[group])
        
        # Убираем уже выполненные
        completed = user_data.get("quests_completed", [])
        available_quests = [q for q in available_quests if q not in completed]
        
        return available_quests
    
    def check_quest_completion(self, user_id: int, quest_name: str) -> bool:
        """Проверяет выполнение квеста"""
        user_data = self.db.get_user(user_id)
        
        # Логика проверки для каждого квеста
        if quest_name == "Общительный 💬":
            # ТОП-3 по сообщениям за день
            # Нужно реализовать получение статистики за день
            pass
        
        elif quest_name == "Оценщик ❤️":
            # Отправить 3 ❤️ другим
            return user_data["reactions_given"]["heart"]["count"] >= 3
        
        elif quest_name == "Послушатель 😇":
            # Не получать наказаний за день
            # Проверяем логи модерации
            pass
        
        # ... остальные квесты
        
        return False
    
    def complete_quest(self, user_id: int, quest_name: str) -> dict:
        """Завершает квест и награждает пользователя"""
        if not self.check_quest_completion(user_id, quest_name):
            return {"success": False, "message": "Квест не выполнен"}
        
        user_data = self.db.get_user(user_id)
        
        # Награда за квест
        xp_reward = 50  # Пример награды
        
        user_data["xp"] += xp_reward
        if "quests_completed" not in user_data:
            user_data["quests_completed"] = []
        user_data["quests_completed"].append(quest_name)
        
        # Проверяем повышение ранга
        user_data = RankSystem.update_rank(user_data)
        
        self.db.save_user(user_id, user_data)
        
        return {
            "success": True,
            "xp_reward": xp_reward,
            "quest": quest_name
        }
