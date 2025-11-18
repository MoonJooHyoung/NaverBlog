"""
이미지 자동 수집 및 처리 모듈
"""
import os
import logging
import requests
from typing import List, Optional, Dict
from PIL import Image
from io import BytesIO
from pathlib import Path

logger = logging.getLogger(__name__)

# 상수 정의
DEFAULT_IMAGE_WIDTH = 800
DEFAULT_IMAGE_HEIGHT = 600
IMAGE_QUALITY = 85
REQUEST_TIMEOUT = 10
CONTENT_LENGTH_PER_IMAGE = 300

class ImageHandler:
    """이미지 수집 및 처리"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.image_config = config.get("image", {})
        self.cache_dir = Path("images_cache")
        self.cache_dir.mkdir(exist_ok=True)
    
    def collect_and_process_images(self, topic: str, content_length: int) -> List[str]:
        """이미지 수집 및 처리"""
        if not self.image_config.get("auto_collect", True):
            return []
        
        max_images = self.image_config.get("max_images_per_post", 5)
        images = []
        
        try:
            # Unsplash API를 사용한 이미지 검색
            # 다양한 이미지 소스 활용 가능
            image_count = min(max_images, content_length // CONTENT_LENGTH_PER_IMAGE)
            for i in range(image_count):
                image_url = self._search_image(topic, i)
                if image_url:
                    processed_image = self._download_and_process(image_url, topic, i)
                    if processed_image:
                        images.append(processed_image)
        except Exception as e:
            logger.error(f"이미지 수집 오류: {e}")
        
        return images
    
    def _search_image(self, topic: str, index: int) -> Optional[str]:
        """이미지 검색 (Unsplash 사용)"""
        try:
            # 다양한 이미지 API 활용 가능
            # 현재는 Unsplash 사용
            safe_topic = topic.replace(' ', ',')
            unsplash_url = f"https://source.unsplash.com/800x600/?{safe_topic}"
            return unsplash_url
        except Exception as e:
            logger.debug(f"이미지 검색 중 오류 (무시됨): {e}")
            return None
    
    def _download_and_process(self, image_url: str, topic: str, index: int) -> Optional[str]:
        """이미지 다운로드 및 처리"""
        try:
            response = requests.get(image_url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                logger.warning(f"이미지 다운로드 실패 (상태 코드: {response.status_code})")
                return None
            
            # 이미지 로드
            img = Image.open(BytesIO(response.content))
            
            # 최적화 설정
            if self.image_config.get("image_optimization", True):
                width = self.image_config.get("resize_width", DEFAULT_IMAGE_WIDTH)
                height = self.image_config.get("resize_height", DEFAULT_IMAGE_HEIGHT)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # 저장 (파일명 정리)
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_topic = safe_topic.replace(' ', '_')[:20]  # 파일명 길이 제한
            filename = f"{safe_topic}_{index}.jpg"
            filepath = self.cache_dir / filename
            img.save(filepath, "JPEG", quality=IMAGE_QUALITY, optimize=True)
            
            logger.info(f"이미지 저장: {filepath}")
            return str(filepath)
            
        except requests.RequestException as e:
            logger.error(f"이미지 다운로드 오류: {e}")
            return None
        except Exception as e:
            logger.error(f"이미지 처리 오류: {e}")
            return None

