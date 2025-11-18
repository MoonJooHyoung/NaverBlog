"""
AI 원고 자동 생성 모듈
"""
import logging
from typing import List, Optional, Dict
from openai import OpenAI
import re

logger = logging.getLogger(__name__)

# 상수 정의
DEFAULT_TOPIC = "일상 이야기"
MIN_PARAGRAPH_LENGTH_FOR_SUBHEADING = 100
SUBHEADING_INTERVAL = 2
MAX_HASHTAGS = 5

class ContentGenerator:
    """콘텐츠 자동 생성"""
    
    def __init__(self, config: Dict):
        self.config = config
        openai_config = config.get("openai", {})
        self.client = OpenAI(api_key=openai_config.get("api_key", ""))
        self.model = openai_config.get("model", "gpt-4")
        self.temperature = openai_config.get("temperature", 0.7)
        self.max_tokens = openai_config.get("max_tokens", 2000)
    
    def generate_topic(self) -> str:
        """주제 자동 생성"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 네이버 블로그 인기 주제를 생성하는 전문가입니다."},
                    {"role": "user", "content": "네이버 블로그에서 인기 있을 만한 주제 하나를 제시해주세요. 주제만 간단히 말해주세요."}
                ],
                temperature=self.temperature,
                max_tokens=50
            )
            topic = response.choices[0].message.content.strip()
            return topic
        except Exception as e:
            logger.error(f"주제 생성 오류: {e}")
            return DEFAULT_TOPIC
    
    def generate_content(self, topic: str) -> str:
        """주제 기반 원고 생성"""
        try:
            prompt = f"""다음 주제에 대해 네이버 블로그 포스팅을 작성해주세요.

주제: {topic}

요구사항:
1. 읽기 쉽고 자연스러운 문체
2. 1000-1500자 정도의 분량
3. 적절한 문단 구분
4. 실용적이고 유용한 정보 포함
5. 마크다운 형식 사용 가능

포스팅 내용:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 전문 블로그 작가입니다. 읽기 쉽고 유용한 블로그 포스팅을 작성합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"원고 생성 완료 (길이: {len(content)}자)")
            return content
            
        except Exception as e:
            logger.error(f"원고 생성 오류: {e}")
            return f"{topic}에 대한 포스팅 내용입니다."
    
    def add_subheadings(self, content: str) -> str:
        """부제목 자동 삽입"""
        # 문단을 분석하여 적절한 위치에 H2, H3 태그 추가
        paragraphs = content.split('\n\n')
        result: List[str] = []
        
        for i, para in enumerate(paragraphs):
            if (len(para) > MIN_PARAGRAPH_LENGTH_FOR_SUBHEADING 
                and i > 0 
                and i % SUBHEADING_INTERVAL == 0):
                # 긴 문단 앞에 부제목 추가
                first_sentence = para[:30].strip()
                if not para.startswith('##'):
                    result.append(f"## {first_sentence}...")
            result.append(para)
        
        return '\n\n'.join(result)
    
    def add_table_of_contents(self, content: str) -> str:
        """목차 자동 생성"""
        # H2 태그 찾기
        h2_pattern = r'##\s+(.+)'
        headings = re.findall(h2_pattern, content)
        
        if len(headings) >= 2:
            toc = "## 목차\n\n"
            for i, heading in enumerate(headings, 1):
                toc += f"{i}. {heading}\n"
            toc += "\n---\n\n"
            return toc + content
        
        return content
    
    def add_hashtags(self, content: str, tags: List[str]) -> str:
        """해시태그 추가"""
        hashtags = "\n\n" + " ".join([f"#{tag}" for tag in tags[:MAX_HASHTAGS]])
        return content + hashtags

