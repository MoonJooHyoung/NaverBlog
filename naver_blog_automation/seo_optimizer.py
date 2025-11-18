"""
SEO 최적화 모듈
"""
import logging
import re
from typing import List, Dict
from openai import OpenAI

logger = logging.getLogger(__name__)

# 상수 정의
MAX_TITLE_LENGTH = 30
MAX_DESCRIPTION_LENGTH = 150
MIN_KEYWORD_LENGTH = 2
MAX_KEYWORDS = 10

class SEOOptimizer:
    """SEO 최적화 처리"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.seo_config = config.get("seo", {})
        openai_config = config.get("openai", {})
        self.client = OpenAI(api_key=openai_config.get("api_key", ""))
        self.model = openai_config.get("model", "gpt-4")
    
    def optimize_title(self, topic: str, content: str) -> str:
        """제목 SEO 최적화"""
        if not self.seo_config.get("auto_optimize_title", True):
            return topic
        
        try:
            # 키워드 추출
            keywords = self._extract_keywords(content)
            main_keyword = keywords[0] if keywords else topic
            
            # SEO 최적화된 제목 생성
            prompt = f"""다음 주제와 내용을 바탕으로 네이버 블로그에 최적화된 제목을 만들어주세요.

주제: {topic}
주요 키워드: {main_keyword}

요구사항:
1. 30자 이내
2. 검색 최적화
3. 클릭을 유도하는 제목
4. 자연스러운 문장

제목만 출력:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 SEO 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=50
            )
            
            title = response.choices[0].message.content.strip()
            return title[:MAX_TITLE_LENGTH]
            
        except Exception as e:
            logger.error(f"제목 최적화 오류: {e}")
            return topic
    
    def generate_tags(self, topic: str, content: str) -> List[str]:
        """태그 자동 생성"""
        try:
            tag_count = self.seo_config.get("auto_tags_count", 10)
            
            prompt = f"""다음 블로그 포스팅의 주제와 내용을 바탕으로 검색 최적화된 태그를 {tag_count}개 생성해주세요.

주제: {topic}
내용 요약: {content[:500]}

태그만 쉼표로 구분하여 출력:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 SEO 태그 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=100
            )
            
            tags_text = response.choices[0].message.content.strip()
            tags = [tag.strip() for tag in tags_text.split(',')]
            return tags[:tag_count]
            
        except Exception as e:
            logger.error(f"태그 생성 오류: {e}")
            return [topic]
    
    def generate_description(self, content: str) -> str:
        """설명(요약) 자동 생성"""
        if not self.seo_config.get("auto_generate_description", True):
            return ""
        
        try:
            prompt = f"""다음 블로그 포스팅의 내용을 바탕으로 150자 이내의 요약 설명을 작성해주세요.

내용: {content[:1000]}

요약 설명만 출력:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 콘텐츠 요약 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=100
            )
            
            description = response.choices[0].message.content.strip()
            return description[:MAX_DESCRIPTION_LENGTH]
            
        except Exception as e:
            logger.error(f"설명 생성 오류: {e}")
            return content[:MAX_DESCRIPTION_LENGTH]
    
    def _extract_keywords(self, content: str) -> List[str]:
        """키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 방법 사용 가능)
        words = re.findall(r'\b[가-힣]{2,}\b', content)
        word_freq: Dict[str, int] = {}
        for word in words:
            if len(word) >= MIN_KEYWORD_LENGTH:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 빈도순 정렬
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:MAX_KEYWORDS]]

