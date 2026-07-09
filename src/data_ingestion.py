import requests
from datetime import datetime
from src.utils.logger import setup_custom_logger
from src.utils.preprocessor import sanitize_text
from src.utils.validator import enforce_schema_quality

logger = setup_custom_logger("DataIngestionEngine")

TARGET_ENTITIES = {
    "openai": ["openai", "gpt-4", "chatgpt", "gpt-4o", "sam altman"],
    "anthropic": ["anthropic", "claude", "sonnet", "opus"],
    "google": ["google gemini", "gemini", "deepmind"],
    "meta": ["llama", "llama3", "open-source llm"]
}

def fetch_hn_top_stories():
    """Queries the open Hacker News API endpoint to extract current active entries."""
    logger.info("Initializing baseline ingestion stream retrieval from Hacker News API...")
    try:
        top_ids_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(top_ids_url, timeout=10)
        response.raise_for_status()
        story_ids = response.json()[:100]
        
        verified_stories = []
        for story_id in story_ids:
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_data = requests.get(story_url, timeout=5).json()
                
                if story_data and "title" in story_data:
                    # Clean the incoming text using our modular preprocessor utility
                    cleaned_title = sanitize_text(story_data["title"])
                    
                    raw_payload = {
                        "id": f"hn_{story_id}",
                        "timestamp": datetime.fromtimestamp(story_data.get("time", datetime.now().timestamp())).strftime('%Y-%m-%d %H:%M:%S'),
                        "source": "HackerNews",
                        "raw_text": cleaned_title
                    }
                    
                    # Validate schema integrity using Pydantic via our validator utility
                    validated_record = enforce_schema_quality(raw_payload)
                    if validated_record:
                        # Convert Pydantic object back into a standard dictionary for downstream processing
                        verified_stories.append(validated_record.model_dump())
                        
            except Exception as item_err:
                logger.debug(f"Skipping transient anomaly on story item ID {story_id}: {item_err}")
                continue
                
        logger.info(f"Ingestion extraction sequence finalized. Gathered {len(verified_stories)} safe database frames.")
        return verified_stories
        
    except Exception as network_err:
        logger.error(f"Critical System Interruption: Failed to bridge Hacker News REST session: {network_err}")
        return []

def extract_target_entities(text: str) -> str:
    """Applies categorical keyword matching rules against the text parameter."""
    text_lower = text.lower()
    for entity, keywords in TARGET_ENTITIES.items():
        if any(keyword in text_lower for keyword in keywords):
            return entity.capitalize()
    return "Generic Tech"

def process_pipeline_ingestion():
    """Main ingestion orchestration node."""
    raw_stories = fetch_hn_top_stories()
    
    filtered_records = []
    for story in raw_stories:
        entity = extract_target_entities(story["raw_text"])
        if entity != "Generic Tech":
            story["target_entity"] = entity
            filtered_records.append(story)
            
    logger.info(f"Filtering pass executed. Isolated {len(filtered_records)} targeted GenAI telemetry data tracks.")
    return filtered_records

if __name__ == "__main__":
    process_pipeline_ingestion()