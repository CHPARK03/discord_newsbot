import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import feedparser
from urllib.parse import quote

logger = logging.getLogger(__name__)

class NewsFetcher:
    """뉴스를 수집하는 클래스"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://newsapi.org/v2'
        
    def fetch_news_by_keywords(self, keywords: List[str], language: str = 'ko', 
                               from_date: Optional[str] = None, page_size: int = 10) -> List[Dict]:
        """키워드 기반으로 뉴스 수집"""
        try:
            # 어제 날짜 계산
            if not from_date:
                yesterday = datetime.now() - timedelta(days=1)
                from_date = yesterday.strftime('%Y-%m-%d')
            
            # 키워드를 OR 조건으로 연결
            query = ' OR '.join(keywords)
            
            url = f'{self.base_url}/everything'
            params = {
                'apiKey': self.api_key,
                'q': query,
                'language': language,
                'from': from_date,
                'sortBy': 'publishedAt',
                'pageSize': page_size
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                logger.info(f"수집된 뉴스: {len(articles)}개 (키워드: {query})")
                return articles
            else:
                logger.error(f"뉴스 수집 실패: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 오류: {e}")
            return []
        except Exception as e:
            logger.error(f"뉴스 수집 중 오류: {e}")
            return []
    
    def fetch_top_headlines(self, category: str = None, country: str = 'kr', 
                           page_size: int = 10) -> List[Dict]:
        """주요 헤드라인 뉴스 수집"""
        try:
            url = f'{self.base_url}/top-headlines'
            params = {
                'apiKey': self.api_key,
                'country': country,
                'pageSize': page_size
            }
            
            if category:
                params['category'] = category
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                logger.info(f"헤드라인 뉴스 수집: {len(articles)}개")
                return articles
            else:
                logger.error(f"헤드라인 수집 실패: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 오류: {e}")
            return []
        except Exception as e:
            logger.error(f"헤드라인 수집 중 오류: {e}")
            return []
    
    def fetch_categorized_news(self, categories: Dict[str, Dict], news_per_category: int = 10) -> Dict[str, List[Dict]]:
        """카테고리별 뉴스 수집 (중복 제거)"""
        result = {}
        used_urls = set()  # 이미 사용한 URL 추적
        used_titles = set()  # 이미 사용한 제목 추적 (유사 제목 방지)
        
        for category_name, category_info in categories.items():
            keywords = category_info.get('keywords', [])
            unique_articles = []
            all_sources_articles = []
            
            # 1. 네이버 RSS에서 뉴스 수집
            naver_articles = self.fetch_naver_rss_news(keywords, limit=news_per_category)
            all_sources_articles.extend(naver_articles)
            
            # 2. 다음 뉴스 RSS에서 수집
            daum_articles = self.fetch_daum_rss_news(keywords, limit=news_per_category)
            all_sources_articles.extend(daum_articles)
            
            # 3. 구글 뉴스 RSS에서 수집
            google_articles = self.fetch_google_rss_news(keywords, limit=news_per_category)
            all_sources_articles.extend(google_articles)
            
            # 4. NewsAPI에서 추가 수집 (보충용)
            if len(all_sources_articles) < news_per_category * 2:
                api_articles = self.fetch_news_by_keywords(keywords, language='ko', 
                                                          page_size=news_per_category)
                all_sources_articles.extend(api_articles)
            
            # 중복 제거
            for article in all_sources_articles:
                url = article.get('url', '')
                title = article.get('title', '')
                
                # URL 중복 체크
                if url and url in used_urls:
                    continue
                
                # 제목 중복 체크 (완전히 같은 제목)
                if title and title in used_titles:
                    continue
                
                # 유니크한 기사만 추가
                unique_articles.append(article)
                if url:
                    used_urls.add(url)
                if title:
                    used_titles.add(title)
                
                # 필요한 개수만큼 모으면 중단
                if len(unique_articles) >= news_per_category:
                    break
            
            result[category_name] = unique_articles[:news_per_category]
            logger.info(f"{category_name} 뉴스 수집 완료: {len(unique_articles)}개")
            
        return result
    
    def fetch_naver_rss_news(self, keywords: List[str], limit: int = 10) -> List[Dict]:
        """네이버 뉴스 RSS에서 뉴스 수집"""
        all_articles = []
        
        # 각 키워드로 RSS 검색
        for keyword in keywords[:3]:  # 너무 많은 요청 방지 위해 최대 3개 키워드만 사용
            try:
                # 네이버 뉴스 검색 RSS URL
                encoded_keyword = quote(keyword)
                rss_url = f'https://news.naver.com/main/search/search.naver?where=rss&query={encoded_keyword}'
                
                # RSS 파싱
                feed = feedparser.parse(rss_url)
                
                # 엔트리를 기사로 변환
                for entry in feed.entries[:limit]:
                    article = {
                        'title': entry.get('title', '제목 없음'),
                        'description': entry.get('description', ''),
                        'url': entry.get('link', ''),
                        'source': '네이버 뉴스',
                        'publishedAt': entry.get('published', ''),
                        'author': '',
                        'urlToImage': ''
                    }
                    
                    # 중복 제거 (같은 URL이 있으면 스킵)
                    if not any(a.get('url') == article['url'] for a in all_articles):
                        all_articles.append(article)
                    
                    if len(all_articles) >= limit:
                        break
                
                logger.info(f"네이버 RSS 수집: {len(all_articles)}개 (키워드: {keyword})")
                
                if len(all_articles) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"네이버 RSS 수집 중 오류 (키워드: {keyword}): {e}")
                continue
        
        return all_articles[:limit]
    
    def fetch_daum_rss_news(self, keywords: List[str], limit: int = 10) -> List[Dict]:
        """다음 뉴스 RSS에서 뉴스 수집"""
        all_articles = []
        
        # 각 키워드로 RSS 검색
        for keyword in keywords[:3]:
            try:
                # 다음 뉴스 검색 RSS URL
                encoded_keyword = quote(keyword)
                rss_url = f'https://search.daum.net/search?w=news&q={encoded_keyword}&rtupcoll=NNS&DA=STC&enc=utf8&output=rss'
                
                # RSS 파싱
                feed = feedparser.parse(rss_url)
                
                # 엔트리를 기사로 변환
                for entry in feed.entries[:limit]:
                    article = {
                        'title': entry.get('title', '제목 없음'),
                        'description': entry.get('description', ''),
                        'url': entry.get('link', ''),
                        'source': '다음 뉴스',
                        'publishedAt': entry.get('published', ''),
                        'author': '',
                        'urlToImage': ''
                    }
                    
                    # 중복 제거
                    if not any(a.get('url') == article['url'] for a in all_articles):
                        all_articles.append(article)
                    
                    if len(all_articles) >= limit:
                        break
                
                logger.info(f"다음 RSS 수집: {len(all_articles)}개 (키워드: {keyword})")
                
                if len(all_articles) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"다음 RSS 수집 중 오류 (키워드: {keyword}): {e}")
                continue
        
        return all_articles[:limit]
    
    def fetch_google_rss_news(self, keywords: List[str], limit: int = 10) -> List[Dict]:
        """구글 뉴스 RSS에서 뉴스 수집"""
        all_articles = []
        
        # 각 키워드로 RSS 검색
        for keyword in keywords[:3]:
            try:
                # 구글 뉴스 RSS URL (한국어, 한국)
                encoded_keyword = quote(keyword)
                rss_url = f'https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko'
                
                # RSS 파싱
                feed = feedparser.parse(rss_url)
                
                # 엔트리를 기사로 변환
                for entry in feed.entries[:limit]:
                    article = {
                        'title': entry.get('title', '제목 없음'),
                        'description': entry.get('summary', ''),
                        'url': entry.get('link', ''),
                        'source': entry.get('source', {}).get('title', '구글 뉴스'),
                        'publishedAt': entry.get('published', ''),
                        'author': '',
                        'urlToImage': ''
                    }
                    
                    # 중복 제거
                    if not any(a.get('url') == article['url'] for a in all_articles):
                        all_articles.append(article)
                    
                    if len(all_articles) >= limit:
                        break
                
                logger.info(f"구글 RSS 수집: {len(all_articles)}개 (키워드: {keyword})")
                
                if len(all_articles) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"구글 RSS 수집 중 오류 (키워드: {keyword}): {e}")
                continue
        
        return all_articles[:limit]
    
    def format_article(self, article: Dict) -> Dict:
        """기사 정보 포맷팅"""
        return {
            'title': article.get('title', '제목 없음'),
            'description': article.get('description', ''),
            'url': article.get('url', ''),
            'source': article.get('source', {}).get('name', '출처 불명'),
            'published_at': article.get('publishedAt', ''),
            'author': article.get('author', ''),
            'image': article.get('urlToImage', '')
        }
