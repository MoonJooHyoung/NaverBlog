"""
포스팅 히스토리 관리 모듈
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class PostHistory:
    """포스팅 히스토리 관리"""
    
    def __init__(self, history_file: str = "post_history.json"):
        self.history_file = Path(history_file)
        self.history: List[Dict] = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """히스토리 로드"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"히스토리 로드 실패: {e}")
        return []
    
    def _save_history(self):
        """히스토리 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"히스토리 저장 실패: {e}")
    
    def add_post(self, title: str, url: Optional[str] = None, 
                 topic: Optional[str] = None, success: bool = True,
                 error: Optional[str] = None) -> Dict:
        """포스팅 추가"""
        post_data = {
            "title": title,
            "url": url,
            "topic": topic,
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.history.append(post_data)
        self._save_history()
        
        if success:
            logger.info(f"포스팅 히스토리 추가: {title}")
        else:
            logger.warning(f"실패한 포스팅 기록: {title}")
        
        return post_data
    
    def get_recent_posts(self, limit: int = 10) -> List[Dict]:
        """최근 포스팅 조회"""
        return self.history[-limit:] if len(self.history) > limit else self.history
    
    def get_today_posts(self) -> List[Dict]:
        """오늘 포스팅 조회"""
        today = datetime.now().strftime("%Y-%m-%d")
        return [post for post in self.history if post.get("date") == today]
    
    def get_failed_posts(self) -> List[Dict]:
        """실패한 포스팅 조회"""
        return [post for post in self.history if not post.get("success", True)]
    
    def get_statistics(self) -> Dict:
        """통계 정보"""
        total = len(self.history)
        successful = len([p for p in self.history if p.get("success", True)])
        failed = total - successful
        today_posts = len(self.get_today_posts())
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "today": today_posts,
            "success_rate": (successful / total * 100) if total > 0 else 0
        }
    
    def check_duplicate(self, title: str, days: int = 7) -> bool:
        """중복 포스팅 확인"""
        from datetime import timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        for post in self.history:
            if post.get("title") == title and post.get("date", "") >= cutoff_date:
                return True
        return False

