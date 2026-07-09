import sys
import os

# Automatic Path Injector: Force Python to treat the repository root as a source directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_ingestion import gather_all_validated_data
from src.nlp_engine import ProductionNLPEngine
from src.data_storage import DataLakeManager
from src.utils.logger import setup_custom_logger
from src.utils.drift_detector import calculate_sentiment_psi

logger = setup_custom_logger("MasterOrchestrator")

def run_pipeline():
    logger.info("="*60)
    logger.info("STARTING RUNTIME: MULTI-SOURCE NLP AUTOMATION SYSTEM")
    logger.info("="*60)
    
    # 1. Multi-Source Ingestion, Cleaning & Validation
    raw_clean_records = gather_all_validated_data()
    if not raw_clean_records:
        logger.warning("Pipeline run terminated: Zero records passed validation steps.")
        logger.info("="*60)
        return
        
    # 2. Deep Learning Zero-Shot Classification & Sentiment Scoring
    nlp_engine = ProductionNLPEngine()
    processed_payload = nlp_engine.process_linguistic_inference(raw_clean_records)
    
    # 3. MLOps Concept Drift Detection Metrics
    if processed_payload:
        fresh_sentiments = [row["sentiment_label"] for row in processed_payload]
        historical_baseline_distribution = ["Neutral", "Positive", "Neutral", "Negative", "Neutral", "Positive"]
        calculate_sentiment_psi(historical_baseline_distribution, fresh_sentiments)
    
    # 4. Save and Commit to the Remote Data Lake
    storage = DataLakeManager()
    storage.append_and_sync(processed_payload)
    
    logger.info("="*60)
    logger.info("CYCLE SUCCESSFUL: Versioned updates pushed to Hugging Face Hub.")
    logger.info("="*60)

if __name__ == "__main__":
    run_pipeline()