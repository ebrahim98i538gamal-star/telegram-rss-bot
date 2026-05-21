import feedparser
import schedule
import time
import json
import os
from bs4 import BeautifulSoup
import requests

# =====================
# بيانات البوت
# =====================

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("Missing environment variables!")
    exit()
# =====================
# RSS Feeds
# =====================

RSS_FEEDS = [
    "https://rss.app/feeds/EkahERRyfQuAH3VJ.xml",
    "https://rss.app/feeds/jM74zFo9UOx4KF9V.xml",
    "https://rss.app/feeds/pZoPl5yoEMdxVfpH.xml",
    "https://rss.app/feeds/t1D7UoY7b9cB71IS.xml",
    "https://rss.app/feeds/s64yK0e9UvAjeDw8.xml",
    "https://rss.app/feeds/pB613yPT21TZjjJT.xml",
    "https://rss.app/feeds/ETNhunGOEU93mgW0.xml",
    "https://rss.app/feeds/lzny2bG4KINXM6yC.xml",
    "https://rss.app/feeds/DwdZAfJ3gIBCts25.xml",
    "https://rss.app/feeds/O9haauV61F6YRrsc.xml",
    "https://rss.app/feeds/o794MXJ4AJZ03sKa.xml",
    "https://rss.app/feeds/Vgec8u3TSWEZiG0e.xml",
    "https://rss.app/feeds/DK7QOlxoMaehb6Y4.xml",
    "https://rss.app/feeds/Ox1BZ03WE3HR15nH.xml",
    "https://rss.app/feeds/8IVfu3R41qWT7J3g.xml",
    "https://rss.app/feeds/IivpDoYCLS5JWlrw.xml",
    "https://rss.app/feeds/1nmwND1Z25987D1i.xml",
    "https://rss.app/feeds/l9Mkxrfv3RduamGR.xml",
    "https://rss.app/feeds/x8D6Dfgpm63LNrxn.xml",
    "https://rss.app/feeds/jBTtM0v1mJzcS50d.xml",
    "https://rss.app/feeds/hQ16E3lDhTw966g7.xml",
    "https://rss.app/feeds/lPBG1NitHubRSERb.xml",
    "https://rss.app/feeds/S6bl2Z6Cf9AYhbg7.xml",
    "https://rss.app/feeds/WoUEd2CmQd64xYNf.xml",
    "https://rss.app/feeds/m6rxj42pSmqB2NvV.xml",
    "https://rss.app/feeds/lnlTQ3cZZnsHpPp6.xml",
    "https://rss.app/feeds/kacyiDz3un7Lxmv3.xml",
    "https://rss.app/feeds/d6RxSXgPGQ0KwbLn.xml",
    "https://rss.app/feeds/w2du9adtasK7I0K1.xml",
    "https://rss.app/feeds/zUncwSYcYzh9NgMY.xml",
    "https://rss.app/feeds/rJwpiiIQ6H4PWbTL.xml",
    "https://rss.app/feeds/FgX5MTZZ0leJidjA.xml",
    "https://rss.app/feeds/ILcCntuO62NTFoLK.xml",
    "https://rss.app/feeds/rL2bMju2kQML4HHi.xml",
    "https://rss.app/feeds/Mua9JKUaSHzCt4LB.xml",
    "https://rss.app/feeds/z2iyLXGoe3lZjhxM.xml",
    "https://rss.app/feeds/4Dqd5z8ZELwRXJs6.xml",
    "https://rss.app/feeds/weY7AEkoZoahDH8V.xml",
    "https://rss.app/feeds/VJaQ7W25JZlpIpC1.xml",
    "https://rss.app/feeds/r2T0Du03Gb8aa0lP.xml",
    "https://rss.app/feeds/ptdtgKtW5ONBS4pL.xml",
    "https://rss.app/feeds/rbGSwmtE0kEe2wq0.xml",
    "https://rss.app/feeds/HTX1NqxVeZA46b5m.xml",
    "https://rss.app/feeds/b9HI8uNFfiZCWPNO.xml",
    "https://rss.app/feeds/8HSyGXMm4Meds6qK.xml",
    "https://rss.app/feeds/pwuKxMr7EJTNOx5v.xml",
    "https://rss.app/feeds/Uityfst6K4avAinh.xml",
    "https://rss.app/feeds/juj8I33CzdhNZQ3a.xml",
    "https://rss.app/feeds/BABPJPKBKGjH6Wc3.xml",
]

def split_text(text, limit=4000):
    parts = []
    while len(text) > limit:
        cut = text.rfind(" ", 0, limit)
        if cut == -1:
            cut = limit
        parts.append(text[:cut])
        text = text[cut:].strip()
    parts.append(text)
    return parts

# =====================
# حفظ المنشورات المرسلة
# =====================

POSTS_FILE = "sent_posts.json"

if os.path.exists(POSTS_FILE):
    with open(POSTS_FILE, "r", encoding="utf-8") as file:
        sent_posts = set(json.load(file))
else:
    sent_posts = set()

def save_posts():
    with open(POSTS_FILE, "w", encoding="utf-8") as file:
        json.dump(list(sent_posts), file)

# =====================
# إرسال تيليجرام (محسن)
# =====================

def send_post(page_name, text, link, image_url=None):

    try:

        # المنشور الكامل
        full_message = f"""📰 {page_name}

📝 {text}

🔗 {link}
"""

        # =========================
        # لو توجد صورة
        # =========================

        if image_url:

            # أول جزء للكابشن (1024)
            first_parts = split_text(full_message, 1024)

            first_caption = first_parts[0]

            # إرسال الصورة مع أول جزء
            response = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={
                    "chat_id": CHAT_ID,
                    "photo": image_url,
                    "caption": first_caption
                },
                timeout=30
            )

            print(response.text)

            # باقي النص
            remaining = full_message[len(first_caption):].strip()

            if remaining:

                parts = split_text(remaining, 4000)

                for part in parts:

                    response = requests.post(
                        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                        data={
                            "chat_id": CHAT_ID,
                            "text": part
                        },
                        timeout=30
                    )

                    print(response.text)

                    time.sleep(1)

        # =========================
        # بدون صورة
        # =========================

        else:

            parts = split_text(full_message, 4000)

            for part in parts:

                response = requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    data={
                        "chat_id": CHAT_ID,
                        "text": part
                    },
                    timeout=30
                )

                print(response.text)

                time.sleep(1)

        return True

    except Exception as e:

        print("Telegram Error:", e)

        return False
# =====================
# معالجة RSS
# =====================

def check_feeds():

    print("Checking feeds...")

    for rss_url in RSS_FEEDS:

        try:

            feed = feedparser.parse(rss_url)

            if not feed.entries:
                continue

            # 🔥 مهم: نأخذ أكثر من منشور
            for entry in feed.entries[:5]:

                post_id = entry.get("id", entry.link)

                if post_id in sent_posts:
                    continue
                
                # =====================
                # اسم الصفحة (محسن)
                # =====================

                page_name = (
                   entry.get("author")
                   or entry.get("dc_creator")
                   or entry.get("source")
                   or "Unknown Page")
                
                # =====================
                # النص
                # =====================

                summary = entry.get("summary") or entry.get("description") or ""
                soup = BeautifulSoup(summary, "html.parser")
                clean_text = soup.get_text(separator="\n").strip()

                # منع التكرار أو النص الفاضي
                if not clean_text:
                  clean_text = "No content"
                
                # =====================
                # استخراج صورة
                # =====================

                image_url = None                
                if hasattr(entry, "media_content"):
                    media = entry.media_content
                    if media:
                        image_url = media[0].get("url")

                elif hasattr(entry, "links"):
                    for item in entry.links:
                        if item.get("type", "").startswith("image"):
                            image_url = item.get("href")
                            break                

                message = f"""📰 {page_name}

📝 {clean_text}

🔗 {entry.get('link')}
"""

                # =====================
                # الإرسال
                # =====================
                        
                try:

                  success = send_post(page_name, clean_text, entry.get("link"), image_url)

                  if success:

                    print("Sent:", page_name)

                    sent_posts.add(post_id)

                    save_posts()

                  time.sleep(2)

                except Exception as send_error:
                   print("Send Error:", send_error)
                    
        except Exception as e:
            import traceback
            traceback.print_exc()

# =====================
# تشغيل دوري
# =====================

import threading

def run_bot():
    while True:
        check_feeds()
        time.sleep(600)  # 10 دقائق

threading.Thread(target=run_bot).start()

while True:
    time.sleep(1000)
