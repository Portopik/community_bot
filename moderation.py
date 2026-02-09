from datetime import datetime, timedelta
from config import MODERATION, RANKS

class ModerationSystem:
    def __init__(self, db, bot):
        self.db = db
        self.bot = bot
        self.sticker_count = {}
    
    async def check_sticker_spam(self, user_id: int, chat_id: int) -> bool:
        """Проверяет спам стикерами"""
        now = datetime.now()
        
        if user_id not in self.sticker_count:
            self.sticker_count[user_id] = []
        
        # Добавляем текущее время
        self.sticker_count[user_id].append(now)
        
        # Очищаем старые записи (старше 1 минуты)
        self.sticker_count[user_id] = [
            time for time in self.sticker_count[user_id]
            if now - time < timedelta(minutes=1)
        ]
        
        # Проверяем лимит
        if len(self.sticker_count[user_id]) > MODERATION["max_stickers_per_minute"]:
            await self.warn_user(
                moderator_id=self.bot.id,
                target_id=user_id,
                chat_id=chat_id,
                reason="Спам стикерами"
            )
            return True
        
        return False
    
    async def mute_user(self, moderator_id: int, target_id: int, 
                       chat_id: int, duration: int, reason: str = "") -> dict:
        """Мутит пользователя"""
        moderator_data = self.db.get_user(moderator_id)
        target_data = self.db.get_user(target_id)
        
        # Проверка прав
        if not self.has_mute_permission(moderator_data["rank"], duration):
            return {"success": False, "message": "Недостаточно прав"}
        
        try:
            # Устанавливаем права
            until_date = datetime.now() + timedelta(seconds=duration)
            
            await self.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=target_id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False
                ),
                until_date=until_date
            )
            
            # Логируем действие
            self.db.add_log(
                action="mute",
                moderator_id=moderator_id,
                target_id=target_id,
                reason=reason
            )
            
            # Обновляем статистику
            target_data["moderation"]["mutes"] += 1
            self.db.save_user(target_id, target_data)
            
            return {"success": True, "duration": duration}
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def warn_user(self, moderator_id: int, target_id: int, 
                       chat_id: int, reason: str = "") -> dict:
        """Выдает предупреждение"""
        moderator_data = self.db.get_user(moderator_id)
        target_data = self.db.get_user(target_id)
        
        # Проверка прав
        if not self.has_warn_permission(moderator_data["rank"]):
            return {"success": False, "message": "Недостаточно прав"}
        
        # Проверка дневного лимита
        if self.get_daily_warns(moderator_id) >= 2:
            return {"success": False, "message": "Достигнут дневной лимит варнов"}
        
        # Добавляем варн
        target_data["moderation"]["warns"] += 1
        target_data["moderation"]["last_warn"] = datetime.now().isoformat()
        
        # Проверяем бан
        if target_data["moderation"]["warns"] >= MODERATION["warns_before_ban"]:
            await self.ban_user(
                moderator_id=moderator_id,
                target_id=target_id,
                chat_id=chat_id,
                duration=86400,  # 1 день
                reason="Слишком много предупреждений"
            )
        
        self.db.save_user(target_id, target_data)
        self.db.add_log("warn", moderator_id, target_id, reason)
        
        return {"success": True, "warns": target_data["moderation"]["warns"]}
    
    async def ban_user(self, moderator_id: int, target_id: int, 
                      chat_id: int, duration: int, reason: str = "") -> dict:
        """Банит пользователя"""
        moderator_data = self.db.get_user(moderator_id)
        
        # Проверка прав
        if not self.has_ban_permission(moderator_data["rank"], duration):
            return {"success": False, "message": "Недостаточно прав"}
        
        try:
            until_date = datetime.now() + timedelta(seconds=duration)
            
            await self.bot.ban_chat_member(
                chat_id=chat_id,
                user_id=target_id,
                until_date=until_date
            )
            
            self.db.add_log("ban", moderator_id, target_id, reason)
            
            return {"success": True, "duration": duration}
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def has_mute_permission(self, rank: int, duration: int) -> bool:
        """Проверяет право на мут"""
        if rank <= 3:
            return duration <= MODERATION["mute_durations"]["low"]
        elif rank <= 7:
            return duration <= MODERATION["mute_durations"]["medium"]
        else:
            return duration <= MODERATION["mute_durations"]["high"]
    
    def has_warn_permission(self, rank: int) -> bool:
        """Проверяет право на варн"""
        return rank >= 4
    
    def has_ban_permission(self, rank: int, duration: int) -> bool:
        """Проверяет право на бан"""
        return rank >= 8 and duration <= 2592000  # 30 дней
    
    def get_daily_warns(self, moderator_id: int) -> int:
        """Получает количество варнов за сегодня"""
        # Реализуйте логику подсчета варнов за день
        return 0
