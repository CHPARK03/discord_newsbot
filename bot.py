import discord
from discord.ext import commands
import logging
from datetime import datetime

from config import Config
from news.fetcher import NewsFetcher
from news.summarizer import NewsSummarizer
from utils.scheduler import NewsScheduler

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 글로벌 객체
news_fetcher = None
news_summarizer = None
scheduler = None

@bot.event
async def on_ready():
    """봇이 준비되었을 때 실행"""
    global news_fetcher, news_summarizer, scheduler
    
    logger.info(f'{bot.user} 봇이 로그인했습니다!')
    logger.info(f'봇 ID: {bot.user.id}')
    logger.info('------')
    
    # 설정 검증
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"설정 오류: {e}")
        return
    
    # 뉴스 수집기 및 요약기 초기화
    news_fetcher = NewsFetcher(Config.NEWSAPI_KEY)
    news_summarizer = NewsSummarizer(Config.OPENAI_API_KEY)
    
    # 스케줄러 초기화 및 시작
    scheduler = NewsScheduler()
    scheduler.start()
    
    # 매일 정해진 시간에 뉴스 전송 스케줄링
    scheduler.schedule_daily_news(send_daily_news, Config.NEWS_SEND_TIME, Config.TIMEZONE)
    
    # 스케줄된 작업 확인
    scheduler.print_jobs()
    
    logger.info("봇이 완전히 준비되었습니다!")

async def send_daily_news():
    """매일 아침 뉴스를 전송하는 함수"""
    try:
        logger.info("일일 뉴스 전송 시작...")
        
        # 뉴스를 전송할 채널 가져오기
        channel = bot.get_channel(Config.NEWS_CHANNEL_ID)
        
        if not channel:
            logger.error(f"채널을 찾을 수 없습니다. ID: {Config.NEWS_CHANNEL_ID}")
            return
        
        # 카테고리별 뉴스 수집
        categorized_news = news_fetcher.fetch_categorized_news(
            Config.NEWS_CATEGORIES,
            Config.NEWS_PER_CATEGORY
        )
        
        # 이모지 딕셔너리 생성
        category_emojis = {
            name: info['emoji'] 
            for name, info in Config.NEWS_CATEGORIES.items()
        }
        
        # 뉴스 리포트 생성
        messages = news_summarizer.create_daily_news_report(
            categorized_news,
            category_emojis
        )
        
        # 메시지 전송
        for message in messages:
            await channel.send(message)
        
        logger.info(f"일일 뉴스 전송 완료! ({len(messages)}개 메시지)")
        
    except Exception as e:
        logger.error(f"뉴스 전송 중 오류: {e}", exc_info=True)

@bot.command(name='뉴스')
async def manual_news(ctx):
    """수동으로 뉴스를 요청하는 명령어"""
    await ctx.send("뉴스를 수집하고 있습니다... 잠시만 기다려주세요 ⏳")
    
    try:
        # 카테고리별 뉴스 수집
        categorized_news = news_fetcher.fetch_categorized_news(
            Config.NEWS_CATEGORIES,
            Config.NEWS_PER_CATEGORY
        )
        
        # 이모지 딕셔너리 생성
        category_emojis = {
            name: info['emoji'] 
            for name, info in Config.NEWS_CATEGORIES.items()
        }
        
        # 뉴스 리포트 생성
        messages = news_summarizer.create_daily_news_report(
            categorized_news,
            category_emojis
        )
        
        # 메시지 전송
        for message in messages:
            await ctx.send(message)
        
        logger.info(f"수동 뉴스 요청 처리 완료 (요청자: {ctx.author})")
        
    except Exception as e:
        await ctx.send(f"뉴스를 가져오는 중 오류가 발생했습니다: {e}")
        logger.error(f"수동 뉴스 요청 오류: {e}", exc_info=True)

@bot.command(name='테스트뉴스')
async def test_news(ctx):
    """테스트용 단일 카테고리 뉴스"""
    await ctx.send("IT 뉴스 테스트 중...")
    
    try:
        # IT 뉴스만 수집
        it_keywords = Config.NEWS_CATEGORIES['IT']['keywords']
        articles = news_fetcher.fetch_news_by_keywords(it_keywords, page_size=5)
        
        if articles:
            emoji = Config.NEWS_CATEGORIES['IT']['emoji']
            summary = news_summarizer.create_news_summary('IT', articles, emoji)
            await ctx.send(summary)
        else:
            await ctx.send("뉴스를 찾을 수 없습니다.")
    
    except Exception as e:
        await ctx.send(f"오류 발생: {e}")
        logger.error(f"테스트 뉴스 오류: {e}", exc_info=True)

@bot.command(name='스케줄')
async def show_schedule(ctx):
    """현재 스케줄된 작업 확인"""
    jobs = scheduler.get_jobs()
    
    if jobs:
        message = "📅 **현재 스케줄된 작업:**\n\n"
        for job in jobs:
            next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else '없음'
            message += f"• {job.name}\n"
            message += f"  다음 실행: {next_run}\n\n"
        await ctx.send(message)
    else:
        await ctx.send("스케줄된 작업이 없습니다.")

@bot.command(name='도움말')
async def help_command(ctx):
    """봇 사용법 안내"""
    help_text = """
📰 **뉴스 봇 사용법** 📰

**명령어:**
• `!뉴스` - 현재 뉴스를 즉시 가져옵니다
• `!테스트뉴스` - IT 뉴스 5개를 테스트로 가져옵니다
• `!스케줄` - 예약된 뉴스 전송 일정을 확인합니다
• `!도움말` - 이 도움말을 표시합니다

**자동 뉴스:**
매일 아침 {}에 다음 카테고리의 뉴스를 자동으로 전송합니다:
• 💻 IT 뉴스 TOP 10
• 🤖 AI 관련 뉴스 TOP 10
• 🔒 정보보안 뉴스 TOP 10
• 💰 경제 뉴스 TOP 10
    """.format(Config.NEWS_SEND_TIME)
    
    await ctx.send(help_text)

@bot.event
async def on_command_error(ctx, error):
    """명령어 오류 처리"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("알 수 없는 명령어입니다. `!도움말`을 입력하여 사용 가능한 명령어를 확인하세요.")
    else:
        logger.error(f"명령어 오류: {error}", exc_info=True)
        await ctx.send(f"오류가 발생했습니다: {error}")

def main():
    """메인 함수"""
    try:
        # 설정 검증
        Config.validate()
        
        # 봇 실행
        logger.info("봇을 시작합니다...")
        bot.run(Config.DISCORD_TOKEN)
        
    except ValueError as e:
        logger.error(f"설정 오류: {e}")
        print("\n❌ 설정 오류가 발생했습니다!")
        print(f"오류 내용: {e}")
        print("\n.env 파일을 확인하고 필수 값들을 설정해주세요.")
        print("(.env.example 파일을 참고하세요)")
        
    except Exception as e:
        logger.error(f"봇 실행 중 오류: {e}", exc_info=True)
        
    finally:
        if scheduler:
            scheduler.shutdown()

if __name__ == '__main__':
    main()
