import os
import json
import requests
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

# Figure out which content category to post based on time slot
tehran_tz = timezone(timedelta(hours=3, minutes=30))
now = datetime.now(tehran_tz)
hour_slots = [6, 9, 12, 15, 18, 21, 0]
best_slot = min(range(7), key=lambda i: abs(now.hour - hour_slots[i]))

categories = [
    "یک تاییدیه انگیزشی فارسی محاوره‌ای برای یک دختر جاه‌طلب که رویاهای بزرگ داره. کوتاه، از دل، با ایموجی.",
    "یک نقل‌قول ادبی یا فلسفی از یک نویسنده یا فیلسوف مشهور، با ترجمه فارسی محاوره‌ای. فرمت: نقل‌قول → خط جدید → نسخه فارسی → 'نویسنده 𓄳' → '☆ Hoshi Studio'",
    "یک ضرب‌المثل یا جمله ژاپنی زیبا با ترجمه فارسی محاوره‌ای زیرش. از کانجی واقعی استفاده کن.",
    "یک اعتراف صادقانه و احساسی به فارسی محاوره‌ای از زبان یک دختر که خسته‌ست ولی تسلیم نمی‌شه. کوتاه و از دل.",
    "یک جمله کوتاه و پانچ به انگلیسی یا فارسی محاوره‌ای درباره تلاش، رویا و موفقیت. پر از انرژی.",
    "یک لحظه دنج و آروم — چای، کتاب، باران، شمع — به فارسی محاوره‌ای یا انگلیسی. حس cozy بده.",
    "یک جمله زیبا و شاعرانه به انگلیسی درباره شب، ستاره، ماه یا رویا. کوتاه و aesthetic."
]

category_prompt = categories[best_slot]

system_prompt = """تو محتوا‌ساز کانال تلگرام 'Hoshi Studio' هستی — یک کانال برای دخترهای جاه‌طلب و رویاپرداز فارسی‌زبان.
سبک: کوتاه (۱-۴ خط)، بیتر‌سوئیت، احساسی ولی قوی، مثل یه دوست صمیمی که دلسوزته.
قوانین:
- فارسی همیشه محاوره‌ای باشه (می‌تونم نه می‌توانم، می‌خوام نه می‌خواهم، یه نه یک)
- از ایموجی‌های این‌ها استفاده کن: ✨🌙🎀🌸⭐🔮🪐🤍🔥💫🫧
- بدون هشتگ
- هر بار خلاق و متفاوت باش — تکراری نباش
- فقط متن پست رو بنویس، هیچ توضیحی نده"""

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": category_prompt}
    ],
    "max_tokens": 300,
    "temperature": 0.9
}

response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
result = response.json()

if "choices" not in result:
    print(f"Groq error: {result}")
    exit(1)

post_text = result["choices"][0]["message"]["content"].strip()
print(f"Generated post:\n{post_text}")

# Send to Telegram
tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
tg_response = requests.post(tg_url, json={"chat_id": CHAT_ID, "text": post_text})
tg_result = tg_response.json()

if tg_result.get("ok"):
    print(f"✅ Posted successfully!")
else:
    print(f"❌ Telegram error: {tg_result}")
    exit(1)
