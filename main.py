"""
네이버 블로그 자동화 프로그램 메인 파일
"""
import json
import logging
from pathlib import Path
from naver_blog_automation import NaverBlogAutomation
from utils.logger import setup_logger
from utils.config_validator import ConfigValidator

def load_config():
    """설정 파일 로드"""
    config_path = Path("config.json")
    if not config_path.exists():
        print("❌ config.json 파일이 없습니다.")
        print("config.json.example 파일을 참고하여 config.json을 생성하세요.")
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """메인 함수"""
    # 로거 설정
    logger = setup_logger()
    logger.info("=" * 50)
    logger.info("네이버 블로그 자동화 프로그램 시작")
    logger.info("=" * 50)
    
    # 설정 로드
    config = load_config()
    if not config:
        return
    
    # 설정 검증
    if not ConfigValidator.validate_and_log(config):
        logger.error("설정 검증 실패. 프로그램을 종료합니다.")
        return
    
    automation = None
    try:
        # 자동화 객체 생성
        automation = NaverBlogAutomation(config)
        
        # 로그인
        if not automation.login():
            logger.error("로그인 실패")
            return
        
        logger.info("✅ 로그인 성공")
        
        # 자동화 작업 실행
        automation.run_automation()
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단되었습니다")
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
    finally:
        if automation:
            automation.close()
        logger.info("프로그램 종료")

if __name__ == "__main__":
    main()

