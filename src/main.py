from data_ingestion import gather_all_validated_data
from nlp_engine import ProductionNLPEngine
from data_storage import DataLakeManager
from src.utils.logger import setup_custom_logger
from src.utils.drift_detector import calculate_sentiment_psi

logger = setup_custom_logger("MasterOrchestrator")

def run_pipeline():
    """
    Main orchestration loop for the multi-source data ingestion,
    inference, and storage pipeline.
    """
    logger.info("="*60)
    logger.info("STARTING RUNTIME: MULTI-SOURCE NLP AUTOMATION SYSTEM")
    logger.info("="*60)
    
    # Step 1: Multi-Source Extraction, Normalization & Pydantic Validation Gates
    raw_clean_records = gather_all_validated_data()
    if not raw_clean_records:
        logger.warning("Pipeline run terminated: Zero records passed validation steps.")
        logger.info("="*60)
        return
        
    # Step 2: Running Deep Learning Zero-Shot Routing & Sentiment Analysis
    nlp_engine = ProductionNLPEngine()
    processed_payload = nlp_engine.process_linguistic_inference(raw_clean_records)
    
    # Step 3: Run MLOps Concept Drift and Sentiment Shift Detection
    if processed_payload:
        fresh_sentiments = [row["sentiment_label"] for row in processed_payload]
        # Compare current run metrics against our historical baseline dataset
        historical_baseline_distribution = ["Neutral", "Positive", "Neutral", "Negative", "Neutral", "Positive"]
        calculate_sentiment_psi(historical_baseline_distribution, fresh_sentiments)
    
    # Step 4: Incremental Deduplication and Commit to Hugging Face Data Lake
    storage = DataLakeManager()
    storage.append_and_sync(processed_payload)
    
    logger.info("="*60)
    logger.info("CYCLE SUCCESSFUL: Versioned updates pushed to Hugging Face Hub.")
    logger.info("="*60)

if __name__ == "__main__":
    run_pipeline()