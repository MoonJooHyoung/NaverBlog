"""
네이버 블로그 자동화 메인 클래스
"""
import time
import logging
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .login import NaverLogin
from .content_generator import ContentGenerator
from .image_handler import ImageHandler
from .seo_optimizer import SEOOptimizer
from .link_manager import LinkManager
from .widget_manager import WidgetManager
from .poster import BlogPoster
from .scheduler import PostScheduler
from .post_history import PostHistory

logger = logging.getLogger(__name__)

# 상수 정의
DEFAULT_WAIT_TIME = 10
DEFAULT_DELAY = 2

class NaverBlogAutomation:
    """네이버 블로그 자동화 메인 클래스"""
    
    def __init__(self, config: Dict):
        """
        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.driver = None
        self.login_manager = None
        self.content_generator = None
        self.image_handler = None
        self.seo_optimizer = None
        self.link_manager = None
        self.widget_manager = None
        self.poster = None
        self.scheduler = None
        self.post_history = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """컴포넌트 초기화"""
        logger.info("컴포넌트 초기화 중...")
        
        # 브라우저 드라이버 설정
        self._setup_driver()
        
        # 각 모듈 초기화
        self.login_manager = NaverLogin(self.driver, self.config)
        self.content_generator = ContentGenerator(self.config)
        self.image_handler = ImageHandler(self.config)
        self.seo_optimizer = SEOOptimizer(self.config)
        self.link_manager = LinkManager(self.config)
        self.widget_manager = WidgetManager(self.config)
        self.poster = BlogPoster(self.driver, self.config)
        self.scheduler = PostScheduler(self.config)
        self.post_history = PostHistory()
        
        logger.info("✅ 컴포넌트 초기화 완료")
    
    def _setup_driver(self):
        """Selenium 드라이버 설정"""
        options = webdriver.ChromeOptions()
        advanced_config = self.config.get("advanced", {})
        
        if advanced_config.get("headless_mode", False):
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent 설정 (더 완전한 User-Agent)
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        options.add_argument(f"user-agent={user_agent}")
        
        # 추가 보안 설정
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            logger.info("Chrome 드라이버 초기화 완료")
        except Exception as e:
            logger.error(f"드라이버 초기화 실패: {e}")
            raise
    
    def login(self) -> bool:
        """네이버 로그인"""
        return self.login_manager.login()
    
    def run_automation(self):
        """자동화 작업 실행"""
        logger.info("자동화 작업 시작")
        
        # 스케줄러가 활성화되어 있으면 스케줄러 실행
        if self.config.get("scheduler", {}).get("enabled", False):
            logger.info("스케줄러 모드로 실행")
            self.scheduler.start(self._post_single_article)
        else:
            # 즉시 포스팅
            self._post_single_article()
    
    def _post_single_article(self, topic: Optional[str] = None):
        """단일 포스팅 생성 및 업로드"""
        try:
            logger.info("=" * 50)
            logger.info("새 포스팅 생성 시작")
            logger.info("=" * 50)
            
            # 1. 원고 생성
            if not topic:
                topic = self.content_generator.generate_topic()
            
            logger.info(f"주제: {topic}")
            content = self.content_generator.generate_content(topic)
            
            # 2. SEO 최적화
            optimized_title = self.seo_optimizer.optimize_title(topic, content)
            tags = self.seo_optimizer.generate_tags(topic, content)
            description = self.seo_optimizer.generate_description(content)
            
            logger.info(f"최적화된 제목: {optimized_title}")
            logger.info(f"태그: {', '.join(tags)}")
            
            # 3. 이미지 처리
            images = self.image_handler.collect_and_process_images(topic, len(content))
            
            # 4. 콘텐츠 가공
            # - 부제목 자동 삽입
            content = self.content_generator.add_subheadings(content)
            # - 목차 생성
            content = self.content_generator.add_table_of_contents(content)
            # - 해시태그 삽입
            content = self.content_generator.add_hashtags(content, tags)
            
            # 5. 내부 링크 삽입
            content = self.link_manager.insert_internal_links(content)
            
            # 6. 위젯/버튼 추가
            content = self.widget_manager.add_widgets(content)
            
            # 7. 포스팅 업로드
            posting_config = self.config.get("posting", {})
            success, post_url = self.poster.post(
                title=optimized_title,
                content=content,
                images=images,
                tags=tags,
                description=description,
                category=posting_config.get("default_category", "일반"),
                is_public=posting_config.get("is_public", True),
                allow_comments=posting_config.get("allow_comments", True),
                scheduled_time=posting_config.get("scheduled_time"),
                thumbnail_image=posting_config.get("thumbnail_image")
            )
            
            # 8. 히스토리 저장
            self.post_history.add_post(
                title=optimized_title,
                url=post_url,
                topic=topic,
                success=success,
                error=None if success else "포스팅 실패"
            )
            
            if success:
                logger.info("✅ 포스팅 성공!")
                if post_url:
                    logger.info(f"포스팅 URL: {post_url}")
            else:
                logger.error("❌ 포스팅 실패")
                
        except Exception as e:
            logger.error(f"포스팅 중 오류 발생: {e}", exc_info=True)
    
    def close(self):
        """리소스 정리"""
        if self.driver:
            self.driver.quit()
        logger.info("브라우저 종료")

