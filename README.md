# 네이버 블로그 자동화 프로그램

네이버 블로그 포스팅을 자동화하는 프로그램입니다.

## 주요 기능

### 1. 자동 포스팅
- AI 기반 원고 자동 생성
- 이미지 자동 수집 및 처리
- 예약 발행 기능

### 2. SEO 최적화
- 제목 최적화 (키워드 기반)
- 태그 자동 생성 및 삽입
- 설명(요약) 자동 생성
- 카테고리 선택

### 3. 콘텐츠 향상
- 부제목(H2, H3) 자동 삽입
- 목차 자동 생성
- 해시태그 자동 삽입

### 4. 링크 최적화
- 글 하단 내부 링크 자동 삽입
- 관련 글 링크 자동 연결
- 키워드 기반 내부 링크

### 5. 위젯 및 UI
- 소셜 공유 버튼
- 언론사 배지/로고 위젯

### 6. 고급 기능
- 포스팅 통계 (히스토리 기반)
- 에러 로깅
- 설정 파일 기반 관리
- 재시도 로직 (최대 3회)
- 포스팅 히스토리 관리
- 설정 검증 기능

### 7. 네이버 블로그 특화 기능
- 공개/비공개 설정
- 댓글 허용/비허용 설정
- 예약 발행 시간 설정
- 썸네일 이미지 설정
- 포스팅 URL 자동 추출 및 저장
- 랜덤 딜레이로 자연스러운 동작

### 8. 댓글 자동 답변 ⭐ (NEW)
- AI 기반 댓글 자동 답변 생성
- 스팸 댓글 자동 필터링
- 답변 톤 설정 가능 (친절하고 정중한, 캐주얼한 등)
- 답변 길이 제한 설정
- 포스팅 후 자동 처리 또는 수동 실행 가능

## 설치 방법

```bash
pip install -r requirements.txt
```

## 설정 방법

### 방법 1: config.json 사용 (권장)

1. `config.json.example` 파일을 `config.json`으로 복사
2. `config.json` 파일을 열어서 설정을 입력하세요
   - 네이버 계정 정보 입력
   - OpenAI API 키 입력 (원고 생성용)
   - 블로그 URL 입력

### 방법 2: 환경변수 사용 (보안 강화)

비밀번호를 환경변수로 설정하여 보안을 강화할 수 있습니다:

**Windows (PowerShell):**
```powershell
$env:NAVER_ID="your_naver_id"
$env:NAVER_PASSWORD="your_naver_password"
```

**Windows (CMD):**
```cmd
set NAVER_ID=your_naver_id
set NAVER_PASSWORD=your_naver_password
```

**Linux/Mac:**
```bash
export NAVER_ID="your_naver_id"
export NAVER_PASSWORD="your_naver_password"
```

환경변수가 설정되어 있으면 `config.json`의 값보다 우선적으로 사용됩니다.

### 댓글 자동 답변 설정

`config.json`에서 댓글 자동 답변 기능을 활성화할 수 있습니다:

```json
{
  "comment_auto_reply": {
    "enabled": true,
    "reply_tone": "친절하고 정중한",
    "max_reply_length": 200,
    "skip_keywords": ["광고", "홍보", "스팸", "링크", "사이트"]
  }
}
```

- `enabled`: 댓글 자동 답변 활성화 여부 (true/false)
- `reply_tone`: 답변 톤 설정 (예: "친절하고 정중한", "캐주얼한", "전문적인")
- `max_reply_length`: 최대 답변 길이 (자)
- `skip_keywords`: 해당 키워드가 포함된 댓글은 자동으로 건너뜀

## 사용 방법

### 기본 사용 (자동 포스팅)

```bash
python main.py
```

### 댓글 자동 답변만 실행

Python 코드에서 직접 호출:

```python
from naver_blog_automation.automation import NaverBlogAutomation
import json

# 설정 파일 로드
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 자동화 객체 생성
automation = NaverBlogAutomation(config)

# 로그인
if automation.login():
    # 모든 포스팅의 댓글 처리
    automation.process_all_comments()
    
    # 또는 특정 포스팅만 처리
    # automation.process_all_comments(["https://blog.naver.com/your_blog_id/123456"])
    
    automation.close()
```

## 주의사항

- 네이버 이용약관을 준수하세요
- 과도한 자동화는 계정 차단 위험이 있습니다
- 자연스러운 시간 간격으로 포스팅하세요
- 고품질 콘텐츠를 생성하세요

## 주요 개선 사항

### ✅ 완료된 개선
1. **랜덤 딜레이 기능**: 자연스러운 동작을 위한 랜덤 딜레이 적용
2. **재시도 로직**: 포스팅 실패 시 자동 재시도 (최대 3회)
3. **포스팅 히스토리**: 모든 포스팅 기록 저장 및 통계 제공
4. **설정 검증**: 시작 전 설정 파일 유효성 검사
5. **URL 추출**: 포스팅 성공 후 자동으로 URL 추출 및 저장
6. **네이버 블로그 특화**: 공개/비공개, 댓글, 예약 발행, 썸네일 설정
7. **댓글 자동 답변**: AI 기반 댓글 자동 답변 기능 구현

## 최신 기능

### 댓글 자동 답변 시스템 (v1.1.0)

AI 기반 댓글 자동 답변 기능이 추가되었습니다. 블로그 운영 시간을 절약하고 독자와의 소통을 자동화할 수 있습니다.

#### 주요 특징

- **AI 기반 답변 생성**: OpenAI GPT를 활용하여 댓글 내용에 맞는 자연스러운 답변 자동 생성
- **스팸 댓글 필터링**: 설정한 키워드가 포함된 댓글은 자동으로 건너뛰기
- **커스터마이징 가능**: 답변 톤, 길이, 필터링 키워드 등 자유롭게 설정
- **자동/수동 실행**: 포스팅 후 자동 처리 또는 별도 실행 가능
- **중복 답변 방지**: 이미 답변이 있는 댓글은 자동으로 건너뛰기

#### 사용 예시

```python
# 댓글 답변 테스트
python test_comment_reply.py

# 특정 포스팅의 댓글만 처리
automation.process_all_comments(["https://blog.naver.com/your_blog_id/123456"])
```

#### 설정 옵션

- `enabled`: 기능 활성화/비활성화
- `reply_tone`: 답변 톤 설정 ("친절하고 정중한", "캐주얼한", "전문적인" 등)
- `max_reply_length`: 최대 답변 길이 (기본값: 200자)
- `skip_keywords`: 스팸 필터링 키워드 리스트

