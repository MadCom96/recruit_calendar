from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

class Parser:
    @staticmethod
    def calendar(html):
        # HTML 문자열을 BeautifulSoup 객체로 파싱
        soup = BeautifulSoup(html, "lxml")

        # 모든 calendar-item 선택
        calendar_items = soup.select(".calendar-item")

        # 결과 저장 리스트
        results = {}

        for item in calendar_items:
            # employment_id 추출
            employment_id = item.get("employment_id", "ID 없음")

            # 정확하게 즐겨찾기 여부 판단
            class_list = item.get("class", [])
            is_favorite = "favorite" in class_list and "no-favorite" not in class_list

            if not is_favorite:
                continue

            # 회사 이름 추출
            company_name_tag = item.select_one(".company-name span")
            company_name = company_name_tag.get_text(strip=True) if company_name_tag else "회사 이름 없음"

            # 링크 추출
            link_tag = item.select_one("a.company")
            link = link_tag["href"] if link_tag else "링크 없음"

            results[employment_id] = {
                "company_name": company_name,
                "link": link,
            }

        print(results)
        return results

    @staticmethod
    def extract_exp_time(html):
        """
        HTML에서 마감 시간과 subtitle 텍스트를 추출합니다.

        Args:
            html (str): HTML 소스 코드.

        Returns:
            tuple: (마감 시간 datetime 객체, subtitle 텍스트) 또는 (None, None) 반환.
        """
        soup = BeautifulSoup(html, "lxml")

        # subtitle 텍스트 추출
        subtitle_tag = soup.find("h1", class_="header4 text-gray-900 mb-[4px]")
        subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else None

        # .body5 클래스 div 모두 검색
        time_divs = soup.find_all("div", class_="body5")

        for time_div in time_divs:
            spans = time_div.find_all("span")
            for i, span in enumerate(spans):
                if span.get_text(strip=True) == "~" and i + 1 < len(spans):
                    try:
                        end_text = spans[i + 1].get_text(strip=True)  # "2025년 4월 28일 17:00"
                        # 문자열을 datetime 객체로 변환
                        exp_dt = datetime.strptime(end_text, "%Y년 %m월 %d일 %H:%M")
                        return exp_dt, subtitle
                    except Exception as e:
                        print(f"[ERROR] 날짜 파싱 실패: {e}")
                        return None

        return None

