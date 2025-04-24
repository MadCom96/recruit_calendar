from google.google_calendar import google_calendar_login, get_or_create_calendar

def delete_all_events(service, calendar_id):
    """
    Google Calendar에서 특정 캘린더의 모든 이벤트를 삭제합니다.

    Args:
        service (googleapiclient.discovery.Resource): Google Calendar API 서비스 객체.
        calendar_id (str): 이벤트를 삭제할 캘린더의 ID.
    """
    # Google Calendar API를 통해 이벤트 목록 가져오기
    events_result = service.events().list(
        calendarId=calendar_id,
        maxResults=2500,  # 최대 2500개의 이벤트 가져오기
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        print("📅 삭제할 일정이 없습니다.")
        return

    # 모든 이벤트 삭제
    for event in events:
        event_id = event['id']
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print(f"🗑️ 삭제된 이벤트: {event.get('summary', '제목 없음')}")

    print("✅ 모든 일정이 삭제되었습니다.")


def main():
    print("📂 recruit_schedule 캘린더 초기화 시작!")

    # Google Calendar API 로그인
    service = google_calendar_login()

    # recruit_schedule 캘린더 ID 가져오기
    calendar_id = get_or_create_calendar(service)

    # 캘린더의 모든 일정 삭제
    delete_all_events(service, calendar_id)

    print("✅ 캘린더 초기화 완료!")


if __name__ == "__main__":
    main()