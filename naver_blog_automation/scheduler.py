"""
예약 발행 스케줄러 모듈
"""
import logging
import schedule
import time
from datetime import datetime
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)

# 상수 정의
SCHEDULER_CHECK_INTERVAL = 60  # 초

class PostScheduler:
    """예약 발행 스케줄러"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.scheduler_config = config.get("scheduler", {})
        default_times: List[str] = ["09:00", "14:00", "20:00"]
        self.default_times = self.scheduler_config.get("default_posting_times", default_times)
    
    def start(self, posting_function: Callable):
        """스케줄러 시작"""
        logger.info("스케줄러 시작")
        
        # 기본 발행 시간 설정
        for posting_time in self.default_times:
            schedule.every().day.at(posting_time).do(posting_function)
            logger.info(f"예약 발행 시간 설정: {posting_time}")
        
        # 스케줄러 실행
        try:
            while True:
                schedule.run_pending()
                time.sleep(SCHEDULER_CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("스케줄러 종료")
    
    def add_schedule(self, time_str: str, posting_function: Callable):
        """예약 추가"""
        schedule.every().day.at(time_str).do(posting_function)
        logger.info(f"예약 추가: {time_str}")
    
    def clear_schedules(self):
        """모든 예약 제거"""
        schedule.clear()
        logger.info("모든 예약 제거")

