"""
설정 검증 모듈
"""
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigValidator:
    """설정 파일 검증"""
    
    @staticmethod
    def validate(config: Dict) -> tuple[bool, List[str]]:
        """
        설정 검증
        
        Returns:
            (is_valid, errors): 유효성 여부와 에러 메시지 리스트
        """
        errors: List[str] = []
        
        # 네이버 설정 검증
        if "naver" not in config:
            errors.append("'naver' 설정이 없습니다")
        else:
            naver = config["naver"]
            if not naver.get("id"):
                errors.append("네이버 ID가 설정되지 않았습니다")
            if not naver.get("password"):
                errors.append("네이버 비밀번호가 설정되지 않았습니다")
            if not naver.get("blog_url"):
                errors.append("블로그 URL이 설정되지 않았습니다")
            elif not naver["blog_url"].startswith("https://blog.naver.com/"):
                errors.append("블로그 URL 형식이 올바르지 않습니다 (https://blog.naver.com/로 시작해야 함)")
        
        # OpenAI 설정 검증
        if "openai" not in config:
            errors.append("'openai' 설정이 없습니다")
        else:
            openai = config["openai"]
            if not openai.get("api_key"):
                errors.append("OpenAI API 키가 설정되지 않았습니다")
            if openai.get("model") not in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]:
                logger.warning(f"알 수 없는 모델: {openai.get('model')}")
        
        # 포스팅 설정 검증
        if "posting" in config:
            posting = config["posting"]
            if posting.get("max_posts_per_day", 0) < 0:
                errors.append("max_posts_per_day는 0 이상이어야 합니다")
            if posting.get("posting_interval_minutes", 0) < 0:
                errors.append("posting_interval_minutes는 0 이상이어야 합니다")
        
        # 이미지 설정 검증
        if "image" in config:
            image = config["image"]
            if image.get("max_images_per_post", 0) < 0:
                errors.append("max_images_per_post는 0 이상이어야 합니다")
            if image.get("resize_width", 0) < 0 or image.get("resize_height", 0) < 0:
                errors.append("이미지 크기는 0보다 커야 합니다")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_and_log(config: Dict) -> bool:
        """설정 검증 및 로깅"""
        is_valid, errors = ConfigValidator.validate(config)
        
        if not is_valid:
            logger.error("설정 검증 실패:")
            for error in errors:
                logger.error(f"  - {error}")
        else:
            logger.info("✅ 설정 검증 완료")
        
        return is_valid

