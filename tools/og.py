# -*- coding: utf-8 -*-
"""페이지마다 카카오톡·SNS 공유 미리보기 이미지(1200×630)를 만든다. og/<slug>.jpg

글꼴은 Noto Sans KR(가변)을 쓴다. 이 PC에 없으면 이미지를 새로 만들지 않고 기존 파일을 둔다.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
PINK, INK, SUB, BG = (200, 30, 91), (24, 20, 28), (74, 66, 80), (255, 241, 245)
FONTS = [
    os.path.join(os.path.dirname(__file__), "fonts", "NotoSansKR-VF.ttf"),
    "C:/Windows/Fonts/NotoSansKR-VF.ttf",
    "/Library/Fonts/NotoSansKR-VF.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansKR-VF.ttf",
]
PHOTO_X = 760  # 오른쪽 사진이 시작하는 x


def font_path():
    for f in FONTS:
        if os.path.exists(f):
            return f
    return None


def font(path, size, weight):
    ft = ImageFont.truetype(path, size)
    try:
        ft.set_variation_by_axes([weight])
    except Exception:
        pass
    return ft


def wrap(draw, text, ft, width):
    """띄어쓰기 기준으로 줄을 나눈다."""
    lines, cur = [], ""
    for word in text.split(" "):
        test = (cur + " " + word).strip()
        if draw.textlength(test, font=ft) <= width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def card(path, photo, title, sub, foot):
    img = Image.new("RGB", (W, H), BG)
    # 오른쪽 사진
    ph = Image.open(photo).convert("RGB")
    pw = W - PHOTO_X
    scale = max(pw / ph.width, H / ph.height)
    ph = ph.resize((round(ph.width * scale), round(ph.height * scale)), Image.LANCZOS)
    left = (ph.width - pw) // 2
    ph = ph.crop((left, 0, left + pw, H))
    img.paste(ph, (PHOTO_X, 0))
    d = ImageDraw.Draw(img)
    fp = font_path()

    # 로고
    logo = font(fp, 40, 900)
    d.text((72, 64), "러브", font=logo, fill=INK)
    d.text((72 + d.textlength("러브", font=logo), 64), "DM", font=logo, fill=PINK)

    # 제목: 길이에 맞춰 크기를 줄인다
    for size in (84, 76, 68, 60):
        tf = font(fp, size, 900)
        lines = wrap(d, title, tf, PHOTO_X - 72 - 48)
        if len(lines) <= 2:
            break
    y = 190 if len(lines) == 2 else 230
    for ln in lines:
        d.text((72, y), ln, font=tf, fill=INK)
        y += round(size * 1.25)

    sf = font(fp, 30, 500)
    d.text((72, y + 18), sub, font=sf, fill=SUB)

    # 아래 알약
    ff = font(fp, 26, 700)
    tw = d.textlength(foot, font=ff)
    d.rounded_rectangle((72, H - 72 - 60, 72 + tw + 56, H - 72), radius=30, fill=PINK)
    d.text((72 + 28, H - 72 - 60 + 13), foot, font=ff, fill=(255, 255, 255))

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "JPEG", quality=86, optimize=True, progressive=True)


def make_og(root, pages):
    if not font_path():
        print("og: Noto Sans KR 글꼴이 없어 공유 이미지를 건너뜁니다.")
        return
    photo = os.path.join(root, "hero.jpg")
    out = os.path.join(root, "og")
    foot = "매주 토요일 오후 8시 · 대전·논산"
    card(os.path.join(out, "home.jpg"), photo, "대전 로테이션 소개팅", "미혼 직장인 1:1 로테이션 소개팅", foot)
    for p in pages:
        sub = "논산 미혼 직장인 로테이션 소개팅" if p["slug"].startswith("논산") else "대전 미혼 직장인 로테이션 소개팅"
        card(os.path.join(out, p["slug"] + ".jpg"), photo, p["eyebrow"], sub, foot)
    print(f"og: {len(pages) + 1} images")
