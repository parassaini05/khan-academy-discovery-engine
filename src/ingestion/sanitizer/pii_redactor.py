"""
COPPA & FERPA Aligned PII Redactor for Student Feedback
Sanitizes emails, phone numbers, student names, teacher/school identifiers, IP addresses, and handles.
"""

import re
from typing import Tuple, Dict, Any

# Pre-compiled regex patterns for deterministic PII redaction
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
PHONE_PATTERN = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
IPV4_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
URL_PATTERN = re.compile(r'https?://[^\s]+|www\.[^\s]+')
USERNAME_PATTERN = re.compile(r'(?:u/|@)[A-Za-z0-9_.-]+')

# School and Teacher context patterns
TEACHER_SCHOOL_PATTERN = re.compile(
    r'\b(?:Mr\.|Mrs\.|Ms\.|Coach|Dr\.)\s+[A-Z][a-z]+(?:\s+at\s+[A-Z][a-zA-Z\s]+(?:High|Middle|Elementary|School|Academy))?\b',
    re.IGNORECASE
)
STUDENT_INTRO_PATTERN = re.compile(
    r'\b(?:my name is|i am|i\'m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
    re.IGNORECASE
)

def redact_pii(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Sanitizes student feedback text, replacing any sensitive PII with standardized redaction tokens.
    Returns:
        (sanitized_text, redaction_metrics)
    """
    if not text:
        return "", {}

    redaction_counts = {
        "emails": 0,
        "phones": 0,
        "ips": 0,
        "urls": 0,
        "usernames": 0,
        "teachers_schools": 0,
        "names": 0
    }

    # 1. Emails
    text, n = EMAIL_PATTERN.subn("[REDACTED_EMAIL]", text)
    redaction_counts["emails"] = n

    # 2. Phone numbers
    text, n = PHONE_PATTERN.subn("[REDACTED_PHONE]", text)
    redaction_counts["phones"] = n

    # 3. IP Addresses
    text, n = IPV4_PATTERN.subn("[REDACTED_IP]", text)
    redaction_counts["ips"] = n

    # 4. URLs
    text, n = URL_PATTERN.subn("[REDACTED_URL]", text)
    redaction_counts["urls"] = n

    # 5. Usernames / Handles
    text, n = USERNAME_PATTERN.subn("[REDACTED_USER]", text)
    redaction_counts["usernames"] = n

    # 6. Teacher & School context
    text, n = TEACHER_SCHOOL_PATTERN.subn("[REDACTED_TEACHER_OR_SCHOOL]", text)
    redaction_counts["teachers_schools"] = n

    # 7. Student Self-Introduction names
    def _student_repl(match):
        return f"i am [REDACTED_STUDENT_NAME]"
    text, n = STUDENT_INTRO_PATTERN.subn(_student_repl, text)
    redaction_counts["names"] = n

    return text.strip(), redaction_counts

# Regex for detecting Emoji characters across Unicode ranges (SMP emojis U+10000-U+10FFFF plus misc symbols U+2600-U+27BF)
EMOJI_PATTERN = re.compile(
    r'[\U00010000-\U0010FFFF\u2600-\u26FF\u2700-\u27BF\uFE00-\uFE0F]',
    flags=re.UNICODE
)

# Regex for Devanagari script (Hindi)
HINDI_DEVANAGARI_PATTERN = re.compile(r'[\u0900-\u097F]')

# Common Hindi / Hinglish tokens (case-insensitive)
HINDI_ROMANIZED_TOKENS = {
    "accha", "achha", "bahut", "bohot", "nahi", "nahin", "karo", "karna", "padhai",
    "samajh", "samaj", "bhai", "yeh", "kya", "kaise", "mujhe", "mera", "meri",
    "hai", "hain", "tha", "thi", "kuch", "thik", "theek", "acche", "bakwas", "padho",
    "karo", "padhaye", "matlab", "shukriya", "dhanyawad"
}

def is_valid_learner_text(text: str, min_words: int = 8) -> bool:
    """
    Validates learner feedback against strict hygiene criteria:
    1. Minimum 8 words (discards sub-8 word entries).
    2. Strict zero-emoji policy (discards any text containing emojis).
    3. Language hygiene (discards Devanagari Hindi script and Hinglish phrasing).
    """
    if not text or not text.strip():
        return False

    # Rule 2: Zero-Emoji Check
    if EMOJI_PATTERN.search(text):
        return False

    # Rule 3: Hindi Language Check (Devanagari script)
    if HINDI_DEVANAGARI_PATTERN.search(text):
        return False

    # Rule 1: Word count check (minimum 8 words)
    words = [w.lower() for w in re.findall(r'\b[A-Za-z0-9\'-]+\b', text)]
    if len(words) < min_words:
        return False

    # Rule 3b: Romanized Hindi / Hinglish check (>= 2 common Hindi words)
    hindi_token_count = sum(1 for w in words if w in HINDI_ROMANIZED_TOKENS)
    if hindi_token_count >= 2:
        return False

    # Check for basic ASCII/English character density
    ascii_chars = sum(1 for c in text if c.isascii() and (c.isalnum() or c.isspace()))
    if ascii_chars / len(text) < 0.65:
        return False

    # Check for repetitive single-word spam (low lexical diversity)
    if len(words) >= 5 and (len(set(words)) / len(words)) < 0.35:
        return False

    return True
