import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class Database:
    def __init__(self):
        self.data_dir = "data"
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.stats_file = os.path.join(self.data_dir, "stats.json")
        self.logs_file = os.path.join(self.data_dir, "logs.json")
        self._ensure_directories()
        self._init_files()
    
    def _ensure_directories(self):
        """Создает директории если их нет"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _init_files(self):
        """Инициализирует JSON файлы"""
        for file_path in [self.users_file, self.stats_file, self.logs_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Получает данные пользователя"""
        with open(self.users_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if str(user_id) not in data:
            return self._create_default_user(user_id)
        
        return data[str(user_id)]
    
    def _create_default_user(self, user_id: int) -> Dict[str, Any]:
        """Создает пользователя по умолчанию"""
        user_data = {
            "user_id": user_id,
            "username": "",
            "first_name": "",
            "last_name": "",
            "xp": 0,
            "rank": 1,
            "messages_count": 0,
            "reactions_given": {
                "heart": {"count": 0, "last_date": None},
                "thumbs_up": {"count": 0, "last_date": None},
                "nerd": {"count": 0, "last_date": None}
            },
            "reactions_received": {"heart": 0, "thumbs_up": 0, "nerd": 0},
            "quests_completed": [],
            "daily_stats": {
                "messages": 0,
                "reactions_given": {"heart": 0, "thumbs_up": 0, "nerd": 0}
            },
            "moderation": {
                "warns": 0,
                "mutes": 0,
                "bans": 0,
                "last_warn": None
            },
            "join_date": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }
        
        self.save_user(user_id, user_data)
        return user_data
    
    def save_user(self, user_id: int, user_data: Dict[str, Any]):
        """Сохраняет данные пользователя"""
        with open(self.users_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data[str(user_id)] = user_data
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_log(self, action: str, moderator_id: int, target_id: int, reason: str = ""):
        """Добавляет лог модерации"""
        with open(self.logs_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        log_id = str(len(logs) + 1)
        logs[log_id] = {
            "action": action,
            "moderator_id": moderator_id,
            "target_id": target_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.logs_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def get_top_users(self, limit: int = 10) -> list:
        """Получает топ пользователей по XP"""
        with open(self.users_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        users = list(data.values())
        users.sort(key=lambda x: x.get('xp', 0), reverse=True)
        return users[:limit]
    
    def reset_daily_stats(self):
        """Сбрасывает ежедневную статистику"""
        with open(self.users_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for user_id, user_data in data.items():
            user_data["daily_stats"] = {
                "messages": 0,
                "reactions_given": {"heart": 0, "thumbs_up": 0, "nerd": 0}
            }
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
