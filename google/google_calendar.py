import os
import pytz
import re
from datetime import timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Calendar API 권한 설정
SCOPES = ['https://www.googleapis.com/auth/calendar']


def google_calendar_login():
    """
    Google Calendar API에 인증하고 서비스 객체를 반환합니다.

    Returns:
        googleapiclient.discovery.Resource: Google Calendar API 서비스 객체.
    """
    creds = None
    # credentials.json과 token.json의 경로를 google/cred/로 설정
    cred_folder = 'google/cred/'
    token_path = os.path.join(cred_folder, 'token.json')
    credentials_path = os.path.join(cred_folder, 'credentials.json')

    # 기존 인증 토큰 파일(token.json)이 있는 경우 로드
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # 인증이 없거나 만료된 경우 새로 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # 토큰 갱신
        else:
            # 새로 인증을 수행
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # 인증 정보를 token.json 파일에 저장
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    # Google Calendar API 서비스 객체 생성
    service = build('calendar', 'v3', credentials=creds)
    return service


def get_or_create_calendar(service, calendar_name='recruit_schedule'):
    """
    Google Calendar에서 특정 이름의 캘린더를 가져오거나, 없으면 새로 생성합니다.

    Args:
        service (googleapiclient.discovery.Resource): Google Calendar API 서비스 객체.
        calendar_name (str): 생성하거나 가져올 캘린더의 이름. 기본값은 'recruit_schedule'.

    Returns:
        str: 캘린더 ID.
    """
    # 1. 캘린더 목록 가져오기
    calendars = service.calendarList().list().execute().get('items', [])
    for calendar in calendars:
        if calendar['summary'] == calendar_name:
            print(f"📅 '{calendar_name}' 캘린더가 이미 존재합니다.")
            return calendar['id']  # 캘린더 ID 반환

    # 2. 캘린더가 없으면 새로 생성
    print(f"📅 '{calendar_name}' 캘린더가 존재하지 않습니다. 새로 생성합니다.")
    new_calendar = {
        'summary': calendar_name,
        'timeZone': 'Asia/Seoul'
    }
    created_calendar = service.calendars().insert(body=new_calendar).execute()
    print(f"✅ '{calendar_name}' 캘린더 생성 완료: {created_calendar['id']}")
    return created_calendar['id']  # 새로 생성된 캘린더 ID 반환


def get_all_events(service, calendar_id):
    """
    Google Calendar에서 모든 이벤트를 가져와, description 필드에서 recruit/ 뒤의 숫자를 추출하여 set으로 반환.

    Args:
        service (googleapiclient.discovery.Resource): Google Calendar API 서비스 객체.
        calendar_id (str): 캘린더의 ID.

    Returns:
        set: recruit/ 뒤의 숫자로 구성된 집합.
    """
    # Google Calendar API를 통해 이벤트 목록 가져오기
    events_result = service.events().list(
        calendarId=calendar_id,
        maxResults=2500,  # 최대 2500개의 이벤트 가져오기
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    recruit_ids = set()  # recruit/ 뒤의 숫자를 저장할 set

    if not events:
        print("📅 가져올 일정이 없습니다.")
    else:
        for event in events:
            description = event.get('description', '')  # description 필드 가져오기
            match = re.search(r'recruit/(\d+)', description)  # recruit/ 뒤의 숫자 추출
            if match:
                recruit_ids.add(match.group(1))  # 숫자를 set에 추가

    print(f"📅 recruit/ 뒤의 숫자 ID: {recruit_ids}")
    return recruit_ids


def create_event(service, calendar_id, company_name, deadline, description="자소설 마감 일정입니다"):
    """
    Google Calendar에 새로운 이벤트를 생성합니다.

    Args:
        service (googleapiclient.discovery.Resource): Google Calendar API 서비스 객체.
        calendar_id (str): 이벤트를 추가할 캘린더의 ID.
        company_name (str): 회사 이름.
        deadline (datetime): 마감 시간.
        description (str): 이벤트 설명. 기본값은 "자소설 마감 일정입니다".
    """
    local_tz = pytz.timezone('Asia/Seoul')  # 한국 시간대 설정
    end_time = local_tz.localize(deadline)  # 마감 시간 설정
    start_time = end_time - timedelta(minutes=5)  # 시작 시간은 마감 5분 전

    # 이벤트 데이터 생성
    event = {
        'summary': f"{company_name} 마감",
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Seoul',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Seoul',
        },
    }

    # Google Calendar에 이벤트 추가
    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"✅ {company_name} 일정 등록됨: {created_event.get('htmlLink')}")

def create_events(service, calendar_id, posts, ids, base_url):
    """
    새로 추가된 공고만 Google Calendar에 이벤트로 등록합니다.

    Args:
        service (googleapiclient.discovery.Resource): Google Calendar API 서비스 객체.
        calendar_id (str): 이벤트를 추가할 캘린더의 ID.
        posts (dict): 크롤링된 공고 데이터.
        ids (set): 새로 추가된 공고 ID 집합.
        base_url (str): 공고 상세 URL의 기본 경로.
    """
    # 새로 추가된 공고만 캘린더에 업로드
    while ids:
        key = ids.pop()
        value = posts[key]
        if value["date"]:  # 날짜가 있는 경우에만 이벤트 생성
            create_event(service, calendar_id, value["company_name"], value["date"], f'{value["subtitle"]}\n{base_url}/{key}')

    print("✅ 모든 새 공고 일정 등록 완료!")