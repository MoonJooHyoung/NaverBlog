"""
블로그 포스팅 업로드 모듈
"""
import time
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from utils.delay_manager import DelayManager

logger = logging.getLogger(__name__)

# 상수 정의
MAX_TAGS = 10
DEFAULT_CATEGORY = "일반"
DEFAULT_WAIT_TIME = 10
MAX_RETRIES = 3

class BlogPoster:
    """블로그 포스팅 업로드"""
    
    def __init__(self, driver: webdriver.Chrome, config: Dict):
        self.driver = driver
        self.config = config
        naver_config = config.get("naver", {})
        self.blog_url = naver_config.get("blog_url", "")
        if not self.blog_url:
            raise ValueError("블로그 URL이 설정되지 않았습니다.")
        self.advanced_config = config.get("advanced", {})
        
        # 딜레이 매니저 초기화
        base_delay = self.advanced_config.get("delay_between_actions", 2)
        random_delay = self.advanced_config.get("random_delay", True)
        self.delay_manager = DelayManager(base_delay=base_delay, random_delay=random_delay)
    
    def post(self, title: str, content: str, images: Optional[List[str]] = None, 
             tags: Optional[List[str]] = None, description: str = "", category: str = DEFAULT_CATEGORY,
             is_public: bool = True, allow_comments: bool = True, 
             scheduled_time: Optional[str] = None, thumbnail_image: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """포스팅 업로드
        
        Returns:
            (success, post_url): 성공 여부와 포스팅 URL
        """
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"포스팅 업로드 시도 {attempt + 1}/{MAX_RETRIES}")
                
                # 포스팅 작성 페이지로 이동
                post_url = f"{self.blog_url}/PostWriteForm.naver"
                logger.info(f"포스팅 페이지 접속: {post_url}")
                self.driver.get(post_url)
                
                # 페이지 로드 대기
                try:
                    WebDriverWait(self.driver, DEFAULT_WAIT_TIME).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                except TimeoutException:
                    logger.warning("페이지 로드 대기 시간 초과, 계속 진행합니다")
                self.delay_manager.short_wait()
                
                # 제목 입력
                self._input_title(title)
                self.delay_manager.short_wait()
                
                # 내용 입력
                self._input_content(content, images)
                self.delay_manager.medium_wait()
                
                # 태그 입력
                if tags:
                    self._input_tags(tags)
                    self.delay_manager.short_wait()
                
                # 카테고리 선택
                self._select_category(category)
                self.delay_manager.short_wait()
                
                # 네이버 블로그 특화 설정
                self._set_visibility(is_public)
                self.delay_manager.short_wait()
                
                self._set_comment_permission(allow_comments)
                self.delay_manager.short_wait()
                
                if thumbnail_image:
                    self._set_thumbnail(thumbnail_image)
                    self.delay_manager.short_wait()
                
                if scheduled_time:
                    self._set_scheduled_time(scheduled_time)
                    self.delay_manager.short_wait()
                
                # 발행 버튼 클릭
                success, post_url_result = self._click_publish_button()
                
                if success:
                    logger.info("✅ 포스팅 업로드 완료")
                    if post_url_result:
                        logger.info(f"포스팅 URL: {post_url_result}")
                    return True, post_url_result
                else:
                    if attempt < MAX_RETRIES - 1:
                        logger.warning(f"포스팅 실패, 재시도 중... ({attempt + 1}/{MAX_RETRIES})")
                        self.delay_manager.long_wait()
                        continue
                    else:
                        logger.error("포스팅 업로드 실패 (최대 재시도 횟수 초과)")
                        return False, None
                
            except Exception as e:
                logger.error(f"포스팅 업로드 오류 (시도 {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    self.delay_manager.long_wait()
                    continue
                else:
                    return False, None
        
        return False, None
    
    def _input_title(self, title: str):
        """제목 입력"""
        try:
            # 네이버 블로그 스마트에디터의 제목 입력 필드 찾기
            # 실제 셀렉터는 네이버 블로그 구조에 맞게 수정 필요
            title_selectors = [
                "input[name='subject']",
                "#subject",
                ".se-title-text",
                "input[placeholder*='제목']"
            ]
            
            for selector in title_selectors:
                try:
                    title_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    title_input.clear()
                    title_input.send_keys(title)
                    logger.info(f"제목 입력 완료: {title}")
                    return
                except:
                    continue
            
            logger.warning("제목 입력 필드를 찾을 수 없습니다")
            
        except Exception as e:
            logger.error(f"제목 입력 오류: {e}")
    
    def _input_content(self, content: str, images: List[str] = None):
        """내용 입력"""
        try:
            # 스마트에디터 iframe 찾기
            iframe_selectors = [
                "iframe.se-component-content",
                "iframe[id*='se']",
                "iframe[class*='editor']",
                "iframe.se-iframe",
                "iframe#se2_iframe"
            ]
            
            iframe_found = False
            for selector in iframe_selectors:
                try:
                    iframe = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    self.driver.switch_to.frame(iframe)
                    iframe_found = True
                    
                    # 에디터 본문 찾기 (다양한 셀렉터 시도)
                    body_selectors = [
                        (By.TAG_NAME, "body"),
                        (By.CLASS_NAME, "se-component-content"),
                        (By.ID, "se2_textarea"),
                        (By.CSS_SELECTOR, ".se-component-content")
                    ]
                    
                    body = None
                    for by, body_selector in body_selectors:
                        try:
                            body = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((by, body_selector))
                            )
                            break
                        except TimeoutException:
                            continue
                    
                    if body:
                        # 기존 내용 지우기
                        body.clear()
                        time.sleep(0.5)
                        
                        # 내용 입력 (자연스러운 타이핑)
                        body.send_keys(content)
                        time.sleep(1)
                        
                        # 이미지가 있으면 업로드
                        if images:
                            self.driver.switch_to.default_content()
                            self._upload_images(images)
                            self.driver.switch_to.frame(iframe)
                        
                        self.driver.switch_to.default_content()
                        logger.info("내용 입력 완료")
                        return
                    else:
                        logger.warning("에디터 본문을 찾을 수 없습니다")
                        self.driver.switch_to.default_content()
                        
                except TimeoutException:
                    if iframe_found:
                        self.driver.switch_to.default_content()
                    continue
                except Exception as e:
                    logger.error(f"에디터 접근 중 오류: {e}")
                    if iframe_found:
                        self.driver.switch_to.default_content()
                    continue
            
            if not iframe_found:
                logger.warning("에디터 iframe을 찾을 수 없습니다. 직접 입력을 시도합니다.")
                # iframe이 없는 경우 직접 입력 시도
                try:
                    content_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, [contenteditable='true']"))
                    )
                    content_input.clear()
                    content_input.send_keys(content)
                    logger.info("내용 입력 완료 (직접 입력)")
                except Exception as e:
                    logger.error(f"직접 입력도 실패: {e}")
            
        except Exception as e:
            logger.error(f"내용 입력 오류: {e}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
    
    def _input_tags(self, tags: List[str]):
        """태그 입력"""
        try:
            tag_input_selectors = [
                "input[name='tag']",
                "#tag",
                "input[placeholder*='태그']"
            ]
            
            for selector in tag_input_selectors:
                try:
                    tag_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    tag_text = ", ".join(tags[:MAX_TAGS])
                    tag_input.clear()
                    tag_input.send_keys(tag_text)
                    logger.info(f"태그 입력 완료: {tag_text}")
                    return
                except:
                    continue
            
        except Exception as e:
            logger.error(f"태그 입력 오류: {e}")
    
    def _select_category(self, category: str):
        """카테고리 선택"""
        try:
            # 카테고리 선택 버튼 찾기
            category_selectors = [
                (By.CSS_SELECTOR, "button[class*='category']"),
                (By.CSS_SELECTOR, "a[class*='category']"),
                (By.ID, "category"),
                (By.CSS_SELECTOR, ".category_select"),
                (By.CSS_SELECTOR, "[data-name='category']")
            ]
            
            category_button = None
            for by, selector in category_selectors:
                try:
                    category_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if category_button:
                category_button.click()
                time.sleep(1)
                
                # 카테고리 목록에서 선택
                category_list_selectors = [
                    (By.XPATH, f"//*[contains(text(), '{category}')]"),
                    (By.CSS_SELECTOR, f"li[data-category='{category}']"),
                    (By.CSS_SELECTOR, f"a:contains('{category}')"),
                    (By.XPATH, f"//li[contains(@class, 'category') and contains(text(), '{category}')]")
                ]
                
                for by, selector in category_list_selectors:
                    try:
                        category_item = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((by, selector))
                        )
                        category_item.click()
                        logger.info(f"카테고리 선택 완료: {category}")
                        time.sleep(0.5)
                        return
                    except TimeoutException:
                        continue
                
                logger.warning(f"카테고리 '{category}'를 찾을 수 없습니다")
            else:
                logger.info("카테고리 선택 기능을 찾을 수 없습니다. 기본 카테고리 사용")
                
        except Exception as e:
            logger.warning(f"카테고리 선택 중 오류 (무시됨): {e}")
    
    def _click_publish_button(self) -> tuple[bool, Optional[str]]:
        """발행 버튼 클릭
        
        Returns:
            (success, post_url): 성공 여부와 포스팅 URL
        """
        try:
            # 다양한 발행 버튼 셀렉터 시도
            publish_selectors = [
                (By.XPATH, "//button[contains(text(), '발행')]"),
                (By.XPATH, "//a[contains(text(), '발행')]"),
                (By.XPATH, "//button[contains(text(), '등록')]"),
                (By.XPATH, "//a[contains(text(), '등록')]"),
                (By.CSS_SELECTOR, "button[class*='publish']"),
                (By.CSS_SELECTOR, "a[class*='publish']"),
                (By.CSS_SELECTOR, "button[class*='submit']"),
                (By.CSS_SELECTOR, "a[class*='submit']"),
                (By.ID, "publishBtn"),
                (By.ID, "submitBtn"),
                (By.CSS_SELECTOR, ".btn_publish"),
                (By.CSS_SELECTOR, ".btn_submit")
            ]
            
            for by, selector in publish_selectors:
                try:
                    publish_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    # 스크롤하여 버튼이 보이도록
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", publish_btn)
                    self.delay_manager.short_wait()
                    publish_btn.click()
                    self.delay_manager.medium_wait()
                    
                    # 발행 완료 확인 및 URL 추출
                    success, post_url = self._verify_publish_success()
                    if success:
                        logger.info("✅ 발행 버튼 클릭 및 발행 완료 확인")
                        return True, post_url
                    else:
                        logger.info("발행 버튼 클릭 완료 (확인 필요)")
                        return True, None
                        
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.debug(f"셀렉터 {selector} 시도 중 오류: {e}")
                    continue
            
            logger.warning("발행 버튼을 찾을 수 없습니다. 수동으로 발행해주세요.")
            return False, None
            
        except Exception as e:
            logger.error(f"발행 버튼 클릭 오류: {e}")
            return False, None
    
    def _verify_publish_success(self) -> tuple[bool, Optional[str]]:
        """발행 성공 여부 확인 및 URL 추출
        
        Returns:
            (success, post_url): 성공 여부와 포스팅 URL
        """
        try:
            self.delay_manager.medium_wait()
            current_url = self.driver.current_url
            post_url = None
            
            # 포스팅 작성 페이지가 아니면 성공으로 간주
            if "PostWriteForm" not in current_url and "PostWrite" not in current_url:
                # URL이 포스팅 상세 페이지인지 확인
                if "PostView" in current_url:
                    post_url = current_url
                    logger.info(f"포스팅 URL 추출: {post_url}")
                    return True, post_url
                
                # 포스팅 목록 페이지인 경우 최신 포스팅 URL 추출 시도
                if "PostList" in current_url:
                    post_url = self._extract_latest_post_url()
                    if post_url:
                        return True, post_url
                
                # 성공 메시지 확인
                success_indicators = [
                    "발행되었습니다",
                    "등록되었습니다",
                    "완료되었습니다",
                    "success"
                ]
                
                page_source = self.driver.page_source.lower()
                for indicator in success_indicators:
                    if indicator in page_source:
                        # 페이지에서 URL 추출 시도
                        post_url = self._extract_post_url_from_page()
                        return True, post_url
            
            return False, None
            
        except Exception as e:
            logger.debug(f"발행 확인 중 오류: {e}")
            return False, None
    
    def _extract_latest_post_url(self) -> Optional[str]:
        """최신 포스팅 URL 추출"""
        try:
            # 포스팅 목록에서 첫 번째 포스팅 링크 찾기
            post_link_selectors = [
                (By.CSS_SELECTOR, "a[href*='PostView']"),
                (By.CSS_SELECTOR, ".post_title a"),
                (By.XPATH, "//a[contains(@href, 'PostView')]")
            ]
            
            for by, selector in post_link_selectors:
                try:
                    links = self.driver.find_elements(by, selector)
                    if links:
                        url = links[0].get_attribute("href")
                        if url and "PostView" in url:
                            return url
                except:
                    continue
        except Exception as e:
            logger.debug(f"URL 추출 중 오류: {e}")
        return None
    
    def _extract_post_url_from_page(self) -> Optional[str]:
        """페이지에서 포스팅 URL 추출"""
        try:
            # JavaScript로 URL 추출 시도
            script = """
            var links = document.querySelectorAll('a[href*="PostView"]');
            if (links.length > 0) {
                return links[0].href;
            }
            return null;
            """
            url = self.driver.execute_script(script)
            if url:
                return url
        except:
            pass
        return None
    
    def _set_visibility(self, is_public: bool):
        """공개/비공개 설정"""
        try:
            # 공개 설정 셀렉터
            visibility_selectors = [
                (By.CSS_SELECTOR, "input[name='openType']"),
                (By.CSS_SELECTOR, "input[type='radio'][value*='public']"),
                (By.CSS_SELECTOR, "input[type='radio'][value*='private']"),
                (By.XPATH, "//input[@name='openType' and @value='0']"),  # 공개
                (By.XPATH, "//input[@name='openType' and @value='1']"),  # 비공개
            ]
            
            for by, selector in visibility_selectors:
                try:
                    if "value" in selector.lower():
                        # value 기반 선택
                        value = "0" if is_public else "1"
                        radio = self.driver.find_element(by, selector.replace("value*=", f"value='{value}'"))
                        if not radio.is_selected():
                            radio.click()
                            logger.info(f"공개 설정: {'공개' if is_public else '비공개'}")
                            return
                    else:
                        # 일반 라디오 버튼
                        radios = self.driver.find_elements(by, selector)
                        if radios:
                            target_index = 0 if is_public else 1
                            if target_index < len(radios):
                                radios[target_index].click()
                                logger.info(f"공개 설정: {'공개' if is_public else '비공개'}")
                                return
                except:
                    continue
            
            logger.debug("공개/비공개 설정을 찾을 수 없습니다")
        except Exception as e:
            logger.warning(f"공개 설정 중 오류 (무시됨): {e}")
    
    def _set_comment_permission(self, allow_comments: bool):
        """댓글 허용/비허용 설정"""
        try:
            comment_selectors = [
                (By.CSS_SELECTOR, "input[name='commentYn']"),
                (By.CSS_SELECTOR, "input[type='checkbox'][name*='comment']"),
                (By.XPATH, "//input[@name='commentYn']"),
            ]
            
            for by, selector in comment_selectors:
                try:
                    checkbox = self.driver.find_element(by, selector)
                    is_checked = checkbox.is_selected()
                    
                    if allow_comments and not is_checked:
                        checkbox.click()
                        logger.info("댓글 허용 설정")
                        return
                    elif not allow_comments and is_checked:
                        checkbox.click()
                        logger.info("댓글 비허용 설정")
                        return
                    elif allow_comments and is_checked:
                        logger.debug("댓글 이미 허용됨")
                        return
                except:
                    continue
            
            logger.debug("댓글 설정을 찾을 수 없습니다")
        except Exception as e:
            logger.warning(f"댓글 설정 중 오류 (무시됨): {e}")
    
    def _set_thumbnail(self, thumbnail_path: str):
        """썸네일 이미지 설정"""
        try:
            if not os.path.exists(thumbnail_path):
                logger.warning(f"썸네일 이미지 파일을 찾을 수 없습니다: {thumbnail_path}")
                return
            
            thumbnail_selectors = [
                (By.CSS_SELECTOR, "input[type='file'][accept*='image']"),
                (By.CSS_SELECTOR, "input[name*='thumbnail']"),
                (By.XPATH, "//input[@type='file' and contains(@accept, 'image')]"),
            ]
            
            for by, selector in thumbnail_selectors:
                try:
                    file_input = self.driver.find_element(by, selector)
                    file_input.send_keys(os.path.abspath(thumbnail_path))
                    logger.info(f"썸네일 이미지 설정: {os.path.basename(thumbnail_path)}")
                    self.delay_manager.medium_wait()  # 업로드 대기
                    return
                except:
                    continue
            
            logger.debug("썸네일 업로드 입력을 찾을 수 없습니다")
        except Exception as e:
            logger.warning(f"썸네일 설정 중 오류 (무시됨): {e}")
    
    def _set_scheduled_time(self, scheduled_time: str):
        """예약 발행 시간 설정 (형식: 'YYYY-MM-DD HH:MM' 또는 'HH:MM')"""
        try:
            from datetime import datetime
            
            # 시간 형식 파싱
            try:
                if len(scheduled_time) == 5:  # HH:MM 형식
                    hour, minute = scheduled_time.split(':')
                    scheduled_datetime = datetime.now().replace(
                        hour=int(hour), minute=int(minute), second=0, microsecond=0
                    )
                else:  # YYYY-MM-DD HH:MM 형식
                    scheduled_datetime = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
            except ValueError:
                logger.error(f"예약 시간 형식이 올바르지 않습니다: {scheduled_time}")
                return
            
            # 예약 발행 버튼/체크박스 찾기
            schedule_selectors = [
                (By.CSS_SELECTOR, "input[name*='schedule']"),
                (By.CSS_SELECTOR, "input[type='checkbox'][name*='reserve']"),
                (By.XPATH, "//input[contains(@name, 'schedule')]"),
            ]
            
            for by, selector in schedule_selectors:
                try:
                    schedule_input = self.driver.find_element(by, selector)
                    if not schedule_input.is_selected():
                        schedule_input.click()
                        self.delay_manager.short_wait()
                    
                    # 날짜/시간 입력 필드 찾기
                    date_selectors = [
                        (By.CSS_SELECTOR, "input[name*='scheduleDate']"),
                        (By.CSS_SELECTOR, "input[type='date']"),
                        (By.CSS_SELECTOR, "input[type='datetime-local']"),
                    ]
                    
                    for date_by, date_selector in date_selectors:
                        try:
                            date_input = self.driver.find_element(date_by, date_selector)
                            # 날짜 형식 변환
                            date_str = scheduled_datetime.strftime("%Y-%m-%d")
                            time_str = scheduled_datetime.strftime("%H:%M")
                            
                            if "datetime-local" in date_selector:
                                datetime_str = scheduled_datetime.strftime("%Y-%m-%dT%H:%M")
                                date_input.clear()
                                date_input.send_keys(datetime_str)
                            else:
                                date_input.clear()
                                date_input.send_keys(date_str)
                                # 시간 입력 필드 찾기
                                time_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='time']")
                                time_input.clear()
                                time_input.send_keys(time_str)
                            
                            logger.info(f"예약 발행 시간 설정: {scheduled_time}")
                            return
                        except:
                            continue
                except:
                    continue
            
            logger.debug("예약 발행 설정을 찾을 수 없습니다")
        except Exception as e:
            logger.warning(f"예약 발행 설정 중 오류 (무시됨): {e}")
    
    def _upload_images(self, images: List[str]):
        """이미지 업로드"""
        try:
            if not images:
                return
            
            logger.info(f"이미지 {len(images)}개 업로드 시작")
            
            # 이미지 업로드 버튼 찾기
            upload_selectors = [
                (By.CSS_SELECTOR, "button[class*='image']"),
                (By.CSS_SELECTOR, "button[class*='upload']"),
                (By.CSS_SELECTOR, "input[type='file'][accept*='image']"),
                (By.XPATH, "//button[contains(text(), '이미지')]"),
                (By.XPATH, "//button[contains(text(), '사진')]"),
                (By.ID, "imageUpload"),
                (By.CSS_SELECTOR, ".btn_image")
            ]
            
            upload_input = None
            for by, selector in upload_selectors:
                try:
                    if "input" in selector.lower():
                        upload_input = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((by, selector))
                        )
                    else:
                        upload_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((by, selector))
                        )
                        upload_btn.click()
                        time.sleep(1)
                        # 클릭 후 파일 입력 필드가 나타날 수 있음
                        upload_input = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                        )
                    break
                except TimeoutException:
                    continue
            
            if upload_input:
                for image_path in images:
                    if os.path.exists(image_path):
                        try:
                            upload_input.send_keys(os.path.abspath(image_path))
                            time.sleep(2)  # 업로드 대기
                            logger.info(f"이미지 업로드 완료: {os.path.basename(image_path)}")
                        except Exception as e:
                            logger.error(f"이미지 업로드 실패 ({image_path}): {e}")
                    else:
                        logger.warning(f"이미지 파일을 찾을 수 없습니다: {image_path}")
            else:
                logger.warning("이미지 업로드 버튼을 찾을 수 없습니다")
                
        except Exception as e:
            logger.error(f"이미지 업로드 중 오류: {e}")

