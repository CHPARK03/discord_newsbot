import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """봇 설정 관리 클래스"""
    
    # Discord 설정
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    NEWS_CHANNEL_ID = int(os.getenv('NEWS_CHANNEL_ID', 0))
    
    # NewsAPI 설정
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
    NEWSAPI_BASE_URL = 'https://newsapi.org/v2'
    
    # OpenAI 설정 (선택사항)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # 뉴스 전송 시간 설정
    NEWS_SEND_TIME = os.getenv('NEWS_SEND_TIME', '09:00')
    # 타임존 설정 (컨테이너/클라우드 환경에서 정확한 스케줄)
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Seoul')
    
    # 뉴스 카테고리 설정
    NEWS_CATEGORIES = {
        'IT': {
            'keywords': ['IT기업', '테크기업', '소프트웨어', '클라우드', '반도체'],
            'emoji': '💻'
        },
        'AI': {
            'keywords': ['인공지능', 'ChatGPT', '머신러닝', '생성형AI', 'LLM'],
            'emoji': '🤖'
        },
        '정보보안': {
            'keywords': ['사이버보안', '해킹', '랜섬웨어', '개인정보유출', '정보보호'],
            'emoji': '🔒'
        },
        '경제': {
            'keywords': ['증시', '코스피', '환율', '금리', '부동산'],
            'emoji': '💰'
        }
    }
    
    # 언어 설정
    NEWS_LANGUAGE = 'ko'  # 한국어 뉴스
    NEWS_LANGUAGE_EN = 'en'  # 영어 뉴스
    
    # 뉴스 개수
    NEWS_PER_CATEGORY = 5
    
    @staticmethod
    def validate():
        """필수 설정 검증"""
        if not Config.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN이 설정되지 않았습니다.")
        if not Config.NEWS_CHANNEL_ID:
            raise ValueError("NEWS_CHANNEL_ID가 설정되지 않았습니다.")
        if not Config.NEWSAPI_KEY:
            raise ValueError("NEWSAPI_KEY가 설정되지 않았습니다.")
        return True
