import os
import requests
from datetime import datetime, timezone, timedelta
import random

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

categories = [
    """یک متن کوتاه فارسی خالص (۱ تا ۳ خط) درباره دلتنگی یا آدمایی که رفتن.
مثل یه خاطره‌ی شخصی حس بده. کلمات ساده و صمیمی.
مهم: هیچ کلمه‌ای غیرفارسی داخل متن فارسی نذار. تمام کلمات باید فارسی باشن.
مثال: 'گاهی وسط روز یهو دلم می‌گیره، نه برای یه چیز خاص، فقط دلم می‌گیره'""",

    """یک نقل‌قول واقعی از یک نویسنده یا فیلسوف معروف به فارسی خالص.
فرمت دقیق:
سطر اول: نقل‌قول به زبان اصلی (مثلاً اگر انگلیسیه، انگلیسی بنویس)
سطر دوم: ترجمه‌ی فارسی محاوره‌ای خالص (هیچ کلمه‌ی غیرفارسی داخل ترجمه نباشد)
𓄳 نام نویسنده
☆ Hoshi Studio
مثال:
The cradle rocks above an abyss
گهواره بالای یک بی‌نهایت تاب می‌خورد
𓄳 نابوکوف
☆ Hoshi Studio""",

    """یک جمله یا ضرب‌المثل ژاپنی واقعی درباره زندگی، زمان یا احساس.
فرمت دقیق:
سطر اول: متن ژاپنی خالص
سطر دوم: ترجمه‌ی فارسی محاوره‌ای خالص (هیچ کلمه‌ی غیرفارسی داخل ترجمه نباشد)
☆ Hoshi Studio
مثال:
七転び八起き
هفت بار بیفتی، هشت بار پا می‌شی
☆ Hoshi Studio""",

    """یک اعتراف صادقانه به فارسی محاوره‌ای خالص (۲ تا ۴ خط) از زبان اول شخص.
درباره یکی از اینها: تنهایی، گذر زمان، آدمایی که رفتن، لحظهایی که دیگه برنمی‌گردن، عشقی که تموم شد.
مهم: تمام کلمات فارسی باشن. هیچ کلمه‌ای غیرفارسی داخل متن نذار.
مثال: 'بعضی آدما رو نمی‌شه فراموش کرد، فقط یاد می‌گیری باهاشون توی ذهنت زندگی کنی'""",

    """یک متن کوتاه انگلیسی خالص (۱ تا ۲ خط) درباره گذر زمان، از دست دادن، یا چیزی که دیگه مثل قبل نیست.
عمیق و شاعرانه، هیچ کلمه‌ای غیرانگلیسی داخل متن نذار.
مثال: 'you don’t move on. you just slowly learn to carry it differently.'""",

    """یک لحظه‌ی کوچیک به فارسی محاوره‌ای خالص (۱ تا ۳ خط) — یک حس عمیق بیدار می‌شه از یک جزئیات چیزی.
مثل صدای بارون، نور آخر روز، بوی یه چیز قدیمی.
تمام کلمات فارسی خالص باشن. هیچ کلمه‌ای غیرفارسی نذار.
مثال: 'ساعت ۴ صبحه و بارون میاد. نمی‌دونم چرا ولی دلم می‌خواد گریه کنم'""",

    """یک جمله‌ی زیبا و عمیق به انگلیسی خالص (۱ تا ۲ خط) درباره عشق، از دست دادن، یا بودن.
شاعرانه، مینیمال، هیچ کلمه‌ای غیرانگلیسی داخل متن نذار.
مثال: 'she kept asking if the phone was charged. that was the last time we spoke.'"""
]

system_prompt = """تو نویسنده‌ی کانال تلگرام 'Hoshi Studio' هستی. مخاطب: دخترهای فارسی‌زبان با احساس عمیق.

قوانین زبانی بسیار مهم:

۱. متن فارسی → تمام کلمات باید فارسی خالص باشن. هیچ کلمه‌ای انگلیسی، ژاپنی، فرانسوی یا هر زبان دیگری داخل متن فارسی نذار. ادات فارسی محاوره‌ای: می‌تونم، می‌خوام، یه، فنجون، دلم می‌گیره

۲. متن انگلیسی → تمام کلمات باید انگلیسی خالص باشن. هیچ کلمه‌ای فارسی مخلوط نشود

۳. متن ژاپنی / فرانسوی / غیره → اول متن به زبان اصلی، سپس ترجمه‌ی فارسی محاوره‌ای خالص زیرش

هیچ‌وقت زبان‌ها رو باهم قاطی نکن. هیچ هشتگی. کلیشه‌ای ننویس. فقط متن پست."""

category_prompt = random.choice(categories)

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
    "temperature": 1.0
}

response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
result = response.json()

if "choices" not in result:
    print(f"Groq error: {result}")
    exit(1)

post_text = result["choices"][0]["message"]["content"].strip()
print(f"Generated:\n{post_text}")

tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
tg_response = requests.post(tg_url, json={"chat_id": CHAT_ID, "text": post_text})
tg_result = tg_response.json()

if tg_result.get("ok"):
    print("✅ Posted!")
else:
    print(f"❌ Telegram error: {tg_result}")
    exit(1)
