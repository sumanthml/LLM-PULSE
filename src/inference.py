import os
from transformers import pipeline

class SentimentEngine:
    def __init__(self):
        """
        Initializes a lightweight, distilled transformer pipeline.
        Using a distilled model optimized for CPU ensures fast processing 
        and prevents timeouts on free cloud runners.
        """
        print("Loading CPU-optimized Transformer model from Hugging Face Hub...")
        # A highly accurate, distilled RoBERTa model fine-tuned for generic sentiment analysis
        self.classifier = pipeline(
            "sentiment-analysis", 
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=-1 # Forces CPU execution explicitly
        )
        
        # Map model outputs (LABEL_0, LABEL_1, LABEL_2) to readable strings
        self.label_mapping = {
            "negative": "Negative",
            "neutral": "Neutral",
            "positive": "Positive"
        }

    def analyze_batch(self, records):
        """
        Accepts ingested dictionary rows, extracts text data, 
        and updates the records with ML inference insights.
        """
        if not records:
            print("No new target entity records found for inference evaluation.")
            return []

        print(f"Executing batch ML inference on {len(records)} items...")
        
        # Batching texts together optimizes inference speeds on CPU runtimes
        texts = [row["raw_text"] for row in records]
        
        try:
            model_outputs = self.classifier(texts, truncation=True, max_length=512)
            
            for idx, output in enumerate(model_outputs):
                # Clean up raw output label formatting from model configurations
                raw_label = output["label"].lower()
                clean_label = self.label_mapping.get(raw_label, "Neutral")
                
                # Append computed inference payloads to the strict data schema
                records[idx]["sentiment_label"] = clean_label
                records[idx]["sentiment_score"] = round(float(output["score"]), 4)
                
            print("Batch inference process completed successfully.")
            return records
            
        except Exception as e:
            print(f"Error encountered during model execution loop: {e}")
            return records

if __name__ == "__main__":
    # Test sample simulation
    mock_data = [
        {"id": "hn_123", "timestamp": "2026-07-09 12:00:00", "source": "HackerNews", "raw_text": "Claude 3.5 Sonnet is absolutely outclassing every other LLM right now.", "target_entity": "Anthropic"},
        {"id": "hn_456", "timestamp": "2026-07-09 12:05:00", "source": "HackerNews", "raw_text": "OpenAI api down again today with persistent server errors.", "target_entity": "Openai"}
    ]
    
    engine = SentimentEngine()
    results = engine.analyze_batch(mock_data)
    print("\nSimulation Results:")
    import pprint
    pprint.pprint(results)