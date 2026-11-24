"""
YouTube Comments Discovery Ingestion for Khan Academy
Extracts learner comments on core Algebra & Linear Equations instructional videos
Supports Google OAuth2 / API Key and parses comments into the Cognitive Struggle Taxonomy.
"""

import os
import json
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from openai import OpenAI
from fastembed import TextEmbedding

# Top Khan Academy Algebra & Linear Equation Video IDs
KHAN_ACADEMY_VIDEOS = [
    {"video_id": "bAerID24QJg", "title": "Linear equations with variables on both sides"},
    {"video_id": "Qyd_v3DGzTM", "title": "Why we do the same thing to both sides of an equation"},
    {"video_id": "f15zA0PhSek", "title": "Solving multi-step equations"},
    {"video_id": "Dopms4S_1m4", "title": "Distributive property with linear equations"},
    {"video_id": "1c5HY3z4k8M", "title": "Linear equation word problems"}
]

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
CREDENTIALS_PATH = 'd:/Khan Academy - Portfolio/credentials/google_client_secret.json'
TOKEN_PATH = 'd:/Khan Academy - Portfolio/credentials/token.json'
OUTPUT_DATA_DIR = 'd:/Khan Academy - Portfolio/data'

def get_authenticated_service():
    """Gets authenticated YouTube service via token or OAuth flow."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            print(f"Error loading existing token: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            print("OAuth token not yet authorized.")
            return None

    return build('youtube', 'v3', credentials=creds)

def sanitize_comment(text: str) -> str:
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
    text = re.sub(r'https?://\S+', '[REDACTED_URL]', text)
    return text.strip()

def fetch_youtube_comments_via_api(youtube, max_per_video=30):
    """Fetches comments from curated Khan Academy algebra videos."""
    all_comments = []
    for vid_info in KHAN_ACADEMY_VIDEOS:
        vid_id = vid_info["video_id"]
        vid_title = vid_info["title"]
        print(f"Fetching comments for video: {vid_title} ({vid_id})...")
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=vid_id,
                maxResults=max_per_video,
                textFormat="plainText",
                order="relevance"
            )
            response = request.execute()
            for item in response.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                text = snippet.get("textDisplay", "")
                if len(text.strip()) > 20:
                    all_comments.append({
                        "video_id": vid_id,
                        "video_title": vid_title,
                        "author": snippet.get("authorDisplayName", "Learner"),
                        "like_count": snippet.get("likeCount", 0),
                        "published_at": snippet.get("publishedAt", ""),
                        "sanitized_text": sanitize_comment(text)
                    })
        except Exception as e:
            print(f"Error fetching comments for video {vid_id}: {e}")
    return all_comments
