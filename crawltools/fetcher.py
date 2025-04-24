from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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

    def selenium_with_login(self, url, user_id, user_pw):
        """
        일반 로그인 기능을 수행하고 HTML 소스를 반환합니다.

        Args:
            url (str): 로그인 페이지 URL.
            user_id (str): 사용자 ID.
            user_pw (str): 사용자 비밀번호.

        Returns:
            str: 로그인 후의 HTML 소스.
        """
        try:
            # 로그인 페이지로 이동
            self.driver.get(url)
            time.sleep(2)

            # 1. 로그인 버튼 클릭
            login_button = self.driver.find_element(By.CSS_SELECTOR, ".sign-in-button.btn")
            login_button.click()
            print("[INFO] 로그인 버튼 클릭 완료")
            time.sleep(2)  # 모달 창 로드 대기

            # 2. 모달 창 찾기
            modal = self.driver.find_element(By.CSS_SELECTOR, "div.sign-modal-container")
            print("[INFO] 모달 창 찾기 완료")

            # 3. 모달 창 내부의 아이디 입력
            id_input = modal.find_element(By.CSS_SELECTOR, "input[placeholder='이메일 주소를 입력해 주세요']")
            id_input.send_keys(user_id)
            print("[INFO] 아이디 입력 완료")

            # 4. 모달 창 내부의 비밀번호 입력
            pw_input = modal.find_element(By.CSS_SELECTOR, "input[placeholder='비밀번호를 입력해 주세요']")
            pw_input.send_keys(user_pw)
            print("[INFO] 비밀번호 입력 완료")

            # 5. 모달 창 내부의 로그인 버튼 클릭
            modal_login_button = modal.find_element(By.CSS_SELECTOR, "a.sign-in-btn[ng-click='signin()']")
            modal_login_button.click()
            print("[INFO] 로그인 버튼 클릭 완료")

            # 로그인 완료 대기
            time.sleep(10)

            # 로그인 후 HTML 반환
            return self.driver.page_source

        except NoSuchElementException as e:
            print(f"[ERROR] 로그인 요소를 찾을 수 없습니다: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] 일반 로그인 중 오류 발생: {e}")
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

    def selenium_next_page(self):
        """
        셀레니움으로 다음 페이지 버튼을 클릭하고 HTML을 가져옵니다.

        Returns:
            str: 다음 페이지의 HTML 소스.
        """
        try:
            # 다음 페이지 버튼 찾기
            next_button = self.driver.find_element(By.CSS_SELECTOR, "div.icon-wrapper img[ng-click='addMonth(1)']")
            
            # 버튼 클릭
            next_button.click()
            print("[INFO] 다음 페이지 버튼 클릭 완료")

            # 페이지 로드 대기
            time.sleep(5)

            # 현재 페이지의 HTML 반환
            return self.driver.page_source
        except NoSuchElementException:
            
            print("[ERROR] 다음 페이지 버튼을 찾을 수 없습니다.")
            return None
        except TimeoutException:
            print("[ERROR] 페이지 로드가 시간 초과되었습니다.")
            return None
        except Exception as e:
            print(f"[ERROR] 다음 페이지로 이동 중 오류 발생: {e}")
            return None
