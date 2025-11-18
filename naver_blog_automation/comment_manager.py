"""
댓글 자동 답변 모듈
"""
import time
import logging
from typing import List, Optional, Dict, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from openai import OpenAI

from utils.delay_manager import DelayManager

logger = logging.getLogger(__name__)

# 상수 정의
DEFAULT_WAIT_TIME = 10
MAX_RETRIES = 3

class CommentManager:
    """댓글 자동 답변 관리"""
    
    def __init__(self, driver: webdriver.Chrome, config: Dict):
        self.driver = driver
        self.config = config
        naver_config = config.get("naver", {})
        self.blog_url = naver_config.get("blog_url", "")
        
        # OpenAI 설정
        openai_config = config.get("openai", {})
        self.client = OpenAI(api_key=openai_config.get("api_key", ""))
        self.model = openai_config.get("model", "gpt-4")
        self.temperature = openai_config.get("temperature", 0.7)
        
        # 댓글 자동 답변 설정
        comment_config = config.get("comment_auto_reply", {})
        self.enabled = comment_config.get("enabled", False)
        self.reply_tone = comment_config.get("reply_tone", "친절하고 정중한")
        self.max_reply_length = comment_config.get("max_reply_length", 200)
        self.skip_keywords = comment_config.get("skip_keywords", ["광고", "홍보", "스팸"])
        
        # 딜레이 매니저
        advanced_config = config.get("advanced", {})
        base_delay = advanced_config.get("delay_between_actions", 2)
        random_delay = advanced_config.get("random_delay", True)
        self.delay_manager = DelayManager(base_delay=base_delay, random_delay=random_delay)
    
    def get_unreplied_comments(self, post_url: str) -> List[Dict]:
        """답변하지 않은 댓글 목록 가져오기
        
        Args:
            post_url: 포스팅 URL
            
        Returns:
            댓글 정보 리스트 [{"author": "작성자", "content": "댓글 내용", "comment_id": "댓글ID"}]
        """
        if not self.enabled:
            return []
        
        try:
            logger.info(f"댓글 확인 중: {post_url}")
            self.driver.get(post_url)
            self.delay_manager.wait()
            
            # 댓글 영역 로딩 대기
            try:
                WebDriverWait(self.driver, DEFAULT_WAIT_TIME).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".comment_area, .comment-list, [class*='comment']"))
                )
            except TimeoutException:
                logger.debug("댓글 영역을 찾을 수 없습니다")
                return []
            
            comments = []
            
            # 다양한 댓글 선택자 시도
            comment_selectors = [
                (By.CSS_SELECTOR, ".comment_item, .comment-item, [class*='commentItem']"),
                (By.CSS_SELECTOR, ".comment_list li"),
                (By.CSS_SELECTOR, "[data-comment-id]"),
                (By.XPATH, "//div[contains(@class, 'comment')]"),
            ]
            
            comment_elements = []
            for by, selector in comment_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    if elements:
                        comment_elements = elements
                        logger.debug(f"댓글 {len(elements)}개 발견 ({selector})")
                        break
                except:
                    continue
            
            if not comment_elements:
                logger.debug("댓글을 찾을 수 없습니다")
                return []
            
            # 각 댓글 정보 추출
            for idx, comment_elem in enumerate(comment_elements):
                try:
                    # 댓글 작성자
                    author = ""
                    author_selectors = [
                        (By.CSS_SELECTOR, ".comment_author, .author, [class*='author']"),
                        (By.CSS_SELECTOR, ".nickname, .user_name"),
                        (By.XPATH, ".//span[contains(@class, 'author')]"),
                    ]
                    
                    for by, selector in author_selectors:
                        try:
                            author_elem = comment_elem.find_element(by, selector)
                            author = author_elem.text.strip()
                            if author:
                                break
                        except:
                            continue
                    
                    # 댓글 내용
                    content = ""
                    content_selectors = [
                        (By.CSS_SELECTOR, ".comment_text, .comment-content, [class*='content']"),
                        (By.CSS_SELECTOR, ".text, .comment"),
                        (By.XPATH, ".//div[contains(@class, 'text')]"),
                    ]
                    
                    for by, selector in content_selectors:
                        try:
                            content_elem = comment_elem.find_element(by, selector)
                            content = content_elem.text.strip()
                            if content:
                                break
                        except:
                            continue
                    
                    # 댓글 ID (답변 여부 확인용)
                    comment_id = comment_elem.get_attribute("data-comment-id") or f"comment_{idx}"
                    
                    # 답변 여부 확인 (답변이 이미 있는지 체크)
                    has_reply = False
                    reply_selectors = [
                        (By.CSS_SELECTOR, ".reply, .comment-reply, [class*='reply']"),
                        (By.XPATH, ".//div[contains(@class, 'reply')]"),
                    ]
                    
                    for by, selector in reply_selectors:
                        try:
                            reply_elem = comment_elem.find_element(by, selector)
                            if reply_elem and reply_elem.text.strip():
                                has_reply = True
                                break
                        except:
                            continue
                    
                    if author and content and not has_reply:
                        # 스팸 키워드 체크
                        if any(keyword in content for keyword in self.skip_keywords):
                            logger.debug(f"스팸 댓글 건너뛰기: {content[:30]}...")
                            continue
                        
                        comments.append({
                            "author": author,
                            "content": content,
                            "comment_id": comment_id
                        })
                        logger.debug(f"댓글 발견: {author} - {content[:30]}...")
                
                except Exception as e:
                    logger.debug(f"댓글 파싱 오류 (무시됨): {e}")
                    continue
            
            logger.info(f"답변하지 않은 댓글 {len(comments)}개 발견")
            return comments
            
        except Exception as e:
            logger.error(f"댓글 가져오기 오류: {e}")
            return []
    
    def test_reply_generation(self, comment_content: str, post_title: str = "") -> str:
        """답변 생성 테스트 (드라이버 없이 테스트 가능)
        
        Args:
            comment_content: 댓글 내용
            post_title: 포스팅 제목
            
        Returns:
            생성된 답변 내용
        """
        return self.generate_reply(comment_content, post_title)
    
    def generate_reply(self, comment_content: str, post_title: str = "") -> str:
        """AI를 사용하여 댓글 답변 생성
        
        Args:
            comment_content: 댓글 내용
            post_title: 포스팅 제목
            
        Returns:
            생성된 답변 내용
        """
        try:
            prompt = f"""다음 댓글에 대해 {self.reply_tone} 톤으로 답변을 작성해주세요.

포스팅 제목: {post_title if post_title else "블로그 포스팅"}

댓글 내용: {comment_content}

요구사항:
1. {self.reply_tone} 톤으로 작성
2. {self.max_reply_length}자 이내로 간결하게
3. 감사 인사 포함
4. 자연스럽고 진솔한 답변
5. 이모지나 특수문자 최소화

답변:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 블로그 운영자로서 댓글에 친절하고 정중하게 답변하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=300
            )
            
            reply = response.choices[0].message.content.strip()
            logger.info(f"답변 생성 완료: {reply[:50]}...")
            return reply
            
        except Exception as e:
            logger.error(f"답변 생성 오류: {e}")
            return f"감사합니다! 좋은 하루 되세요. 😊"
    
    def reply_to_comment(self, post_url: str, comment_id: str, reply_text: str) -> bool:
        """댓글에 답변 작성
        
        Args:
            post_url: 포스팅 URL
            comment_id: 댓글 ID
            reply_text: 답변 내용
            
        Returns:
            성공 여부
        """
        try:
            logger.info(f"댓글 답변 작성 중: {comment_id}")
            self.driver.get(post_url)
            self.delay_manager.wait()
            
            # 댓글 영역 로딩 대기
            try:
                WebDriverWait(self.driver, DEFAULT_WAIT_TIME).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".comment_area, .comment-list"))
                )
            except TimeoutException:
                logger.warning("댓글 영역을 찾을 수 없습니다")
                return False
            
            # 답변 버튼 찾기
            reply_button_selectors = [
                (By.XPATH, f"//div[@data-comment-id='{comment_id}']//button[contains(text(), '답글')]"),
                (By.XPATH, f"//div[@data-comment-id='{comment_id}']//a[contains(text(), '답글')]"),
                (By.CSS_SELECTOR, f"[data-comment-id='{comment_id}'] .reply-btn, [data-comment-id='{comment_id}'] .reply-button"),
            ]
            
            reply_button = None
            for by, selector in reply_button_selectors:
                try:
                    reply_button = self.driver.find_element(by, selector)
                    if reply_button:
                        break
                except:
                    continue
            
            if not reply_button:
                # 댓글 요소를 찾아서 답변 버튼 클릭 시도
                try:
                    comment_elem = self.driver.find_element(By.CSS_SELECTOR, f"[data-comment-id='{comment_id}']")
                    # 답변 버튼 클릭
                    reply_buttons = comment_elem.find_elements(By.XPATH, ".//button | .//a")
                    for btn in reply_buttons:
                        if "답글" in btn.text or "답변" in btn.text or "reply" in btn.get_attribute("class").lower():
                            reply_button = btn
                            break
                except:
                    pass
            
            if reply_button:
                reply_button.click()
                self.delay_manager.wait()
            
            # 답변 입력 필드 찾기
            reply_input_selectors = [
                (By.CSS_SELECTOR, "textarea[name*='reply'], textarea[name*='comment']"),
                (By.CSS_SELECTOR, ".reply-input textarea, .comment-reply textarea"),
                (By.XPATH, "//textarea[contains(@placeholder, '답글') or contains(@placeholder, '댓글')]"),
                (By.CSS_SELECTOR, "textarea"),
            ]
            
            reply_input = None
            for by, selector in reply_input_selectors:
                try:
                    inputs = self.driver.find_elements(by, selector)
                    # 가장 최근에 나타난 textarea 사용 (답변 입력 필드)
                    if inputs:
                        reply_input = inputs[-1]
                        break
                except:
                    continue
            
            if not reply_input:
                logger.warning("답변 입력 필드를 찾을 수 없습니다")
                return False
            
            # 답변 입력
            reply_input.clear()
            reply_input.send_keys(reply_text)
            self.delay_manager.wait()
            
            # 등록 버튼 클릭
            submit_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(text(), '등록') or contains(text(), '작성')]"),
                (By.CSS_SELECTOR, ".submit-btn, .register-btn"),
            ]
            
            for by, selector in submit_selectors:
                try:
                    submit_btn = reply_input.find_element(By.XPATH, "./ancestor::form//button | ./ancestor::div//button")
                    if submit_btn:
                        submit_btn.click()
                        self.delay_manager.wait()
                        logger.info("✅ 댓글 답변 작성 완료")
                        return True
                except:
                    continue
            
            logger.warning("등록 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"댓글 답변 작성 오류: {e}")
            return False
    
    def process_comments(self, post_url: str, post_title: str = "") -> int:
        """포스팅의 모든 댓글 처리 (답변 작성)
        
        Args:
            post_url: 포스팅 URL
            post_title: 포스팅 제목
            
        Returns:
            답변한 댓글 개수
        """
        if not self.enabled:
            logger.debug("댓글 자동 답변이 비활성화되어 있습니다")
            return 0
        
        try:
            comments = self.get_unreplied_comments(post_url)
            if not comments:
                logger.info("답변할 댓글이 없습니다")
                return 0
            
            replied_count = 0
            for comment in comments:
                try:
                    # 답변 생성
                    reply_text = self.generate_reply(comment["content"], post_title)
                    
                    # 답변 작성
                    if self.reply_to_comment(post_url, comment["comment_id"], reply_text):
                        replied_count += 1
                        logger.info(f"✅ 댓글 답변 완료: {comment['author']}")
                        # 다음 댓글 처리 전 딜레이
                        self.delay_manager.delay_range(3, 5)
                    else:
                        logger.warning(f"❌ 댓글 답변 실패: {comment['author']}")
                
                except Exception as e:
                    logger.error(f"댓글 처리 오류: {e}")
                    continue
            
            logger.info(f"총 {replied_count}개의 댓글에 답변했습니다")
            return replied_count
            
        except Exception as e:
            logger.error(f"댓글 처리 중 오류: {e}")
            return 0

