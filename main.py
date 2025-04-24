from google.google_calendar import (
    google_calendar_login,
    get_or_create_calendar,
    get_all_events,
    create_events
)
from crawltools.crawler import Crawler, START_URL

def main():
    print("📂 자소설 마감 일정 등록 시작!")

    # 0. 크롤러
    crawler = Crawler()

    # 1. 크롤링 데이터 가져오기
    base_url = START_URL
    posts = crawler.get_all_stars()  # 크롤링된 공고 데이터
    print(posts)

    # 2. Google Calendar API 로그인
    service = google_calendar_login()

    # 3. recruit_schedule 캘린더에 접근하거나 생성, 모든 일정 가져오기
    calendar_id = get_or_create_calendar(service)
    saved = get_all_events(service, calendar_id)

    # 4. 새로 생긴 공고만 구분
    ids = set(posts.keys()).difference(saved)  # 새로 추가된 공고 ID
    crawler.add_times(posts, ids)

    # 5. 새로 추가된 공고를 캘린더에 등록
    create_events(service, calendar_id, posts, ids, base_url)

    print("✅ 모든 작업 완료!")


if __name__ == "__main__":
    main()
