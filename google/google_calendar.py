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


def get_new_credentials(credentials_path, scopes, token_path):
    """
    새로운 인증 흐름을 통해 Google Credentials를 발급받고 저장합니다.

    Args:
        credentials_path (str): credentials.json 파일 경로.
        scopes (list): 필요한 Google API 스코프 목록.
        token_path (str): 발급받은 토큰을 저장할 token.json 파일 경로.

    Returns:
        google.oauth2.credentials.Credentials: 새로 발급받은 인증 객체.
    """
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, scopes)
        creds = flow.run_local_server(port=0)
        
        # 인증 정보를 token.json 파일에 저장
        # cred_folder는 호출하는 곳에서 이미 존재하거나 생성될 것이므로 여기서는 os.makedirs 생략
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print(f"✅ 새 인증 정보가 '{token_path}'에 저장됨.")
        return creds
    except Exception as e:
        print(f"🚨 새로운 인증 과정 중 오류 발생: {e}")
        raise # 인증 실패 시 프로그램 중단


def google_calendar_login():
    """
    Google Calendar API에 인증하고 서비스 객체를 반환합니다.
    Refresh 토큰 만료 시 token.json을 삭제하고 새로 인증을 시도합니다.

    Returns:
        googleapiclient.discovery.Resource: Google Calendar API 서비스 객체.
    """
    creds = None
    cred_folder = 'google/cred/'
    token_path = os.path.join(cred_folder, 'token.json')
    credentials_path = os.path.join(cred_folder, 'credentials.json')

    # 기존 인증 토큰 파일(token.json)이 있는 경우 로드
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # 인증이 없거나 만료된 경우 새로 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # 토큰 갱신 시도
            try:
                creds.refresh(Request())  # 토큰 갱신
            except Exception as e:
                print("Refresh 토큰이 무효화되었거나 만료되었을 수 있습니다. 새로 인증을 시도합니다.")
                # token.json 파일을 삭제하고 새로 인증을 받도록 get_new_credentials 호출
                if os.path.exists(token_path):
                    os.remove(token_path)
                creds = get_new_credentials(credentials_path, SCOPES, token_path)
        else:
            # 기존에 토큰이 없거나, 유효하지 않거나, refresh_token이 없는 경우
            creds = get_new_credentials(credentials_path, SCOPES, token_path)

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
        'summary': f"{company_name} {os.getenv('JOB_TITLE', '직무')} 마감", # '직무' 부분 추가
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Seoul',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Seoul',
        },
        'reminders': { # 알림 추가
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 30}, # 30분 전 팝업
                {'method': 'popup', 'minutes': 1440}, # 24시간 전 팝업
            ],
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
            # 시스템 엔지니어 직무는 summary에 반영하고 description은 원본 유지
            job_title_description = f"{value['subtitle']}\n{base_url}/{key}"
            create_event(service, calendar_id, value["company_name"], value["date"], job_title_description)

    print("✅ 모든 새 공고 일정 등록 완료!")