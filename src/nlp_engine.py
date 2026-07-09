import sys
import os

# Automatic Path Injector
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from transformers import pipeline
from src.utils.logger import setup_custom_logger
from src.utils.summarizer import generate_executive_brief
from src.utils.vector_ops import compute_lightweight_token_hash

logger = setup_custom_logger("AdvancedNLPEngine")

class ProductionNLPEngine:
    def __init__(self):
        logger.info("Loading CPU-Optimized Distilled RoBERTa Sentiment Architecture...")
        self.sentiment_pipe = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=-1
        )
        
        logger.info("Loading High-Efficiency Zero-Shot Extraction Frame...")
        self.zero_shot_pipe = pipeline(
            "zero-shot-classification",
            model="typeform/distilbert-base-uncased-mnli",
            device=-1
        )
        
        self.candidate_brands = ["OpenAI", "Anthropic", "Google Gemini", "Meta Llama"]
        self.token_filter_keywords = ["openai", "gpt", "chatgpt", "sam altman", "anthropic", "claude", "sonnet", "opus", "gemini", "deepmind", "llama", "open-source llm", "meta ai"]
        
        self.sentiment_map = {
            "negative": "Negative",
            "neutral": "Neutral",
            "positive": "Positive"
        }

    def process_linguistic_inference(self, records: list) -> list:
        if not records:
            return []
            
        pre_filtered_records = []
        for r in records:
            text_lower = r["raw_text"].lower()
            if any(keyword in text_lower for keyword in self.token_filter_keywords):
                pre_filtered_records.append(r)
                
        if not pre_filtered_records:
            logger.info("Zero records matched the target domain keyword filters.")
            return []
            
        logger.info(f"Running continuous NLP inference across {len(pre_filtered_records)} targeted records...")
        texts = [row["raw_text"] for row in pre_filtered_records]
        
        try:
            logger.info("Executing Stage 1: Zero-Shot Entity Classification...")
            entity_outputs = self.zero_shot_pipe(texts, candidate_labels=self.candidate_brands, hypothesis_template="This text discusses {}")
            
            logger.info("Executing Stage 2: Transformer Batch Sentiment Classification...")
            sentiment_outputs = self.sentiment_pipe(texts, truncation=True, max_length=256)
            
            enriched_records = []
            for idx, record in enumerate(pre_filtered_records):
                ent_res = entity_outputs[idx]
                sent_res = sentiment_outputs[idx]
                
                top_score = ent_res["scores"][0]
                if top_score >= 0.35:
                    record["target_entity"] = ent_res["labels"][0]
                    raw_label = sent_res["label"].lower()
                    record["sentiment_label"] = self.sentiment_map.get(raw_label, "Neutral")
                    record["sentiment_score"] = round(float(sent_res["score"]), 4)
                    
                    # Core Feature Enrichment Connections
                    record["executive_summary"] = generate_executive_brief(record["raw_text"], record["target_entity"])
                    record["semantic_vector"] = str(compute_lightweight_token_hash(record["raw_text"]))
                    
                    enriched_records.append(record)
                    
            logger.info(f"NLP Engine evaluation complete. Saved {len(enriched_records)} premium rows.")
            return enriched_records
            
        except Exception as e:
            logger.error(f"Critical execution error during model computation passes: {e}")
            return []