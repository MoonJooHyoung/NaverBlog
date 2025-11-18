"""
댓글 답변 생성 테스트 스크립트
실제로 어떤 답변이 생성되는지 테스트할 수 있습니다.
"""
import json
import logging
from naver_blog_automation.comment_manager import CommentManager
from selenium import webdriver

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_comment_replies():
    """댓글 답변 생성 테스트"""
    
    # 설정 파일 로드
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ config.json 파일을 찾을 수 없습니다.")
        print("config.json.example을 복사하여 config.json을 만드세요.")
        return
    
    # 드라이버 초기화 (실제로는 사용하지 않지만 CommentManager 초기화에 필요)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"❌ Chrome 드라이버 초기화 실패: {e}")
        print("드라이버 없이 테스트하려면 comment_manager.py의 generate_reply 메서드를 직접 수정하세요.")
        return
    
    # CommentManager 초기화
    comment_manager = CommentManager(driver, config)
    
    # 테스트할 댓글들
    test_comments = [
        {
            "comment": "좋은 글 감사합니다!",
            "post_title": "네이버 블로그 자동화 가이드"
        },
        {
            "comment": "이 내용이 정말 유용하네요. 도움이 많이 되었습니다.",
            "post_title": "Python 자동화 튜토리얼"
        },
        {
            "comment": "궁금한 점이 있는데요, 추가 설명이 가능할까요?",
            "post_title": "웹 크롤링 기초"
        },
        {
            "comment": "완전 대박이에요! 👍👍",
            "post_title": "최신 기술 트렌드"
        },
        {
            "comment": "광고 링크 클릭하세요! 무료 이벤트 진행중!",
            "post_title": "일반 포스팅"
        }
    ]
    
    print("=" * 60)
    print("댓글 답변 생성 테스트")
    print("=" * 60)
    print()
    
    for i, test_case in enumerate(test_comments, 1):
        comment = test_case["comment"]
        post_title = test_case["post_title"]
        
        print(f"[테스트 {i}]")
        print(f"포스팅 제목: {post_title}")
        print(f"댓글 내용: {comment}")
        print()
        
        # 스팸 필터링 체크
        if any(keyword in comment for keyword in comment_manager.skip_keywords):
            print("⚠️  스팸 댓글로 판단되어 답변하지 않습니다.")
            print()
            continue
        
        # 답변 생성
        try:
            reply = comment_manager.generate_reply(comment, post_title)
            print(f"생성된 답변: {reply}")
            print(f"답변 길이: {len(reply)}자")
        except Exception as e:
            print(f"❌ 답변 생성 오류: {e}")
        
        print()
        print("-" * 60)
        print()
    
    driver.quit()
    print("테스트 완료!")

if __name__ == "__main__":
    test_comment_replies()

