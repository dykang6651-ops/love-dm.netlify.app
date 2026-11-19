# -*- coding: utf-8 -*-
"""소개팅 일정. 여기만 고치고 `python tools/build.py`를 돌리면
홈 첫 화면 초대장, 일정표, 신청 버튼, 모바일 하단 신청 바, 구글 행사 데이터(Event)가 함께 바뀐다.

- date: 행사 날짜(YYYY-MM-DD), time: 시작 시각(HH:MM)
- city: "대전" 또는 "논산"
- form: 그 날짜 신청서 주소(네이버 폼)
- status: 아래 다섯 가지 중 하나. 남은 자리 숫자는 보여 주지 않는다.
    "모집 중", "마감 임박", "남성 마감", "여성 마감", "마감"
    "마감"이면 신청 버튼이 꺼진다. "남성 마감"·"여성 마감"은 그 성별만 마감으로 안내한다.
- 지난 날짜는 빌드할 때 빠지고, 빌드를 안 해도 페이지가 열릴 때 시작 시각이 지난 회차는 숨겨진다.
"""

EVENTS = [
    {"date": "2026-11-14", "time": "20:00", "city": "대전", "form": "https://naver.me/GgUKj08Z", "status": "모집 중"},
    {"date": "2026-11-14", "time": "20:00", "city": "논산", "form": "https://naver.me/FUiLxZ8K", "status": "모집 중"},
    {"date": "2026-11-21", "time": "20:00", "city": "대전", "form": "https://naver.me/GO68nALn", "status": "모집 중"},
    {"date": "2026-11-21", "time": "20:00", "city": "논산", "form": "https://naver.me/xqbVpkl5", "status": "모집 중"},
]

# 참가비(원). 홈 참가비 표와 같은 값.
PRICE = {"남": 50000, "여": 30000}

# 카카오톡 채널 주소(예: "https://pf.kakao.com/_xxxxx"). 비워 두면 문의 버튼을 숨긴다.
KAKAO = ""
