import anthropic
import requests
import json
import os
import random
from datetime import datetime

# ============================================================
# APNI SETTINGS YAHAN CHANGE KARO
# ============================================================

BLOG_TOPICS = [
    "Bollywood box office collection this week",
    "Latest Bollywood celebrity news",
    "Upcoming Bollywood movies 2025",
    "Bollywood celebrity relationships and gossip",
    "Best Bollywood songs trending on YouTube",
    "Bollywood actor fitness and lifestyle secrets",
    "Bollywood movie reviews and ratings",
    "OTT releases this week Bollywood",
    "Bollywood award shows and red carpet looks",
    "Bollywood controversies and viral moments",
]

# ============================================================

def get_topic():
    return random.choice(BLOG_TOPICS)

def write_blog_post(topic):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    
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
- Do NOT include the main title in HTML, only the body content with h2/p tags

Return format:
Line 1: Blog post title (plain text)
Line 2: Empty line  
Line 3 onwards: Full HTML blog content (only body content, no <html>/<head>/<body> tags)"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = message.content[0].text
    lines = response_text.split('\n')
    title = lines[0].strip()
    content = '\n'.join(lines[2:]).strip()
    
    return title, content

def get_access_token():
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": os.environ["BLOGGER_CLIENT_ID"],
        "client_secret": os.environ["BLOGGER_CLIENT_SECRET"],
        "refresh_token": os.environ["BLOGGER_REFRESH_TOKEN"],
        "grant_type": "refresh_token"
    }
    response = requests.post(token_url, data=data)
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
    title, content = write_blog_post(topic)
    print(f"✍️ Written: {title}")
    publish_to_blogger(title, content)
    print("🚀 Done!")
