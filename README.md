# Discord News Bot 📰

매일 아침 IT, AI, 정보보안, 경제 뉴스를 자동으로 요약해서 전달하는 디스코드 챗봇입니다.

## 주요 기능

- 📰 **자동 뉴스 전송**: 매일 설정된 시간에 자동으로 뉴스 전송
- 🔍 **카테고리별 수집**: IT, AI, 정보보안, 경제 분야의 TOP 10 뉴스
- 📝 **뉴스 요약**: 핵심 내용만 간추려서 제공
- 🤖 **디스코드 명령어**: 언제든지 수동으로 뉴스 확인 가능

## 설치 방법

### 1. 필수 요구사항

- Python 3.8 이상
- Discord Bot Token
- NewsAPI Key (https://newsapi.org/)

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 필수 값들을 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 내용:
```
DISCORD_TOKEN=your_discord_bot_token_here
NEWS_CHANNEL_ID=your_channel_id_here
NEWSAPI_KEY=your_newsapi_key_here
NEWS_SEND_TIME=09:00
```

#### Discord Bot Token 발급 방법:
1. https://discord.com/developers/applications 접속
2. "New Application" 클릭
3. Bot 탭에서 "Add Bot" 클릭
4. Token 복사 (Reset Token 클릭 시 새로 생성)
5. Bot 탭에서 "MESSAGE CONTENT INTENT" 활성화 필수!
6. OAuth2 > URL Generator에서:
   - SCOPES: `bot` 선택
   - BOT PERMISSIONS: `Send Messages`, `Read Messages/View Channels` 선택
7. 생성된 URL로 봇을 서버에 초대

#### News Channel ID 확인 방법:
1. Discord 설정 > 고급 > 개발자 모드 활성화
2. 뉴스를 받고 싶은 채널에서 우클릭 > "ID 복사"

#### NewsAPI Key 발급:
1. https://newsapi.org/ 접속
2. 회원가입
3. API Key 복사 (무료 플랜: 100 requests/day)

## 사용 방법

### 봇 실행

```bash
python bot.py
```

### 디스코드 명령어

- `!뉴스` - 현재 뉴스를 즉시 가져옵니다
- `!테스트뉴스` - IT 뉴스 5개를 테스트로 가져옵니다
- `!스케줄` - 예약된 뉴스 전송 일정을 확인합니다
- `!도움말` - 봇 사용법을 확인합니다

### 자동 뉴스 전송

`.env` 파일의 `NEWS_SEND_TIME`에 설정된 시간(기본 09:00)에 자동으로 뉴스가 전송됩니다.

## 프로젝트 구조

```
discord_chatbot/
├── bot.py                  # 메인 봇 실행 파일
├── config.py              # 설정 관리
├── .env                   # 환경 변수 (git에 포함 안 됨)
├── .env.example           # 환경 변수 예시
├── requirements.txt       # Python 패키지 목록
├── news/
│   ├── __init__.py
│   ├── fetcher.py        # 뉴스 수집 모듈
│   └── summarizer.py     # 뉴스 요약 모듈
└── utils/
    ├── __init__.py
    └── scheduler.py      # 스케줄링 모듈

## 24/7 배포 가이드

### Render (권장, 무료 플랜 가능)

1. 이 폴더를 GitHub에 푸시합니다.
2. https://render.com 에 가입 후 "New +" → "Worker" 선택
3. 리포지토리 연결 후 Build Command: `pip install -r requirements.txt`, Start Command: `python bot.py`
4. 환경변수(Secrets)를 설정합니다:
    - `DISCORD_TOKEN`: 디스코드 봇 토큰
    - `NEWS_CHANNEL_ID`: 채널 ID
    - `NEWSAPI_KEY`: NewsAPI 키
    - `NEWS_SEND_TIME`: 예 `09:00`
    - `TIMEZONE`: `Asia/Seoul`
5. 배포하면 컨테이너가 백그라운드에서 계속 실행됩니다.

참고: `render.yaml` 파일로 IaC 배포도 가능합니다.

### Railway (간단, 무료 플랜 가능)

1. GitHub에 푸시 후 https://railway.app 에서 프로젝트 생성
2. "Deploy from Repo" 선택 후 연결
3. `Procfile` 의 `worker: python bot.py`가 자동 인식됩니다
4. 환경변수로 `DISCORD_TOKEN`, `NEWS_CHANNEL_ID`, `NEWSAPI_KEY`, `NEWS_SEND_TIME`, `TIMEZONE` 등록
5. 배포 후 워커가 24/7 실행됩니다.

### 타임존과 스케줄

컨테이너 환경은 기본 UTC일 수 있으므로 `TIMEZONE=Asia/Seoul` 환경변수를 설정하고, 내부 스케줄러는 해당 타임존으로 매일 설정된 시간에 실행됩니다.
```

## 수집 뉴스 카테고리

1. **💻 IT 뉴스**: 기술, 소프트웨어, 하드웨어, 스타트업 관련
2. **🤖 AI 뉴스**: 인공지능, 머신러닝, ChatGPT, LLM 관련
3. **🔒 정보보안**: 사이버보안, 해킹, 취약점, 랜섬웨어 관련
4. **💰 경제**: 경제, 비즈니스, 주식, 금융, 투자 관련

## 설정 커스터마이징

### 뉴스 전송 시간 변경
`.env` 파일에서 `NEWS_SEND_TIME` 수정:
```
NEWS_SEND_TIME=08:30  # 오전 8시 30분
```

### 카테고리 및 키워드 수정
[config.py](config.py)의 `NEWS_CATEGORIES` 딕셔너리를 수정하세요.

### 뉴스 개수 조정
[config.py](config.py)의 `NEWS_PER_CATEGORY` 값을 변경하세요 (기본값: 10).

## 문제 해결

### 봇이 실행되지 않을 때
- `.env` 파일의 모든 필수 값이 올바르게 설정되었는지 확인
- Discord Bot의 "MESSAGE CONTENT INTENT"가 활성화되어 있는지 확인
- Python 버전이 3.8 이상인지 확인

### 뉴스가 수집되지 않을 때
- NewsAPI Key가 유효한지 확인
- 무료 플랜 일일 요청 제한(100회)을 초과하지 않았는지 확인
- 인터넷 연결 상태 확인

### 봇이 메시지를 보내지 못할 때
- 봇이 해당 채널에 메시지를 보낼 권한이 있는지 확인
- NEWS_CHANNEL_ID가 올바른지 확인

## 로그 확인

실행 중 발생하는 모든 로그는 `bot.log` 파일에 기록됩니다.

## 라이선스

MIT License

## 개발자

디스코드 뉴스 봇 v1.0
