from typing import List, Dict
import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class NewsSummarizer:
    """뉴스 요약 클래스"""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        self.use_openai = bool(openai_api_key)
        
        if self.use_openai:
            try:
                import openai
                self.openai = openai
                self.openai.api_key = openai_api_key
                logger.info("OpenAI API 사용 가능")
            except ImportError:
                logger.warning("OpenAI 라이브러리가 설치되지 않았습니다. 기본 요약을 사용합니다.")
                self.use_openai = False
    
    def summarize_article(self, article: Dict, max_length: int = 200) -> str:
        """단일 기사 요약"""
        if self.use_openai:
            return self._summarize_with_openai(article)
        else:
            return self._summarize_basic(article, max_length)
    
    def _summarize_basic(self, article: Dict, max_length: int = 200) -> str:
        """기본 요약 (OpenAI 미사용)"""
        description = article.get('description', '')
        
        # HTML 태그 제거
        if description:
            # BeautifulSoup로 HTML 파싱 및 텍스트 추출
            soup = BeautifulSoup(description, 'html.parser')
            description = soup.get_text(separator=' ', strip=True)
            
            # 여러 공백을 하나로
            description = re.sub(r'\s+', ' ', description)
            
            # URL 같은 긴 문자열 제거 (50자 이상의 연속 문자)
            description = re.sub(r'\S{50,}', '', description).strip()
        
        if description and len(description) > max_length:
            return description[:max_length] + '...'
        elif description:
            return description
        else:
            return '요약 정보 없음'
    
    def _summarize_with_openai(self, article: Dict) -> str:
        """OpenAI를 사용한 요약"""
        try:
            title = article.get('title', '')
            description = article.get('description', '')
            content = f"{title}\n\n{description}"
            
            response = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 뉴스를 간결하게 요약하는 전문가입니다. 핵심 내용만 2-3문장으로 요약해주세요."},
                    {"role": "user", "content": f"다음 뉴스를 요약해주세요:\n\n{content}"}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"OpenAI 요약 중 오류: {e}")
            return self._summarize_basic(article)
    
    def create_news_summary(self, category_name: str, articles: List[Dict], emoji: str = '📰') -> str:
        """카테고리별 뉴스 요약 생성"""
        if not articles:
            return f"{emoji} **{category_name} 뉴스**\n오늘은 {category_name} 관련 뉴스가 없습니다.\n"
        
        summary = f"{emoji} **{category_name} 뉴스 TOP {len(articles)}**\n"
        summary += f"{'─' * 40}\n\n"
        
        for idx, article in enumerate(articles, 1):
            title = article.get('title', '제목 없음')
            url = article.get('url', '')
            source = article.get('source', '출처 불명')
            description = self.summarize_article(article, max_length=150)
            
            summary += f"**{idx}. {title}**\n"
            summary += f"📌 {description}\n"
            summary += f"🔗 출처: {source}\n"
            
            if url:
                summary += f"링크: <{url}>\n"
            
            summary += "\n"
        
        summary += f"{'─' * 40}\n\n"
        
        return summary
    
    def create_daily_news_report(self, categorized_news: Dict[str, List[Dict]], 
                                 category_emojis: Dict[str, str]) -> List[str]:
        """일일 뉴스 리포트 생성 (여러 메시지로 분할)"""
        messages = []
        
        # 헤더
        header = "📰 **오늘의 뉴스 브리핑** 📰\n"
        header += f"{'=' * 40}\n\n"
        messages.append(header)
        
        # 각 카테고리별로 메시지 생성
        for category_name, articles in categorized_news.items():
            emoji = category_emojis.get(category_name, '📰')
            category_summary = self.create_news_summary(category_name, articles, emoji)
            
            # Discord 메시지 길이 제한 (2000자) 고려
            if len(category_summary) > 1900:
                # 너무 길면 분할
                parts = self._split_message(category_summary, 1900)
                messages.extend(parts)
            else:
                messages.append(category_summary)
        
        # 푸터
        footer = f"\n{'=' * 40}\n"
        footer += "📅 매일 아침 최신 뉴스를 전달해드립니다!"
        messages.append(footer)
        
        return messages
    
    def _split_message(self, message: str, max_length: int = 1900) -> List[str]:
        """긴 메시지를 여러 개로 분할"""
        if len(message) <= max_length:
            return [message]
        
        parts = []
        lines = message.split('\n')
        current_part = ""
        
        for line in lines:
            if len(current_part) + len(line) + 1 <= max_length:
                current_part += line + '\n'
            else:
                if current_part:
                    parts.append(current_part)
                current_part = line + '\n'
        
        if current_part:
            parts.append(current_part)
        
        return parts
