import sys
import os

# Automatic Path Injector
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import feedparser
from datetime import datetime
from src.utils.logger import setup_custom_logger
from src.utils.preprocessor import sanitize_text
from src.utils.validator import enforce_schema_quality

logger = setup_custom_logger("MultiSourceIngestionEngine")

RSS_FEEDS = {
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "AWS Machine Learning": "https://aws.amazon.com/blogs/machine-learning/feed/",
    "Wired AI": "https://www.wired.com/category/science/ai/feed/"
}

def fetch_hacker_news_stream():
    logger.info("Harvesting from Channel 1: Hacker News live feed API...")
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(url, timeout=10)
        story_ids = response.json()[:40]
        records = []
        for s_id in story_ids:
            try:
                s_url = f"https://hacker-news.firebaseio.com/v0/item/{s_id}.json"
                data = requests.get(s_url, timeout=5).json()
                if data and "title" in data:
                    records.append({
                        "id": f"hn_{s_id}",
                        "timestamp": datetime.fromtimestamp(data.get("time", datetime.now().timestamp())).strftime('%Y-%m-%d %H:%M:%S'),
                        "source": "HackerNews",
                        "raw_text": data["title"]
                    })
            except Exception:
                continue
        return records
    except Exception as e:
        logger.error(f"HN Stream exception: {e}")
        return []

def fetch_rss_streams():
    logger.info("Harvesting from Channels 2-5: Global Tech Syndication RSS Feeds...")
    records = []
    for provider, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:25]:
                if "title" in entry:
                    clean_id = entry.get("id", entry.get("link", entry.title))
                    pub_time = entry.get("published", entry.get("updated", datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    records.append({
                        "id": f"rss_{hash(clean_id)}",
                        "timestamp": pub_time,
                        "source": provider,
                        "raw_text": entry.title
                    })
        except Exception as e:
            logger.warning(f"Skipping RSS stream {provider}: {e}")
    return records

def fetch_reddit_json_fallback():
    logger.info("Harvesting from Channel 6: Anonymous Raw Reddit JSON Scrapers...")
    records = []
    subreddits = ["MachineLearning", "LocalLLM"]
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    
    for sub in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sub}/new.json?limit=30"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                children = response.json().get("data", {}).get("children", [])
                for post in children:
                    data = post.get("data", {})
                    if "title" in data:
                        records.append({
                            "id": f"red_{data.get('id')}",
                            "timestamp": datetime.fromtimestamp(data.get("created_utc", datetime.now().timestamp())).strftime('%Y-%m-%d %H:%M:%S'),
                            "source": f"Reddit/r/{sub}",
                            "raw_text": data["title"]
                        })
        except Exception as e:
            logger.warning(f"Reddit scraper bypassed for r/{sub} due to rate limits: {e}")
    return records

def gather_all_validated_data():
    raw_payload = fetch_hacker_news_stream() + fetch_rss_streams() + fetch_reddit_json_fallback()
    logger.info(f"Aggregated {len(raw_payload)} total raw streaming rows across active channels.")
    
    clean_records = []
    for record in raw_payload:
        record["raw_text"] = sanitize_text(record["raw_text"])
        validated = enforce_schema_quality(record)
        if validated:
            clean_records.append(validated.model_dump())
    return clean_records

if __name__ == "__main__":
    gather_all_validated_data()