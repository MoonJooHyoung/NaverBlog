"""
로깅 설정 모듈
"""
import logging
import colorlog
from pathlib import Path

def setup_logger(name: str = "naver_blog_automation", level: int = logging.INFO) -> logging.Logger:
    """로거 설정"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 기존 핸들러 제거
    logger.handlers = []
    
    # 콘솔 핸들러 (컬러)
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(level)
    
    # 컬러 포맷터
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s%(reset)s | %(asctime)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(
        log_dir / f"{name}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    file_formatter = logging.Formatter(
        "%(levelname)s | %(asctime)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

