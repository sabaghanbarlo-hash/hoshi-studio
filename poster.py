import json
import os
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
POST_INDEX = int(os.environ.get("POST_INDEX", "0"))

with open("posts.json", "r", encoding="utf-8") as f:
    all_posts = json.load(f)

total = len(all_posts)
if POST_INDEX >= total:
    print(f"All {total} posts sent!")
    exit(0)

post_text = all_posts[POST_INDEX]
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
response = requests.post(url, json={"chat_id": CHAT_ID, "text": post_text})
result = response.json()
if result.get("ok"):
    print(f"Posted [{POST_INDEX}/{total}]: {post_text[:60]}...")
else:
    print(f"Failed: {result}")
    exit(1)
