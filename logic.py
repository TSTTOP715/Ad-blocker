import re
import os
import sqlite3


URL_PATTERN = re.compile(r'(https?://\S+|www\.\S+|\b[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\b)')
AD_KEYWORDS = [""]
DB_NAME = 'bot_database.db'


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS banned_words (
                chat_id INTEGER,
                word TEXT,
                PRIMARY KEY (chat_id, word)
            )
        ''')
        conn.commit()


def add_banned_word(chat_id: int, word: str) -> bool:
    word_lower = word.lower().strip()
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO banned_words (chat_id, word) VALUES (?, ?)', (chat_id, word_lower))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def remove_banned_word(chat_id: int, word: str) -> bool:
    word_lower = word.lower().strip()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM banned_words WHERE chat_id = ? AND word = ?', (chat_id, word_lower))
        changes = conn.total_changes
        conn.commit()
        return changes > 0

def get_banned_words(chat_id: int) -> list:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT word FROM banned_words WHERE chat_id = ?', (chat_id,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]

def is_link(text: str, chat_id: int) -> bool: # проверка сообщения
    if not text:
        return False
    if URL_PATTERN.search(text):
        return True

    text_lower = text.lower()
    all_keywords = AD_KEYWORDS + get_banned_words(chat_id)
    
    for keyword in all_keywords:
        if keyword in text_lower:
            return True
    return False

def contains_telegram_entities(message) -> bool:
    entities = (message.entities or []) + (message.caption_entities or [])
    for entity in entities:
        if entity.type in ['url', 'text_link', 'mention']:
            return True
    return False

def is_admin(bot, chat_id, user_id) -> bool:
    try:
        status = bot.get_chat_member(chat_id, user_id).status
        return status in ['administrator', 'creator']
    except Exception:
        return False