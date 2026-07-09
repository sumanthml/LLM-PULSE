import requests
import json
from datetime import datetime

# Define the GenAI entities we want our data pipeline to track
TARGET_ENTITIES = {
    "openai": ["openai", "gpt-4", "chatgpt", "gpt-4o", "sam altman"],
    "anthropic": ["anthropic", "claude", "sonnet", "opus"],
    "google": ["google gemini", "gemini", "deepmind"],
    "meta": ["llama", "llama3", "open-source llm"]
}

def fetch_hn_top_stories():
    """Fetches trending tech stories directly from the open Hacker News API."""
    print("Initializing Data Ingestion from Hacker News...")
    try:
        # Get the top 100 current trending story IDs
        top_ids_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(top_ids_url, timeout=10)
        story_ids = response.json()[:100]
        
        stories = []
        for story_id in story_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story_data = requests.get(story_url, timeout=5).json()
            
            if story_data and "title" in story_data:
                stories.append({
                    "id": f"hn_{story_id}",
                    "timestamp": datetime.fromtimestamp(story_data.get("time", datetime.now().timestamp())).strftime('%Y-%m-%d %H:%M:%S'),
                    "source": "HackerNews",
                    "raw_text": story_data["title"]
                })
        print(f"Successfully scraped {len(stories)} stories from Hacker News.")
        return stories
    except Exception as e:
        print(f"Error fetching data from Hacker News API: {e}")
        return []

def extract_target_entities(text):
    """
    Named Entity Recognition (NER) Rule:
    Scans raw text to match it to a targeted AI ecosystem ecosystem.
    """
    text_lower = text.lower()
    for entity, keywords in TARGET_ENTITIES.items():
        if any(keyword in text_lower for keyword in keywords):
            return entity.capitalize()
    return "Generic Tech"

def process_pipeline_ingestion():
    """Orchestrates data harvesting and runs the mapping logic."""
    raw_stories = fetch_hn_top_stories()
    
    processed_records = []
    for story in raw_stories:
        entity = extract_target_entities(story["raw_text"])
        
        # Only pipeline articles discussing our core GenAI targets to save compute
        if entity != "Generic Tech":
            story["target_entity"] = entity
            processed_records.append(story)
            
    print(f"Filtered down to {len(processed_records)} highly relevant GenAI conversations.")
    return processed_records

if __name__ == "__main__":
    # Test execution
    data = process_pipeline_ingestion()
    if data:
        print(f"Sample Ingested Row: {data[0]}")