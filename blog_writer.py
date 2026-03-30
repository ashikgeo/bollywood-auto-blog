import requests
import os
import random
import json
from datetime import datetime

# ============================================================
# APNI SETTINGS YAHAN CHANGE KARO
# ============================================================

BLOG_TOPICS = [
    "Dhurandhar movie Ranbir Kapoor",
    "Bollywood box office collection this week",
    "Latest Bollywood celebrity news",
    "Upcoming Bollywood movies 2026",
    "Bollywood celebrity relationships gossip",
    "Best Bollywood songs trending YouTube",
    "Bollywood movie reviews ratings",
    "OTT releases this week Bollywood",
    "Bollywood award shows red carpet",
    "Bollywood controversies viral moments",
]

# ============================================================

def get_topic():
    return random.choice(BLOG_TOPICS)

def get_image_url(topic):
    try:
        api_key = os.environ["GOOGLE_API_KEY"]
        cx = os.environ["GOOGLE_CX"]
        params = {
            "key": api_key,
            "cx": cx,
            "q": f"{topic} bollywood",
            "searchType": "image",
            "num": 3,
            "imgType": "photo",
            "safe": "active"
        }
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            image_url = data["items"][0]["link"]
            print(f"🖼️ Image mili: {image_url}")
            return image_url
        else:
            print("⚠️ Image nahi mili")
            return None
    except Exception as e:
        print(f"⚠️ Image error: {e}")
        return None

def write_blog_post(topic):
    gemini_key = os.environ["GEMINI_API_KEY"]
    
    prompt = f"""You are an expert Bollywood blogger. Write a detailed, SEO-optimized blog post about:

Topic: {topic}
Date: {datetime.now().strftime('%B %Y')}

Requirements:
- Length: 1200-1500 words
- Start with a catchy title on the FIRST line (no # symbol, just plain title text)
- Write in an engaging, conversational Hindi-English (Hinglish) style that Indian readers love
- Include: introduction, 4-5 detailed sections with subheadings, conclusion
- Add SEO-friendly keywords naturally
- Make it feel like a real entertainment blog, not AI-generated
- Use HTML formatting: <h2> for subheadings, <p> for paragraphs, <b> for emphasis
- Do NOT include the main title in HTML, only the body content

Return format:
Line 1: Blog post title (plain text)
Line 2: Empty line
Line 3 onwards: Full HTML blog content"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 2048
        }
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    if response.status_code != 200:
        raise Exception(f"Gemini error: {data}")
    
    response_text = data["candidates"][0]["content"]["parts"][0]["text"]
    lines = response_text.split('\n')
    title = lines[0].strip()
    content = '\n'.join(lines[2:]).strip()
    
    return title, content

def add_image_to_content(content, image_url, topic):
    if not image_url:
        return content
    image_html = f"""
<div style="text-align:center; margin: 20px 0;">
  <img src="{image_url}" alt="{topic}" style="max-width:100%; height:auto; border-radius:8px;">
  <p style="font-size:12px; color:gray;">Image: {topic}</p>
</div>"""
    if "</p>" in content:
        first_p_end = content.index("</p>") + 4
        content = content[:first_p_end] + image_html + content[first_p_end:]
    else:
        content = image_html + content
    return content

def get_access_token():
    data = {
        "client_id": os.environ["BLOGGER_CLIENT_ID"],
        "client_secret": os.environ["BLOGGER_CLIENT_SECRET"],
        "refresh_token": os.environ["BLOGGER_REFRESH_TOKEN"],
        "grant_type": "refresh_token"
    }
    response = requests.post("https://oauth2.googleapis.com/token", data=data)
    return response.json()["access_token"]

def publish_to_blogger(title, content):
    access_token = get_access_token()
    blog_id = os.environ["BLOGGER_BLOG_ID"]
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    post_data = {
        "title": title,
        "content": content,
        "labels": ["Bollywood", "Entertainment", "Hindi Cinema"]
    }
    response = requests.post(url, headers=headers, json=post_data)
    if response.status_code == 200:
        post_url = response.json().get('url', 'N/A')
        print(f"✅ Post published! URL: {post_url}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        raise Exception("Publishing failed!")

if __name__ == "__main__":
    print("🎬 Bollywood Blog Writer starting...")
    topic = get_topic()
    print(f"📝 Topic: {topic}")
    image_url = get_image_url(topic)
    title, content = write_blog_post(topic)
    content = add_image_to_content(content, image_url, topic)
    print(f"✍️ Written: {title}")
    publish_to_blogger(title, content)
    print("🚀 Done!")
