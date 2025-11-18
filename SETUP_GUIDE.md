# 네이버 블로그 자동화 프로그램 설치 가이드

## 📋 준비물 체크리스트

### 필수 항목
- [ ] Python 3.8 이상 설치
- [ ] 네이버 계정 (테스트용)
- [ ] OpenAI API 키 (원고 생성용)
- [ ] Chrome 브라우저 설치

### 선택 항목
- [ ] VS Code 또는 다른 코드 에디터
- [ ] Git (버전 관리용)

## 🚀 설치 단계

### 1단계: Python 설치 확인
```bash
python --version
```
Python 3.8 이상이어야 합니다.

### 2단계: 프로젝트 디렉토리로 이동
```bash
cd "C:\Users\LENOVO\Desktop\Moon\Development\NaverBlog"
```

### 3단계: 가상환경 생성 (권장)
```bash
python -m venv venv
venv\Scripts\activate
```

### 4단계: 패키지 설치
```bash
pip install -r requirements.txt
```

### 5단계: 설정 파일 생성
```bash
copy config.json.example config.json
```

### 6단계: config.json 수정
`config.json` 파일을 열어서 다음 정보를 입력하세요:

```json
{
  "naver": {
    "id": "실제_네이버_아이디",
    "password": "실제_네이버_비밀번호",
    "blog_url": "https://blog.naver.com/실제_블로그_ID"
  },
  "openai": {
    "api_key": "sk-실제_OpenAI_API_키",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**보안 강화 (선택사항):** 비밀번호를 환경변수로 설정할 수 있습니다:
- Windows: `set NAVER_ID=아이디` 및 `set NAVER_PASSWORD=비밀번호`
- Linux/Mac: `export NAVER_ID="아이디"` 및 `export NAVER_PASSWORD="비밀번호"`

## 🎯 사용 방법

### 기본 실행
```bash
python main.py
```

### 스케줄러 모드
`config.json`에서 `scheduler.enabled`를 `true`로 설정하면 자동으로 예약 발행됩니다.

## ⚙️ 주요 설정 옵션

### 포스팅 설정
- `posting_interval_minutes`: 포스팅 간격 (분)
- `max_posts_per_day`: 하루 최대 포스팅 수
- `auto_tags`: 태그 자동 생성 여부
- `auto_internal_links`: 내부 링크 자동 삽입 여부

### SEO 설정
- `auto_optimize_title`: 제목 자동 최적화
- `auto_generate_description`: 설명 자동 생성
- `auto_tags_count`: 자동 생성 태그 개수

### 이미지 설정
- `auto_collect`: 이미지 자동 수집 여부
- `max_images_per_post`: 포스팅당 최대 이미지 수
- `image_optimization`: 이미지 최적화 여부

### 고급 설정
- `headless_mode`: 브라우저 숨김 모드
- `delay_between_actions`: 동작 간 딜레이 (초)
- `random_delay`: 랜덤 딜레이 사용 여부

## 🔧 문제 해결

### ChromeDriver 오류
```bash
pip install webdriver-manager
```

### OpenAI API 오류
- API 키가 올바른지 확인
- 계정에 충분한 크레딧이 있는지 확인

### 로그인 실패
- 네이버 계정 정보 확인
- 2단계 인증이 설정되어 있으면 일시적으로 해제

## 📝 주의사항

1. **이용약관 준수**: 네이버 이용약관을 반드시 확인하세요
2. **자연스러운 사용**: 과도한 자동화는 계정 차단 위험이 있습니다
3. **고품질 콘텐츠**: 자동 생성된 콘텐츠도 검토 후 발행하세요
4. **테스트 먼저**: 실제 계정에 적용하기 전에 테스트 계정으로 먼저 시도하세요

## 🆘 도움말

문제가 발생하면 `logs/` 폴더의 로그 파일을 확인하세요.

