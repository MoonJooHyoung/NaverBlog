"""
딜레이 관리 모듈
랜덤 딜레이 및 자연스러운 대기 시간 관리
"""
import time
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DelayManager:
    """딜레이 관리 클래스"""
    
    def __init__(self, base_delay: float = 2.0, random_delay: bool = True, 
                 min_random: float = 0.5, max_random: float = 2.0):
        """
        Args:
            base_delay: 기본 딜레이 시간 (초)
            random_delay: 랜덤 딜레이 사용 여부
            min_random: 최소 랜덤 시간 (초)
            max_random: 최대 랜덤 시간 (초)
        """
        self.base_delay = base_delay
        self.random_delay = random_delay
        self.min_random = min_random
        self.max_random = max_random
    
    def wait(self, custom_delay: Optional[float] = None):
        """대기 시간 적용"""
        if custom_delay is not None:
            delay = custom_delay
        else:
            delay = self.base_delay
        
        if self.random_delay:
            random_add = random.uniform(self.min_random, self.max_random)
            delay += random_add
        
        time.sleep(delay)
        logger.debug(f"딜레이 적용: {delay:.2f}초")
    
    def delay(self, custom_delay: Optional[float] = None):
        """대기 시간 적용 (wait의 별칭)"""
        self.wait(custom_delay)
    
    def delay_range(self, min_delay: float, max_delay: float):
        """범위 딜레이 적용"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        logger.debug(f"범위 딜레이 적용: {delay:.2f}초")
    
    def short_wait(self):
        """짧은 대기 (0.5~1.5초)"""
        delay = random.uniform(0.5, 1.5) if self.random_delay else 0.5
        time.sleep(delay)
    
    def medium_wait(self):
        """중간 대기 (1~3초)"""
        delay = random.uniform(1.0, 3.0) if self.random_delay else 2.0
        time.sleep(delay)
    
    def long_wait(self):
        """긴 대기 (3~5초)"""
        delay = random.uniform(3.0, 5.0) if self.random_delay else 4.0
        time.sleep(delay)

