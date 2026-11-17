# -*- coding: utf-8 -*-
"""키워드 서브페이지, sitemap.xml, robots.txt를 만든다.

    python tools/build.py

본문은 tools/pages.py, 공통 스타일은 assets/site.css에 있다.
"""
import html
import json
import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
from pages import PAGES, HUB  # noqa: E402
import events  # noqa: E402
from og import make_og  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://love-dm.netlify.app"
UPDATED = "2026-11-17"
BRAND = "러브DM"
FONTS = "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&amp;display=swap"

# 홈 일정표와 같은 값. 참가비나 요일이 바뀌면 여기만 고친다.
INFO = [
    ("일정", "매주 토요일 오후 8시, 대전·논산"),
    ("참가비", "남성 50,000원, 여성 30,000원"),
    ("할인", "동반 참석, 재참여 시 각 5,000원 할인"),
    ("확인", "재직 서류, 본인 사진, 미혼 여부"),
]

LOGO_SVG = ('<svg aria-hidden="true" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#C81E5B" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H9l-5 4V6a1 1 0 0 1 1-1z"></path>'
            '<path d="M12 14.2s-3-1.8-3-3.7A1.6 1.6 0 0 1 12 9.6a1.6 1.6 0 0 1 3 .9c0 1.9-3 3.7-3 3.7z"></path></svg>')

BY_SLUG = {p["slug"]: p for p in PAGES}
AREAS = [p for p in PAGES if p["kind"] == "area"]
TOPICS = [p for p in PAGES if p["kind"] == "topic"]
TARGETS = [p for p in PAGES if p["kind"] == "target"]
EVENTS = events.upcoming()


def og_url(name):
    return f"{SITE}/og/{quote(name)}.jpg"


def url(slug):
    return f"/{quote(slug)}/"


def abs_url(slug):
    return SITE + url(slug)


def e(s):
    return html.escape(s, quote=True)


def block(b):
    kind, body = b
    if kind == "p":
        return f"<p>{e(body)}</p>"
    tag = "ol" if kind == "ol" else "ul"
    items = "".join(f"<li><b>{e(t)}</b><span>{e(d)}</span></li>" for t, d in body)
    return f'<{tag} class="pts">{items}</{tag}>'


def link_cards(items, current):
    out = []
    for p in items:
        if p["slug"] == current:
            out.append(f'<li><span class="lk on" aria-current="page">{e(p["slug"])}</span></li>')
        else:
            out.append(f'<li><a class="lk" href="{url(p["slug"])}">{e(p["slug"])}</a></li>')
    return "".join(out)


def schema(p):
    crumbs = [{"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"}]
    if p["slug"] != HUB:
        crumbs.append({"@type": "ListItem", "position": 2, "name": HUB, "item": abs_url(HUB)})
    crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": p["slug"], "item": abs_url(p["slug"])})
    data = [
        {"@context": "https://schema.org", "@type": "WebPage", "name": p["title"], "description": p["desc"],
         "url": abs_url(p["slug"]), "inLanguage": "ko-KR", "dateModified": UPDATED,
         "about": p["slug"], "publisher": {"@type": "Organization", "name": BRAND, "url": SITE + "/"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]},
    ]
    return json.dumps(data, ensure_ascii=False, indent=1)


def render(p):
    slug = p["slug"]
    crumb = '<a href="/">홈</a><span aria-hidden="true">›</span>'
    if slug != HUB:
        crumb += f'<a href="{url(HUB)}">{e(HUB)}</a><span aria-hidden="true">›</span>'
    crumb += f'<span aria-current="page">{e(slug)}</span>'

    sec_ids = [f"s{i + 1}" for i in range(len(p["sections"]))]
    toc = '<a href="#key">핵심 요약</a>' + "".join(
        f'<a href="#{sid}">{e(h)}</a>' for sid, (h, _) in zip(sec_ids, p["sections"]))
    toc += '<a href="#info">참가 정보</a><a href="#faq">자주 묻는 질문</a><a href="#more">더 많은 안내</a>'

    summary = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in p["summary"])
    sections = "".join(
        f'<section id="{sid}" class="sec"><h2>{e(h)}</h2>{"".join(block(b) for b in blocks)}</section>'
        for sid, (h, blocks) in zip(sec_ids, p["sections"]))
    info = f"<div><dt>다음 일정</dt>{events.next_line(EVENTS)}</div>" + "".join(
        f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in INFO)
    faq = "".join(
        f'<details{" open" if i == 0 else ""}><summary>{e(q)}</summary><p>{e(a)}</p></details>'
        for i, (q, a) in enumerate(p["faq"]))
    city = "논산" if slug.startswith("논산") else "대전"

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p["title"])}</title>
<meta name="description" content="{e(p["desc"])}">
<link rel="canonical" href="{abs_url(slug)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(p["title"])}">
<meta property="og:description" content="{e(p["desc"])}">
<meta property="og:url" content="{abs_url(slug)}">
<meta property="og:image" content="{og_url(slug)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:locale" content="ko_KR">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/bar.css">
<link rel="stylesheet" href="/assets/fx.css">
<script type="application/ld+json">
{schema(p)}
</script>
</head>
<body>
<header class="hd"><div class="wrap hd-in">
<a class="logo" href="/">{LOGO_SVG}<span>러브<em>DM</em></span></a>
<nav aria-label="주요 메뉴"><a href="/#schedule">소개팅 일정</a><a href="{url(HUB)}">대전 소개팅 안내</a><a class="btn" href="/#schedule">참여 신청</a></nav>
</div></header>

<main>
<section class="hero"><div class="wrap">
<nav class="crumb" aria-label="현재 위치">{crumb}</nav>
<p class="pill">{e(p["eyebrow"])}</p>
<h1>{e(p["h1"])}</h1>
<p class="lead">{e(p["lead"])}</p>
<div class="cta"><a class="btn" href="/#schedule">일정 보고 신청하기</a><a class="btn ghost" href="/#process">진행 방식 보기</a></div>
<p class="upd">최종 업데이트 {UPDATED} · 작성 {BRAND}</p>
</div></section>

<nav class="toc" aria-label="이 페이지 목차"><div class="wrap">{toc}</div></nav>

<div class="wrap body">
<section id="key" class="key"><h2>{e(p["slug"])}, 핵심만 먼저</h2><dl>{summary}</dl></section>
{sections}
<section id="info" class="info"><h2>러브DM 참가 정보</h2><dl>{info}</dl>
<p>장소와 입금 계좌는 참가가 확정된 분께만 문자로 안내합니다. 날짜별 신청서는 홈의 일정표에 있습니다.</p>
<a class="btn" href="/#schedule">이번 주 일정 확인하기</a></section>
<section id="faq" class="faq"><h2>{e(p["slug"])} 자주 묻는 질문</h2>{faq}</section>
<section id="more" class="more"><h2>지역·대상·주제별 소개팅 안내</h2>
<h3>지역별</h3><ul class="lks">{link_cards(AREAS, slug)}</ul>
<h3>대상별</h3><ul class="lks">{link_cards(TARGETS, slug)}</ul>
<h3>주제별</h3><ul class="lks">{link_cards(TOPICS, slug)}</ul>
</section>
</div>

<section class="band"><div class="wrap">
<h2>이번 주 토요일, {e(city)}에서 만나요</h2>
<p>신청서 검토 후 확정된 분께만 계좌번호, 장소, 시간을 문자로 개별 안내드립니다. 카카오톡 친구 추가 허용 설정을 꼭 켜 주세요.</p>
<a class="btn light" href="/#schedule">일정 보고 신청하기</a>
</div></section>
</main>

<footer class="ft"><div class="wrap">
<p class="ft-logo">러브<em>DM</em></p>
<p>대전 로테이션 소개팅 · 대전 직장인 소개팅 · 논산 소개팅</p>
<p>상호 [상호명] · 대표 [대표자명] · 사업자등록번호 [000-00-00000]</p>
<p>통신판매업 신고번호 [제0000-대전○○-0000호]</p>
<p>주소 [대전광역시 ○○구 ○○로 00] · 문의 [카카오톡 채널] · [연락처]</p>
</div></footer>
{events.bar(EVENTS, "/#schedule")}
<script src="/assets/live.js" defer></script>
</body>
</html>
"""


def home_links():
    """홈(index.html)의 키워드 안내 칸을 pages.py 목록으로 다시 채운다."""
    def lis(items):
        return "".join(
            f'<li><a class="chip" href="{url(p["slug"])}" style="display: block; padding: 12px 16px; border: 1px solid #F0E6EA; '
            f'border-radius: 12px; text-decoration: none; color: #18141C; font-weight: 500; font-size: 15px">{e(p["slug"])}</a></li>'
            for p in items)
    ul = 'style="margin: 0; padding: 0; list-style: none; display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px"'
    h3 = 'style="margin: 28px 0 12px; font-size: 17px; color: #4A4250"'
    start, end = "<!-- 키워드 안내 시작 -->", "<!-- 키워드 안내 끝 -->"
    block = "\n".join([
        start,
        '<section id="guide" style="background: #FFFFFF; border-top: 1px solid #F0E6EA">',
        '<div style="max-width: 1200px; margin: 0 auto; padding: 72px 24px">',
        '<p class="eb" style="margin: 0 0 8px; color: #C81E5B; font-weight: 700; font-size: 15px">대전 소개팅 안내</p>',
        '<h2 style="margin: 0; font-size: clamp(26px, 3.4vw, 36px); font-weight: 900; letter-spacing: -0.8px">지역·대상·주제별로 더 알아보기</h2>',
        f'<h3 {h3}>지역별</h3>',
        f'<ul {ul}>{lis(AREAS)}</ul>',
        f'<h3 {h3}>대상별</h3>',
        f'<ul {ul}>{lis(TARGETS)}</ul>',
        f'<h3 {h3}>주제별</h3>',
        f'<ul {ul}>{lis(TOPICS)}</ul>',
        '</div>',
        '</section>',
        end,
    ])
    path = os.path.join(ROOT, "index.html")
    s = open(path, encoding="utf-8").read()
    a, b = s.index(start), s.index(end) + len(end)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(s[:a] + block + s[b:])


def fill(name, content):
    """index.html의 <!-- name 시작 --> ~ <!-- name 끝 --> 사이를 바꾼다."""
    start, end = f"<!-- {name} 시작 -->", f"<!-- {name} 끝 -->"
    path = os.path.join(ROOT, "index.html")
    s = open(path, encoding="utf-8").read()
    a, b = s.index(start) + len(start), s.index(end)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(s[:a] + "\n" + content + "\n" + s[b:])


def home_blocks():
    """홈의 일정 관련 칸과 공유 이미지를 schedule.py 기준으로 다시 채운다."""
    fill("행사 데이터", events.event_schema(EVENTS, SITE, og_url("home")))
    fill("다음 소개팅", events.home_next(EVENTS))
    fill("일정 카드", events.home_cards(EVENTS))
    fill("신청 버튼", events.home_apply(EVENTS))
    fill("하단 바", events.bar(EVENTS, "#schedule"))
    path = os.path.join(ROOT, "index.html")
    s = open(path, encoding="utf-8").read()
    old = '<meta property="og:image" content="https://love-dm.netlify.app/hero.jpg">'
    if old in s:
        s = s.replace(old, f'<meta property="og:image" content="{og_url("home")}">\n<meta property="og:image:width" content="1200">\n'
                      '<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">')
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(s)


def main():
    for p in PAGES:
        d = os.path.join(ROOT, p["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(render(p))

    urls = [(SITE + "/", "1.0")] + [(abs_url(p["slug"]), "0.9" if p["slug"] == HUB else "0.8") for p in PAGES]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, pr in urls:
        sm.append(f"  <url><loc>{u}</loc><lastmod>{UPDATED}</lastmod><priority>{pr}</priority></url>")
    sm.append("</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(sm))
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"User-agent: *\nAllow: /\nDisallow: /tools/\n\nSitemap: {SITE}/sitemap.xml\n")
    home_links()
    home_blocks()
    make_og(ROOT, PAGES)
    print(f"{len(PAGES)} pages, sitemap {len(urls)} urls")


if __name__ == "__main__":
    main()
