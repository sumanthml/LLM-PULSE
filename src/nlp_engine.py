import torch
from transformers import pipeline
from src.utils.logger import setup_custom_logger

logger = setup_custom_logger("AdvancedNLPEngine")

class ProductionNLPEngine:
    def __init__(self):
        """
        Loads optimized deep-learning transformers from the Hugging Face registry.
        """
        logger.info("Instantiating CPU-bound Twitter-RoBERTa Sentiment Classifier...")
        self.sentiment_pipe = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=-1
        )
        
        logger.info("Instantiating dynamic Zero-Shot Brand Identification Engine...")
        self.zero_shot_pipe = pipeline(
            "zero-shot-classification",
            model="typeform/distilbert-base-uncased-mnli",
            device=-1
        )
        
        # Dynamic extraction targets evaluated across raw unstructured text frames
        self.candidate_brands = ["OpenAI", "Anthropic", "Google Gemini", "Meta Llama"]
        
        self.sentiment_map = {
            "negative": "Negative",
            "neutral": "Neutral",
            "positive": "Positive"
        }

    def process_linguistic_inference(self, records: list) -> list:
        """
        Runs dual-stage Deep Learning inference across ingested data.
        Performs dynamic entity mapping and computes text sentiment scores.
        """
        if not records:
            return []
            
        logger.info(f"Running inference sequence across {len(records)} verified text frames...")
        texts = [row["raw_text"] for row in records]
        
        try:
            # Stage 1: Zero-Shot Entity Classification (Removes hardcoded lists)
            logger.info("Executing Stage 1: Zero-Shot Entity Extraction...")
            entity_outputs = self.zero_shot_pipe(texts, candidate_labels=self.candidate_brands, hypothesis_template="This text discusses {}")
            
            # Stage 2: Transformer Batch Sentiment Analysis
            logger.info("Executing Stage 2: Semantic Tone Extraction...")
            sentiment_outputs = self.sentiment_pipe(texts, truncation=True, max_length=256)
            
            enriched_records = []
            for idx, record in enumerate(records):
                ent_res = entity_outputs[idx]
                sent_res = sentiment_outputs[idx]
                
                # MLOps Quality Control Gate: Only keep records with high classification confidence (>35%)
                top_score = ent_res["scores"][0]
                if top_score >= 0.35:
                    record["target_entity"] = ent_res["labels"][0]
                    raw_label = sent_res["label"].lower()
                    record["sentiment_label"] = self.sentiment_map.get(raw_label, "Neutral")
                    record["sentiment_score"] = round(float(sent_res["score"]), 4)
                    enriched_records.append(record)
                    
            logger.info(f"NLP Inference loop complete. Retained {len(enriched_records)} highly relevant records.")
            return enriched_records
            
        except Exception as e:
            logger.error(f"Downstream Deep Learning compilation error: {e}")
            return records