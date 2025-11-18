"""
네이버 로그인 모듈
"""
import time
import os
import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class NaverLogin:
    """네이버 로그인 처리"""
    
    def __init__(self, driver: webdriver.Chrome, config: dict):
        self.driver = driver
        self.config = config
        # 환경변수에서 먼저 확인, 없으면 config에서 가져오기
        self.naver_id = os.getenv("NAVER_ID") or config.get("naver", {}).get("id", "")
        self.naver_password = os.getenv("NAVER_PASSWORD") or config.get("naver", {}).get("password", "")
        
        if not self.naver_id or not self.naver_password:
            raise ValueError("네이버 ID 또는 비밀번호가 설정되지 않았습니다. config.json 또는 환경변수를 확인하세요.")
    
    def login(self) -> bool:
        """네이버 로그인 수행"""
        try:
            logger.info("네이버 로그인 페이지 접속 중...")
            self.driver.get("https://nid.naver.com/nidlogin.login")
            
            # 로그인 폼 입력
            self._input_credentials()
            
            # 로그인 버튼 클릭
            login_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "log.login"))
            )
            login_button.click()
            
            # 로그인 완료 대기
            time.sleep(3)
            
            # 로그인 성공 확인
            if self._check_login_success():
                logger.info("✅ 로그인 성공")
                return True
            else:
                logger.error("❌ 로그인 실패")
                return False
                
        except Exception as e:
            logger.error(f"로그인 중 오류 발생: {e}")
            return False
    
    def _input_credentials(self):
        """로그인 정보 입력"""
        try:
            # 아이디 입력 (동적 대기 사용)
            id_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "id"))
            )
            # 요소가 클릭 가능할 때까지 대기
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "id"))
            )
            id_input.clear()
            # 자연스러운 타이핑을 위한 지연
            for char in self.naver_id:
                id_input.send_keys(char)
                time.sleep(0.1)
            
            time.sleep(1)
            
            # 비밀번호 입력
            pw_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "pw"))
            )
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "pw"))
            )
            pw_input.clear()
            for char in self.naver_password:
                pw_input.send_keys(char)
                time.sleep(0.1)
            
            time.sleep(1)
            
        except TimeoutException:
            logger.error("로그인 입력 필드를 찾을 수 없습니다")
            raise
        except Exception as e:
            logger.error(f"로그인 정보 입력 중 오류: {e}")
            raise
    
    def _check_login_success(self) -> bool:
        """로그인 성공 여부 확인"""
        try:
            # 로그인 완료 대기
            time.sleep(2)
            
            # 현재 URL 확인
            current_url = self.driver.current_url
            
            # 로그인 페이지가 아니면 성공으로 간주
            if "nid.naver.com" not in current_url:
                # 추가 확인: 네이버 메인 페이지나 블로그 페이지인지 확인
                if "naver.com" in current_url:
                    logger.info("로그인 성공 확인: 네이버 페이지로 이동됨")
                    return True
            
            # 에러 메시지 확인 (다양한 셀렉터 시도)
            error_selectors = [
                (By.CLASS_NAME, "error_message"),
                (By.CLASS_NAME, "error"),
                (By.ID, "err_common"),
                (By.CSS_SELECTOR, ".error_message"),
                (By.CSS_SELECTOR, "[class*='error']")
            ]
            
            for by, selector in error_selectors:
                try:
                    error_elements = self.driver.find_elements(by, selector)
                    if error_elements:
                        error_text = error_elements[0].text.strip()
                        if error_text:
                            logger.error(f"로그인 오류: {error_text}")
                            return False
                except Exception:
                    continue
            
            # 캡차 확인
            if "captcha" in current_url.lower() or "보안" in self.driver.page_source:
                logger.warning("캡차 또는 보안 인증이 필요합니다")
                return False
            
            # 여전히 로그인 페이지에 있으면 실패
            if "nid.naver.com" in current_url:
                logger.warning("로그인 페이지에 머물러 있습니다")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"로그인 확인 중 오류: {e}")
            return False

