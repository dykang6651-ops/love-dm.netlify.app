# -*- coding: utf-8 -*-
"""schedule.py 일정으로 홈 일정 카드·일정표·신청 버튼, 하단 신청 바, 행사 구조화 데이터를 만든다.

빌드 시점에 지난 회차는 빼고, 페이지가 열릴 때 assets/live.js가
시작 시각이 지난 회차(data-at)를 한 번 더 지운다.
"""
import html
import json
from datetime import datetime, timedelta, timezone

from schedule import EVENTS, PRICE, KAKAO

KST = timezone(timedelta(hours=9))
WD = "월화수목금토일"
CITY_ORDER = {"대전": 0, "논산": 1}
REGION = {"대전": "대전광역시", "논산": "충청남도"}
STATUSES = ("모집 중", "마감 임박", "남성 마감", "여성 마감", "마감")


def e(s):
    return html.escape(str(s), quote=True)


def dt(ev):
    return datetime.strptime(f'{ev["date"]} {ev["time"]}', "%Y-%m-%d %H:%M").replace(tzinfo=KST)


def iso(ev):
    return dt(ev).isoformat()


def day_label(ev):
    d = dt(ev)
    return f"{d.month}월 {d.day}일 ({WD[d.weekday()]})"


def time_label(ev):
    d = dt(ev)
    h = d.hour
    ap = "오전" if h < 12 else "오후"
    h12 = h % 12 or 12
    return f"{ap} {h12}시" + (f" {d.minute}분" if d.minute else "")


def upcoming(now=None):
    now = now or datetime.now(KST)
    evs = [ev for ev in EVENTS if dt(ev) > now]
    return sorted(evs, key=lambda ev: (dt(ev), CITY_ORDER.get(ev["city"], 9)))


def groups(evs):
    """같은 날짜·시각 회차끼리 묶는다."""
    out = []
    for ev in evs:
        if out and dt(out[-1][0]) == dt(ev):
            out[-1].append(ev)
        else:
            out.append([ev])
    return out


def status(ev):
    s = ev.get("status") or "모집 중"
    return s if s in STATUSES else "모집 중"


def closed(ev):
    return status(ev) == "마감"


def group_status(g):
    labels = [status(ev) for ev in g]
    for want in ("마감 임박", "모집 중", "남성 마감", "여성 마감"):
        if want in labels:
            return want
    return "마감"


def group_line(g):
    """'대전·논산 모집 중' 또는 '대전 마감 임박 · 논산 모집 중'."""
    labels = {status(ev) for ev in g}
    if len(labels) == 1:
        return "·".join(ev["city"] for ev in g) + " " + labels.pop()
    return " · ".join(f'{ev["city"]} {status(ev)}' for ev in g)


# ------------------------------------------------------------------ 홈 블록 (홈은 인라인 스타일, 움직임은 assets/home.css)
BADGE_COLOR = {"모집 중": "#C81E5B", "마감 임박": "#18141C", "남성 마감": "#8A8190", "여성 마감": "#8A8190", "마감": "#8A8190"}


def badge(label, size=13):
    return (f'<span class="badge" style="background: {BADGE_COLOR[label]}; color: #FFFFFF; font-weight: 700; '
            f'font-size: {size}px; padding: 5px 13px; border-radius: 999px; white-space: nowrap">{e(label)}</span>')


def home_next(evs):
    """첫 화면의 '다음 소개팅' 카드."""
    card = "background: linear-gradient(135deg, #221B27 0%, #18141C 100%); color: #FFFFFF; border-radius: 20px; padding: 22px 26px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px"
    out = ['<div data-pick style="display: contents">']
    for i, g in enumerate(groups(evs)):
        cities = " · ".join(ev["city"] for ev in g)
        label = group_status(g)
        if label == "마감 임박":
            label_html = badge(label, 14).replace("background: #18141C", "background: #C81E5B")
        else:
            label_html = badge(label, 14)
        out.append(
            f'<a href="#schedule" class="nx" data-at="{iso(g[0])}"{" hidden" if i else ""} style="{card}; text-decoration: none">'
            f'<div><p style="margin: 0; font-size: 13px; color: #F5C9D7; font-weight: 700; letter-spacing: .04em">다음 소개팅</p>'
            f'<p style="margin: 2px 0 0; font-size: 20px; font-weight: 700">{e(day_label(g[0]))} {e(time_label(g[0]))} · {e(cities)}</p></div>'
            f'{label_html}</a>')
    out.append(
        f'<div data-empty{"" if not evs else " hidden"} style="{card}">'
        '<div><p style="margin: 0; font-size: 13px; color: #F5C9D7; font-weight: 700">다음 소개팅</p>'
        '<p style="margin: 2px 0 0; font-size: 20px; font-weight: 700">새 일정을 준비하고 있어요</p></div></div>')
    out.append("</div>")
    return "\n".join(out)


def home_cards(evs):
    """일정표 카드. 가장 가까운 날짜는 class="near"(굵은 테두리)."""
    first = dt(evs[0]) if evs else None
    out = ['<div data-list style="margin-top: 40px; display: flex; flex-wrap: wrap; gap: 20px">']
    for ev in evs:
        near = " near" if dt(ev) == first else ""
        if closed(ev):
            btn = '<span class="btn-card off">마감되었어요</span>'
        else:
            btn = f'<a href="{e(ev["form"])}" target="_blank" rel="noopener" class="btn-card">신청하기</a>'
        out.append(
            f'<div class="sc-card{near}" data-at="{iso(ev)}" data-day="{ev["date"]}T{ev["time"]}" style="flex: 1 1 360px; border-radius: 22px; padding: 30px">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; gap: 12px"><span style="font-weight: 700; color: #9C1546">{e(ev["city"])}</span>'
            f'{badge(status(ev))}</div>'
            f'<p style="margin: 10px 0 4px; font-size: 26px; font-weight: 900; letter-spacing: -0.5px">{e(day_label(ev))} {e(time_label(ev))}</p>'
            f'<p style="margin: 0; color: #5A5160">{e(ev["city"])} · 장소는 확정 문자로 안내</p>'
            f'{btn}</div>')
    out.append(
        f'<div data-empty{"" if not evs else " hidden"} style="flex: 1 1 100%; border: 1px dashed #F5C9D7; border-radius: 22px; padding: 30px; text-align: center; color: #5A5160">'
        '다음 일정을 준비하고 있어요. 곧 이 자리에 신청서가 열립니다.</div>')
    out.append("</div>")
    return "\n".join(out)


def home_apply(evs):
    """신청 띠의 버튼. 가장 가까운 회차의 신청서로 연결."""
    btn = "background: #FFFFFF; color: #9C1546; padding: 17px 32px; font-weight: 900; font-size: 18px"
    row = "margin-top: 32px; display: flex; flex-wrap: wrap; justify-content: center; gap: 12px"
    out = ['<div data-pick style="display: contents">']
    for i, g in enumerate(groups(evs)):
        links = []
        for ev in g:
            if closed(ev):
                links.append(f'<span class="btn off" style="{btn}; opacity: .6">{e(ev["city"])} 마감</span>')
            else:
                links.append(f'<a href="{e(ev["form"])}" target="_blank" rel="noopener" class="btn btn-w" style="{btn}">{e(ev["city"])} 신청서 작성하기</a>')
        out.append(f'<div data-at="{iso(g[0])}"{" hidden" if i else ""} style="{row}">{"".join(links)}</div>')
    out.append(f'<div data-empty{"" if not evs else " hidden"} style="{row}"><a href="#schedule" class="btn btn-w" style="{btn}">일정 확인하기</a></div>')
    out.append("</div>")
    return "\n".join(out)


def event_schema(evs, site, image):
    data = []
    for ev in evs:
        st = status(ev)
        offers = []
        for g, price in PRICE.items():
            sold = st == "마감" or st == f"{g}성 마감"
            offers.append({
                "@type": "Offer", "name": f"{g}성 참가비", "price": str(price), "priceCurrency": "KRW",
                "url": ev["form"], "validFrom": "2026-11-01T00:00:00+09:00",
                "availability": "https://schema.org/SoldOut" if sold else "https://schema.org/InStock"})
        data.append({
            "@context": "https://schema.org", "@type": "Event",
            "name": f'러브DM {ev["city"]} 로테이션 소개팅 ({day_label(ev)})',
            "description": f'{ev["city"]} 미혼 직장인 1:1 로테이션 소개팅. 재직 서류와 사진을 확인한 참가자가 정해진 시간마다 자리를 바꿔 대화하고, 서로 선택하면 대화방을 열어 드립니다.',
            "startDate": iso(ev),
            "endDate": (dt(ev) + timedelta(hours=2)).isoformat(),
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "location": {"@type": "Place", "name": f'{ev["city"]} (장소는 확정 문자로 안내)',
                         "address": {"@type": "PostalAddress", "addressLocality": ev["city"],
                                     "addressRegion": REGION.get(ev["city"], ev["city"]), "addressCountry": "KR"}},
            "image": [image],
            "offers": offers,
            "organizer": {"@type": "Organization", "name": "러브DM", "url": site + "/"},
        })
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=1) + "\n</script>"


# ------------------------------------------------------------------ 하단 바 (홈·서브페이지 공통)
def bar(evs, href):
    out = ['<div class="mbar" role="region" aria-label="빠른 신청"><div class="mbar-in">', '<div class="mbar-tx" data-pick>']
    for i, g in enumerate(groups(evs)):
        out.append(f'<p data-at="{iso(g[0])}"{" hidden" if i else ""}><b>{e(day_label(g[0]))} {e(time_label(g[0]))}</b><span>{e(group_line(g))}</span></p>')
    out.append(f'<p data-empty{"" if not evs else " hidden"}><b>다음 일정 준비 중</b><span>일정표에서 확인하세요</span></p>')
    out.append("</div>")
    if KAKAO:
        out.append(f'<a class="kk" href="{e(KAKAO)}" target="_blank" rel="noopener">카톡 문의</a>')
    out.append(f'<a class="go" href="{href}">신청하기</a>')
    out.append("</div></div>")
    return "\n".join(out)


def next_line(evs):
    """서브페이지 참가 정보의 '다음 일정' 칸."""
    out = ['<dd data-pick>']
    for i, g in enumerate(groups(evs)):
        out.append(f'<span data-at="{iso(g[0])}"{" hidden" if i else ""}>{e(day_label(g[0]))} {e(time_label(g[0]))}, {e(group_line(g))}</span>')
    out.append(f'<span data-empty{"" if not evs else " hidden"}>새 일정을 준비하고 있어요</span>')
    out.append("</dd>")
    return "".join(out)
