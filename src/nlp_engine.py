from transformers import pipeline
from src.utils.logger import setup_custom_logger

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
        
        # Broad keywords used to screen out non-AI rows before running inference
        self.token_filter_keywords = ["openai", "gpt", "chatgpt", "sam altman", "anthropic", "claude", "sonnet", "gemini", "deepmind", "llama", "open-source llm", "meta ai"]
        
        self.sentiment_map = {
            "negative": "Negative",
            "neutral": "Neutral",
            "positive": "Positive"
        }

    def process_linguistic_inference(self, records: list) -> list:
        if not records:
            return []
            
        # Advanced NLP Practice: Filter out non-AI rows first to prevent computing overhead
        pre_filtered_records = []
        for r in records:
            text_lower = r["raw_text"].lower()
            if any(keyword in text_lower for keyword in self.token_filter_keywords):
                pre_filtered_records.append(r)
                
        if not pre_filtered_records:
            logger.info("No incoming records passed the AI keyword pre-filtering phase.")
            return []
            
        logger.info(f"Running dual-stage deep learning inference on {len(pre_filtered_records)} filtered rows...")
        texts = [row["raw_text"] for row in pre_filtered_records]
        
        try:
            logger.info("Executing Stage 1: Zero-Shot Entity Extraction...")
            entity_outputs = self.zero_shot_pipe(texts, candidate_labels=self.candidate_brands, hypothesis_template="This text discusses {}")
            
            logger.info("Executing Stage 2: Transformer Batch Sentiment Classification...")
            sentiment_outputs = self.sentiment_pipe(texts, truncation=True, max_length=256)
            
            enriched_records = []
            for idx, record in enumerate(pre_filtered_records):
                ent_res = entity_outputs[idx]
                sent_res = sentiment_outputs[idx]
                
                # Quality Gate: Only retain high-confidence predictions (>35%)
                top_score = ent_res["scores"][0]
                if top_score >= 0.35:
                    record["target_entity"] = ent_res["labels"][0]
                    raw_label = sent_res["label"].lower()
                    record["sentiment_label"] = self.sentiment_map.get(raw_label, "Neutral")
                    record["sentiment_score"] = round(float(sent_res["score"]), 4)
                    enriched_records.append(record)
                    
            logger.info(f"NLP Inference successful. Retained {len(enriched_records)} records.")
            return enriched_records
            
        except Exception as e:
            logger.error(f"Error encountered during deep learning inference pass: {e}")
            return []