from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger(__name__)

class NewsScheduler:
    """뉴스 전송 스케줄러"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        """스케줄러 시작"""
        self.scheduler.start()
        logger.info("스케줄러가 시작되었습니다.")
    
    def shutdown(self):
        """스케줄러 종료"""
        self.scheduler.shutdown()
        logger.info("스케줄러가 종료되었습니다.")
    
    def schedule_daily_news(self, callback, time_str: str = "09:00", timezone_name: str = "Asia/Seoul"):
        """매일 정해진 시간에 뉴스 전송 스케줄링
        
        Args:
            callback: 실행할 비동기 함수
            time_str: 실행 시간 (HH:MM 형식)
            timezone_name: 타임존 이름 (예: Asia/Seoul)
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            
            # Cron 표현식으로 매일 특정 시간에 실행
            trigger = CronTrigger(hour=hour, minute=minute, timezone=ZoneInfo(timezone_name))
            
            self.scheduler.add_job(
                callback,
                trigger=trigger,
                id='daily_news',
                name='일일 뉴스 전송',
                replace_existing=True
            )
            
            logger.info(f"매일 {time_str} ({timezone_name})에 뉴스 전송이 스케줄되었습니다.")
            
        except ValueError as e:
            logger.error(f"시간 형식이 올바르지 않습니다: {time_str}")
            raise
    
    def schedule_test_news(self, callback, seconds: int = 10):
        """테스트용 스케줄링 (몇 초 후 실행)
        
        Args:
            callback: 실행할 비동기 함수
            seconds: 몇 초 후 실행할지
        """
        self.scheduler.add_job(
            callback,
            'interval',
            seconds=seconds,
            id='test_news',
            name='테스트 뉴스 전송',
            replace_existing=True,
            max_instances=1
        )
        
        logger.info(f"{seconds}초마다 테스트 뉴스가 전송됩니다.")
    
    def remove_job(self, job_id: str):
        """특정 작업 제거"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"작업 '{job_id}'가 제거되었습니다.")
        except Exception as e:
            logger.error(f"작업 제거 중 오류: {e}")
    
    def get_jobs(self):
        """현재 스케줄된 작업 목록 반환"""
        return self.scheduler.get_jobs()
    
    def print_jobs(self):
        """스케줄된 작업 목록 출력"""
        jobs = self.get_jobs()
        if jobs:
            logger.info("=== 스케줄된 작업 목록 ===")
            for job in jobs:
                logger.info(f"- {job.name} (ID: {job.id}): {job.next_run_time}")
        else:
            logger.info("스케줄된 작업이 없습니다.")
