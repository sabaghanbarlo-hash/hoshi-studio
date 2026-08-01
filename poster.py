import os
import requests
from datetime import datetime, timezone, timedelta
import random

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

tehran_tz = timezone(timedelta(hours=3, minutes=30))
now = datetime.now(tehran_tz)

categories = [
    """یک متن کوتاه فارسی محاوره‌ای (۱ تا ۳ خط) درباره دلتنگی یا از دست دادن کسی. 
باید مثل یک خاطره‌ی شخصی حس بده، نه شعار. از کلمات ساده و صمیمی استفاده کن.
مثال سبک: 'گاهی وسط روز یهو دلم می‌گیره، نه برای یه چیز خاص، فقط دلم می‌گیره'""",

    """یک نقل‌قول واقعی از یک نویسنده یا فیلسوف معروف (داستایوفسکی، کافکا، مارکز، چخوف، رومی، حافظ، سهراب سپهری یا مشابه) 
که عمیق و احساسی باشه. فرمت دقیق:
متن نقل‌قول به زبان اصلی
ترجمه فارسی محاوره‌ای
𓄳 نام نویسنده
☆ Hoshi Studio""",

    """یک جمله یا ضرب‌المثل ژاپنی واقعی و زیبا درباره زندگی، زمان، یا احساس.
فرمت:
متن ژاپنی
ترجمه فارسی محاوره‌ای (ساده و صمیمی)
☆ Hoshi Studio""",

    """یک اعتراف صادقانه به فارسی محاوره‌ای (۲ تا ۴ خط) از زبان اول شخص.
درباره یکی از این موضوعات: تنهایی، گذر زمان، آدم‌هایی که رفتن، لحظه‌هایی که دیگه برنمی‌گردن.
باید خیلی واقعی و بی‌فیلتر باشه، نه کلیشه‌ای.
مثال سبک: 'بعضی آدما رو نمی‌شه فراموش کرد، فقط یاد می‌گیری باهاشون توی ذهنت زندگی کنی'""",

    """یک متن کوتاه انگلیسی یا فارسی محاوره‌ای (۱ تا ۲ خط) درباره گذر زمان، بزرگ شدن، یا چیزی که دیگه مثل قبل نیست.
عمیق و شاعرانه ولی ساده. نه انگیزشی.
مثال: 'you don't move on. you just slowly learn to carry it differently'""",

    """یک لحظه‌ی کوچیک و احساسی به فارسی محاوره‌ای (۱ تا ۳ خط) — 
مثل صبح زود، صدای بارون، نور آخر روز، یه آهنگ قدیمی — که یه حس عمیق رو بیدار می‌کنه.
نباید مستقیم بگه 'این احساس خوبیه'، باید حس رو نشون بده.
مثال: 'ساعت ۴ صبحه و بارون میاد. نمی‌دونم چرا ولی دلم می‌خواد گریه کنم'""",

    """یک جمله‌ی زیبا و عمیق به انگلیسی (۱ تا ۲ خط) درباره عشق، از دست دادن، یا بودن.
سبک: شاعرانه، مینیمال، مثل یه سطر از یه رمان خوب.
مثال: 'she kept asking if the phone was charged, and i kept saying yes, and that was the last time we spoke'"""
]

slot_index = random.randint(0, 6)
category_prompt = categories[slot_index]

system_prompt = """تو نویسنده‌ی کانال تلگرام 'Hoshi Studio' هستی.
مخاطب: دخترهای ۱۸ تا ۲۸ ساله فارسی‌زبان که اهل کتاب، موسیقی و احساس عمیق هستن.

قوانین مهم:
- فارسی همیشه محاوره‌ای باشه: می‌تونم، می‌خوام، یه، فنجون، دلم می‌گیره، آدما
- هیچ‌وقت فارسی رسمی ننویس: نه می‌توانم، نه می‌خواهم، نه یک
- هیچ هشتگی نذار
- هیچ توضیحی ندی، فقط متن پست رو بنویس
- کلیشه‌ای ننویس — هر پست باید یه حس تازه داشته باشه
- پست‌های انگیزشی و مثبت‌اندیش ننویس
- عمق مهمه، نه طول متن"""

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
