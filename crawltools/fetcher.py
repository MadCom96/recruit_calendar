from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time
import atexit

class Fetcher:
    def __init__(self, timeout=5):
        self.timeout = timeout
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 필요 시 사용
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        self.driver_service = Service("./chromedriver/chromedriver")
        self.driver = webdriver.Chrome(service=self.driver_service, options=chrome_options)

        # 프로그램 종료 시 자동으로 드라이버 종료
        atexit.register(self.close_driver)

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("[INFO] Selenium 드라이버 종료")

    def fetch_with_selenium(self, url):
        try:
            self.driver.get(url)
            time.sleep(3)
            return self.driver.page_source
        except Exception as e:
            print(f"[ERROR] 페이지 로딩 실패: {e}")
            return None

    def selenium_with_kakao_login(self, url, kakao_id, kakao_pw):
        try:
            self.driver.get(url)
            time.sleep(2)

            # 1. 로그인 버튼 클릭
            login_button = self.driver.find_element(By.CSS_SELECTOR, ".sign-in-button.btn")
            login_button.click()
            time.sleep(1)

            # 2. 카카오 로그인 버튼 클릭
            kakao_button = self.driver.find_element(By.CSS_SELECTOR, ".ga-sign-in-with-kakao")
            kakao_button.click()
            time.sleep(2)

            # 3. 카카오 로그인 창으로 전환
            self.driver.switch_to.window(self.driver.window_handles[-1])

            # 4. 아이디/비밀번호 입력
            id_input = self.driver.find_element(By.ID, "loginId--1")
            id_input.send_keys(kakao_id)
            pw_input = self.driver.find_element(By.ID, "password--2")
            pw_input.send_keys(kakao_pw)

            # 5. 로그인 버튼 클릭
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button.submit")
            login_btn.click()

            time.sleep(10)  # 로그인 완료 대기

            return self.driver.page_source

        except Exception as e:
            print(f"[ERROR] 카카오 로그인 실패: {e}")
            return None
