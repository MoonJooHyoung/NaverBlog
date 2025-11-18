"""
내부 링크 관리 모듈
"""
import logging
import re
from typing import List, Dict
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# 상수 정의
MAX_RELATED_POSTS = 3
MIN_KEYWORD_OVERLAP = 2
MAX_KEYWORDS_FOR_DB = 10
CONTENT_PREVIEW_LENGTH = 200

class LinkManager:
    """내부 링크 자동 삽입 관리"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.posting_config = config.get("posting", {})
        self.links_db_path = Path("links_database.json")
        self.links_db: Dict = self._load_links_db()
    
    def _load_links_db(self) -> Dict:
        """링크 데이터베이스 로드"""
        if self.links_db_path.exists():
            try:
                with open(self.links_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"링크 DB 로드 실패, 새로 생성합니다: {e}")
        return {"posts": []}
    
    def _save_links_db(self):
        """링크 데이터베이스 저장"""
        try:
            with open(self.links_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.links_db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"링크 DB 저장 오류: {e}")
    
    def insert_internal_links(self, content: str) -> str:
        """내부 링크 자동 삽입"""
        if not self.posting_config.get("auto_internal_links", True):
            return content
        
        try:
            # 기존 포스팅에서 관련 키워드 찾기
            related_posts = self._find_related_posts(content)
            
            if not related_posts:
                return content
            
            # 글 하단에 관련 글 링크 추가
            links_section = "\n\n---\n\n## 관련 글\n\n"
            for post in related_posts[:MAX_RELATED_POSTS]:
                links_section += f"- [{post['title']}]({post['url']})\n"
            
            return content + links_section
            
        except Exception as e:
            logger.error(f"내부 링크 삽입 오류: {e}")
            return content
    
    def _find_related_posts(self, content: str) -> List[Dict]:
        """관련 포스팅 찾기"""
        # 간단한 키워드 매칭 (실제로는 더 정교한 방법 사용)
        content_keywords = set(re.findall(r'\b[가-힣]{2,}\b', content))
        
        related = []
        for post in self.links_db.get("posts", []):
            post_keywords = set(post.get("keywords", []))
            # 키워드 겹치는 정도 계산
            overlap = len(content_keywords & post_keywords)
            if overlap >= MIN_KEYWORD_OVERLAP:
                related.append({
                    "title": post.get("title", ""),
                    "url": post.get("url", ""),
                    "overlap": overlap
                })
        
        # 겹치는 정도로 정렬
        related.sort(key=lambda x: x["overlap"], reverse=True)
        return related
    
    def add_post_to_db(self, title: str, url: str, content: str):
        """새 포스팅을 링크 DB에 추가"""
        keywords = list(set(re.findall(r'\b[가-힣]{2,}\b', content)))[:MAX_KEYWORDS_FOR_DB]
        
        self.links_db["posts"].append({
            "title": title,
            "url": url,
            "keywords": keywords,
            "content_preview": content[:CONTENT_PREVIEW_LENGTH]
        })
        
        self._save_links_db()
        logger.info(f"포스팅을 링크 DB에 추가: {title}")

