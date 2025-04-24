from crawltools.fetcher import Fetcher
from crawltools.parser import Parser
from dotenv import load_dotenv
import os

START_URL = "https://jasoseol.com/recruit"

# .env 파일 강제 재로드
load_dotenv(override=True)

class Crawler:
    def __init__(self):
        self.fetcher = Fetcher()

    def get_all_stars(self):
        print(f"\n시작 URL: {START_URL}")

        # .env에서 LOGIN_METHOD 값 읽기
        login_method = os.getenv("LOGIN_METHOD", "general").lower()  # 기본값은 "kakao"

        # Selenium으로 HTML 가져오기
        if login_method == "kakao":
            print("[INFO] 카카오 로그인")
            html = self.fetcher.selenium_with_kakao_login(
                START_URL, os.getenv("KAKAO_ID"), os.getenv("KAKAO_PW")
            )
        elif login_method == "general":
            print("[INFO] 일반 로그인")
            html = self.fetcher.selenium_with_login(
                START_URL, os.getenv("USER_ID"), os.getenv("USER_PW")
            )
        else:
            raise ValueError("[ERROR] LOGIN_METHOD 값이 잘못되었습니다. 'kakao' 또는 'general' 중 하나를 설정하세요.")

        # HTML 파싱
        results = Parser.calendar(html)

        # 다음 달 HTML 가져오기
        html = self.fetcher.selenium_next_page()

        # HTML 파싱
        next_results = Parser.calendar(html)

        for id, nresult in next_results.items():
            results[id] = nresult

        print(f"파싱 결과: ")
        print(*results.values(), sep="\n")
        return results

    def add_times(self, posts, ids):
        for id in ids:
            html = self.fetcher.fetch_with_selenium(f"{START_URL}/{id}")
            ext = Parser.extract_exp_time(html)
            posts[id]["date"] = ext[0]
            posts[id]["subtitle"] = ext[1]