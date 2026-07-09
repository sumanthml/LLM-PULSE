import requests
import feedparser
from datetime import datetime
from src.utils.logger import setup_custom_logger
from src.utils.preprocessor import sanitize_text
from src.utils.validator import enforce_schema_quality

logger = setup_custom_logger("MultiSourceIngestionEngine")

# 4 Core News Aggregator Streams
RSS_FEEDS = {
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "AWS Machine Learning": "https://aws.amazon.com/blogs/machine-learning/feed/",
    "Wired AI": "https://www.wired.com/category/science/ai/feed/"
}

def fetch_hacker_news_stream():
    """Source 1: Queries Hacker News REST API for active trending items."""
    logger.info("Harvesting from Source 1: Hacker News API...")
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
        logger.error(f"HN Stream failure: {e}")
        return []

def fetch_rss_streams():
    """Sources 2, 3, 4, 5: Synthesizes high-volume syndication feeds."""
    logger.info("Harvesting from Sources 2-5: Enterprise RSS Networks...")
    records = []
    for provider, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:
                if "title" in entry:
                    clean_id = entry.get("id", entry.get("link", entry.title))
                    records.append({
                        "id": f"rss_{hash(clean_id)}",
                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "source": provider,
                        "raw_text": entry.title
                    })
        except Exception as e:
            logger.warning(f"Skipping RSS stream {provider}: {e}")
    return records

def fetch_reddit_json_fallback():
    """Source 6: Headless raw JSON stream extraction bypassing developer API blocks."""
    logger.info("Harvesting from Source 6: Headless Reddit JSON Stream (/r/MachineLearning)...")
    try:
        url = "https://www.reddit.com/r/MachineLearning/new.json"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        children = response.json().get("data", {}).get("children", [])
        
        records = []
        for post in children[:30]:
            data = post.get("data", {})
            if "title" in data:
                records.append({
                    "id": f"red_{data.get('id')}",
                    "timestamp": datetime.fromtimestamp(data.get("created_utc", datetime.now().timestamp())).strftime('%Y-%m-%d %H:%M:%S'),
                    "source": "Reddit/r/MachineLearning",
                    "raw_text": data["title"]
                })
        return records
    except Exception as e:
        logger.warning(f"Reddit headless stream bypassed due to strict cloud network limits: {e}")
        return []

def gather_all_validated_data():
    """Synthesizes and validates all active network ingestion frames."""
    raw_payload = fetch_hacker_news_stream() + fetch_rss_streams() + fetch_reddit_json_fallback()
    logger.info(f"Aggregated {len(raw_payload)} raw text metrics across 6 ingestion channels.")
    
    clean_records = []
    for record in raw_payload:
        record["raw_text"] = sanitize_text(record["raw_text"])
        validated = enforce_schema_quality(record)
        if validated:
            clean_records.append(validated.model_dump())
    return clean_records

if __name__ == "__main__":
    gather_all_validated_data()