from config import RANKS

class RankSystem:
    @staticmethod
    def get_rank_info(xp: int) -> dict:
        """Получает информацию о ранге на основе XP"""
        current_rank = 1
        next_rank = 2
        
        for rank, info in RANKS.items():
            if xp >= info["xp_required"]:
                current_rank = rank
                if rank < len(RANKS):
                    next_rank = rank + 1
        
        current_info = RANKS[current_rank]
        next_info = RANKS.get(next_rank, current_info)
        
        xp_for_current = xp - current_info["xp_required"]
        xp_for_next = next_info["xp_required"] - current_info["xp_required"]
        progress = (xp_for_current / xp_for_next * 100) if xp_for_next > 0 else 100
        
        return {
            "current_rank": current_rank,
            "current_name": f"{current_info['symbols']} {current_info['name']} {current_info['emoji']}",
            "next_rank": next_rank,
            "next_name": f"{next_info['symbols']} {next_info['name']} {next_info['emoji']}",
            "xp_current": xp,
            "xp_required_current": current_info["xp_required"],
            "xp_required_next": next_info["xp_required"],
            "progress": min(progress, 100),
            "symbols": current_info["symbols"]
        }
    
    @staticmethod
    def check_rank_up(user_data: dict) -> bool:
        """Проверяет, нужно ли повысить ранг"""
        current_rank = user_data.get("rank", 1)
        xp = user_data.get("xp", 0)
        
        if current_rank < len(RANKS):
            next_rank_xp = RANKS[current_rank + 1]["xp_required"]
            if xp >= next_rank_xp:
                return True
        return False
    
    @staticmethod
    def update_rank(user_data: dict) -> dict:
        """Обновляет ранг пользователя"""
        if RankSystem.check_rank_up(user_data):
            user_data["rank"] = min(user_data["rank"] + 1, len(RANKS))
        return user_data
