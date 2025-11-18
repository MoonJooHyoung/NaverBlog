"""
위젯 및 버튼 관리 모듈
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class WidgetManager:
    """위젯 및 버튼 자동 삽입"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.posting_config = config.get("posting", {})
    
    def add_widgets(self, content: str) -> str:
        """위젯 및 버튼 추가"""
        if not self.posting_config.get("auto_widgets", True):
            return content
        
        try:
            # 소셜 공유 버튼
            content = self._add_social_share_buttons(content)
            
            # 언론사 배지
            content = self._add_media_badge(content)
            
            return content
            
        except Exception as e:
            logger.error(f"위젯 추가 오류: {e}")
            return content
    
    def _add_social_share_buttons(self, content: str) -> str:
        """소셜 공유 버튼 추가"""
        buttons_html = """
<div style="text-align: center; margin: 20px 0;">
    <a href="#" style="display: inline-block; margin: 5px; padding: 10px 20px; background: #03C75A; color: white; text-decoration: none; border-radius: 5px;">네이버 공유</a>
    <a href="#" style="display: inline-block; margin: 5px; padding: 10px 20px; background: #1877F2; color: white; text-decoration: none; border-radius: 5px;">페이스북 공유</a>
    <a href="#" style="display: inline-block; margin: 5px; padding: 10px 20px; background: #1DA1F2; color: white; text-decoration: none; border-radius: 5px;">트위터 공유</a>
</div>
"""
        return content + "\n\n" + buttons_html
    
    def _add_media_badge(self, content: str) -> str:
        """언론사 배지 추가"""
        badge_html = """
<div style="text-align: center; margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 10px;">
    <p style="margin: 0; font-size: 14px; color: #666;">📰 언론 보도 자료</p>
</div>
"""
        return content + "\n\n" + badge_html

