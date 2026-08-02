import os
import requests
import random
import re

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

# Persian unicode range + allowed chars (emojis, punctuation, newlines, ☆, 𓄳)
PERSIAN_CHARS = re.compile(r'[\u0600-\u06FF\u200c\u200d\s\n\r…،؛؟«»‘’“”!?.,;:\-\u2014\u2013()\[\]\*\/\\0-9۰-۹]')

def is_persian_clean(text):
    """Check if text is clean Persian - no Latin or other foreign chars except emojis and special symbols"""
    # Remove emojis and special symbols like ☆, 𓄳, Hoshi Studio signature
    cleaned = re.sub(r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF\u2B50\u2B55\u231A-\u231B\u23E9-\u23F3\u25AA-\u25FE\u2614-\u2615\u2648-\u2653\u267F\u2693\u26A1\u26AA-\u26AB\u26BD-\u26BE\u26C4-\u26C5\u26CE\u26D4\u26EA\u26F2-\u26F3\u26F5\u26FA\u26FD\u2702\u2705\u2708-\u270D\u270F\u2712\u2714\u2716\u271D\u2721\u2728\u2733-\u2734\u2744\u2747\u274C\u274E\u2753-\u2755\u2757\u2763-\u2764\u2795-\u2797\u27A1\u27B0\u27BF\u2934-\u2935\u2B05-\u2B07\u2B1B-\u2B1C\u2B50\u2B55\u3030\u303D\u3297\u3299\U0001F004\U0001F0CF\U0001F170-\U0001F171\U0001F17E-\U0001F17F\U0001F18E\U0001F191-\U0001F19A]', '', text)
    # Remove the Hoshi Studio signature lines
    cleaned = re.sub(r'☆ Hoshi Studio', '', cleaned)
    cleaned = re.sub(r'𓄳[^\n]*', '', cleaned)
    # Remove pure numbers and punctuation lines
    cleaned = cleaned.strip()
    # Check for Latin characters (a-z, A-Z) - these indicate foreign words
    latin = re.search(r'[a-zA-Z]', cleaned)
    return latin is None

def call_groq(system_prompt, user_prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 300,
        "temperature": 1.0
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    result = response.json()
    if "choices" not in result:
        raise Exception(f"Groq error: {result}")
    return result["choices"][0]["message"]["content"].strip()

# Content categories
persian_categories = [
    """یک متن کوتاه فارسی خالص (۱ تا ۳ خط) درباره دلتنگی یا آدمایی که رفتن.
مثل یه خاطره‌ی شخصی حس بده. کلمات ساده و صمیمی.محاوره‌ای: می‌تونم، می‌خوام، یه، دلم می‌گیره، آدما""",
    """یک اعتراف صادقانه به فارسی محاوره‌ای خالص (۲ تا ۴ خط) از زبان اول شخص.
درباره: تنهایی، گذر زمان، آدمایی که رفتن، لحظاتی که دیگه برنمی‌گردن، عشقی که تموم شد.محاوره‌ای: می‌تونم، می‌خوام، یه، دلم می‌گیره، آدما""",
    """یک لحظه‌ی کوچیک به فارسی محاوره‌ای خالص (۱ تا ۳ خط) — یک حس عمیق بیدار می‌شه از یک جزئیات.
مثل صدای بارون، نور آخر روز، بوی یه چیز قدیمی. تمام کلمات فارسی خالص باشن.محاوره‌ای: می‌تونم، می‌خوام، یه، دلم می‌گیره، آدما"""
]

english_categories = [
    """Write a short, deep English post (1-2 lines) about love, loss, or time passing.
Poetic, minimal. Only English words. No Persian.
Example: 'you don’t move on. you just slowly learn to carry it differently.'""",
    """Write a short, deep English post (1-2 lines) about being human, existence, or longing.
Poetic, minimal. Only English words. No Persian.
Example: 'she kept asking if the phone was charged. that was the last time we spoke.'"""
]

quote_categories = [
    """یک نقل‌قول واقعی از یک نویسنده معروف (داستایوفسکی، کافکا، مارکز، چخوف، نابوکوف، حافظ، رومی) به زبان اصلی.
فرمت دقیق:
[ORIGINAL QUOTE IN ORIGINAL LANGUAGE]
[PERSIAN TRANSLATION - فارسی محاوره‌ای خالص]
𓄳 [AUTHOR NAME]
☆ Hoshi Studio""",
    """یک جمله یا ضرب‌المثل ژاپنی واقعی درباره زندگی، زمان یا احساس.
فرمت دقیق:
[متن ژاپنی خالص]
[ترجمه‌ی فارسی محاوره‌ای خالص]
☆ Hoshi Studio"""
]

# Pick category type
roll = random.random()
if roll < 0.45:
    category = random.choice(persian_categories)
    post_type = "persian"
elif roll < 0.70:
    category = random.choice(english_categories)
    post_type = "english"
else:
    category = random.choice(quote_categories)
    post_type = "quote"

system_map = {
    "persian": """تو نویسنده‌ی کانال تلگرام 'Hoshi Studio' هستی.
قانون طلایی: متن فارسی یعنی فقط و فقط فارسی. هیچ کلمه‌ای لاتین، فرانسوی، ژاپنی، ویتنامی، یا هر زبان دیگری داخل متن فارسی نذار.
فارسی محاوره‌ای: می‌تونم، می‌خوام، یه، فنجون، دلم می‌گیره، آدما، اینجوری، براشون
هیچ هشتگی. دیپ، احساسی، واقعی. فقط متن پست.""",
    "english": """You are the writer of Telegram channel 'Hoshi Studio'.
Golden rule: English posts must be 100% English. No Persian, no other languages mixed in.
Deep, poetic, minimal. No hashtags. Just the post text.""",
    "quote": """تو نویسنده‌ی کانال تلگرام 'Hoshi Studio' هستی.
برای نقل‌قولها: سطر اول متن اصلی به زبان خودش. سطر دوم ترجمه‌ی فارسی محاوره‌ای خالص (هیچ کلمه‌ای غیرفارسی داخل ترجمه نباشد).
هیچ هشتگی. فقط متن پست."""
}

system_prompt = system_map[post_type]

# Generate with retry if Persian post contains Latin chars
max_retries = 3
post_text = None

for attempt in range(max_retries):
    text = call_groq(system_prompt, category)
    if post_type == "persian" and not is_persian_clean(text):
        print(f"Attempt {attempt+1}: Found foreign chars in Persian post, retrying...")
        print(f"Rejected: {text[:100]}")
        continue
    post_text = text
    break

if not post_text:
    print("All retries failed, using last generated text anyway")
    post_text = text

print(f"Final post:\n{post_text}")

tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
tg_response = requests.post(tg_url, json={"chat_id": CHAT_ID, "text": post_text})
tg_result = tg_response.json()

if tg_result.get("ok"):
    print("✅ Posted!")
else:
    print(f"❌ Telegram error: {tg_result}")
    exit(1)
