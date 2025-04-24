from crawltools.fetcher import Fetcher
from crawltools.parser import Parser
from dotenv import load_dotenv
import os
import json

START_URL = "https://jasoseol.com/recruit"
load_dotenv(verbose=True)

class Crawler:
    def __init__(self):
        self.fetcher = Fetcher()

    def get_all_stars(self):
        print(f"\n시작 URL: {START_URL}")

        # Selenium으로 HTML 가져오기
        html = self.fetcher.selenium_with_kakao_login(START_URL, os.getenv("KAKAO_ID"), os.getenv("KAKAO_PW"))

        # HTML 파싱
        results = Parser.calendar(html)

        print(f"파싱 결과: ")
        print(*results.values(), sep="\n")
        return results

    def add_times(self, posts, ids):
        for id in ids:
            html = self.fetcher.fetch_with_selenium(f"{START_URL}/{id}")
            posts[id]["date"] = Parser.extract_exp_time(html)