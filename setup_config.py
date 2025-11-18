"""
설정 파일을 쉽게 생성하고 수정하는 스크립트
"""
import json
import os
import sys
from pathlib import Path

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def print_header():
    print("=" * 60)
    print("네이버 블로그 자동화 프로그램 설정 도우미")
    print("=" * 60)
    print()

def load_existing_config():
    """기존 config.json 로드"""
    config_path = Path("config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    """설정 저장"""
    config_path = Path("config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 설정이 {config_path}에 저장되었습니다!")

def setup_naver(config):
    """네이버 설정"""
    print("\n[1] 네이버 계정 설정")
    print("-" * 60)
    
    naver = config.get("naver", {})
    
    current_id = naver.get("id", "")
    if current_id and current_id != "네이버_아이디":
        print(f"현재 ID: {current_id}")
    id_input = input("네이버 ID (변경하지 않으려면 Enter): ").strip()
    if id_input:
        naver["id"] = id_input
    
    current_pw = naver.get("password", "")
    if current_pw and current_pw != "네이버_비밀번호":
        print("비밀번호: (이미 설정됨)")
    pw_input = input("네이버 비밀번호 (변경하지 않으려면 Enter): ").strip()
    if pw_input:
        naver["password"] = pw_input
    
    current_url = naver.get("blog_url", "")
    if current_url and current_url != "https://blog.naver.com/your_blog_id":
        print(f"현재 블로그 URL: {current_url}")
    url_input = input("블로그 URL (예: https://blog.naver.com/your_blog_id, 변경하지 않으려면 Enter): ").strip()
    if url_input:
        naver["blog_url"] = url_input
    
    config["naver"] = naver

def setup_openai(config):
    """OpenAI 설정"""
    print("\n[2] OpenAI API 설정")
    print("-" * 60)
    
    openai = config.get("openai", {})
    
    current_key = openai.get("api_key", "")
    if current_key and current_key != "sk-your-openai-api-key":
        print("API 키: (이미 설정됨)")
    key_input = input("OpenAI API 키 (변경하지 않으려면 Enter): ").strip()
    if key_input:
        openai["api_key"] = key_input
    
    print("\n모델 선택:")
    print("1. gpt-4 (기본값, 고품질)")
    print("2. gpt-4-turbo (빠름)")
    print("3. gpt-3.5-turbo (저렴함)")
    model_choice = input("선택 (1-3, 기본값: 1): ").strip()
    model_map = {"1": "gpt-4", "2": "gpt-4-turbo", "3": "gpt-3.5-turbo"}
    if model_choice in model_map:
        openai["model"] = model_map[model_choice]
    elif not openai.get("model"):
        openai["model"] = "gpt-4"
    
    config["openai"] = openai

def setup_scheduler(config):
    """스케줄러 설정"""
    print("\n[3] 스케줄러 설정")
    print("-" * 60)
    
    scheduler = config.get("scheduler", {})
    
    current_enabled = scheduler.get("enabled", False)
    print(f"현재 스케줄러: {'활성화' if current_enabled else '비활성화'}")
    enable_input = input("스케줄러 활성화? (y/n, 기본값: n): ").strip().lower()
    if enable_input == 'y':
        scheduler["enabled"] = True
        
        current_times = scheduler.get("default_posting_times", ["09:00", "14:00", "20:00"])
        print(f"\n현재 포스팅 시간: {', '.join(current_times)}")
        print("예시: 09:00,14:00,20:00 (쉼표로 구분)")
        times_input = input("포스팅 시간 설정 (변경하지 않으려면 Enter): ").strip()
        if times_input:
            times = [t.strip() for t in times_input.split(',')]
            scheduler["default_posting_times"] = times
    else:
        scheduler["enabled"] = False
    
    config["scheduler"] = scheduler

def setup_posting(config):
    """포스팅 설정"""
    print("\n[4] 포스팅 설정")
    print("-" * 60)
    
    posting = config.get("posting", {})
    
    current_category = posting.get("default_category", "일반")
    print(f"현재 기본 카테고리: {current_category}")
    category_input = input("기본 카테고리 (변경하지 않으려면 Enter): ").strip()
    if category_input:
        posting["default_category"] = category_input
    
    current_max = posting.get("max_posts_per_day", 5)
    print(f"현재 하루 최대 포스팅 수: {current_max}")
    max_input = input("하루 최대 포스팅 수 (변경하지 않으려면 Enter): ").strip()
    if max_input:
        try:
            posting["max_posts_per_day"] = int(max_input)
        except:
            print("잘못된 입력입니다. 기본값 유지")
    
    config["posting"] = posting

def setup_comment_reply(config):
    """댓글 자동 답변 설정"""
    print("\n[5] 댓글 자동 답변 설정")
    print("-" * 60)
    
    comment = config.get("comment_auto_reply", {})
    
    current_enabled = comment.get("enabled", False)
    print(f"현재 댓글 자동 답변: {'활성화' if current_enabled else '비활성화'}")
    enable_input = input("댓글 자동 답변 활성화? (y/n, 기본값: n): ").strip().lower()
    if enable_input == 'y':
        comment["enabled"] = True
    else:
        comment["enabled"] = False
    
    config["comment_auto_reply"] = comment

def main():
    print_header()
    
    # 기존 설정 로드
    config = load_existing_config()
    
    # 기본값 설정 (없는 경우)
    if not config:
        print("새로운 설정 파일을 생성합니다.\n")
        config = {
            "naver": {},
            "openai": {},
            "posting": {},
            "seo": {},
            "image": {},
            "scheduler": {},
            "advanced": {},
            "comment_auto_reply": {}
        }
    
    # 필수 설정
    setup_naver(config)
    setup_openai(config)
    
    # 선택 설정
    print("\n" + "=" * 60)
    print("추가 설정을 변경하시겠습니까?")
    print("=" * 60)
    
    setup_scheduler(config)
    setup_posting(config)
    setup_comment_reply(config)
    
    # 기본값 설정 (없는 경우)
    if "seo" not in config or not config["seo"]:
        config["seo"] = {
            "auto_optimize_title": True,
            "auto_generate_description": True,
            "auto_tags_count": 10,
            "keyword_density_check": True
        }
    
    if "image" not in config or not config["image"]:
        config["image"] = {
            "auto_collect": True,
            "max_images_per_post": 5,
            "image_optimization": True,
            "resize_width": 800,
            "resize_height": 600
        }
    
    if "advanced" not in config or not config["advanced"]:
        config["advanced"] = {
            "use_undetected_chromedriver": True,
            "headless_mode": False,
            "delay_between_actions": 2,
            "random_delay": True
        }
    
    if "posting" not in config or not config["posting"]:
        posting = config.get("posting", {})
        posting.setdefault("auto_tags", True)
        posting.setdefault("auto_internal_links", True)
        posting.setdefault("auto_widgets", True)
        posting.setdefault("posting_interval_minutes", 60)
        posting.setdefault("is_public", True)
        posting.setdefault("allow_comments", True)
        posting.setdefault("scheduled_time", None)
        posting.setdefault("thumbnail_image", None)
    
    if "comment_auto_reply" not in config or not config["comment_auto_reply"]:
        comment = config.get("comment_auto_reply", {})
        comment.setdefault("reply_tone", "친절하고 정중한")
        comment.setdefault("max_reply_length", 200)
        comment.setdefault("skip_keywords", ["광고", "홍보", "스팸", "링크", "사이트"])
    
    # 저장
    save_config(config)
    
    print("\n" + "=" * 60)
    print("설정 완료!")
    print("=" * 60)
    print("\n다음 명령어로 프로그램을 실행하세요:")
    print("  python main.py")
    print("\n설정 파일 위치: " + str(Path("config.json").absolute()))
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n설정이 취소되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")

