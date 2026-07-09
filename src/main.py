from data_ingestion import gather_all_validated_data
from nlp_engine import ProductionNLPEngine
from data_storage import DataLakeManager
from src.utils.logger import setup_custom_logger

logger = setup_custom_logger("MasterOrchestrator")

def run_pipeline():
    logger.info("="*60)
    logger.info("STARTING RUNTIME: MULTI-SOURCE NLP PIPELINE")
    logger.info("="*60)
    
    # 1. Multi-Source Ingestion & Sanitization
    raw_clean_records = gather_all_validated_data()
    if not raw_clean_records:
        logger.warning("Pipeline execution halted: Empty ingestion array.")
        return
        
    # 2. Deep Learning Zero-Shot Classification & Sentiment Extraction
    nlp_engine = ProductionNLPEngine()
    processed_payload = nlp_engine.process_linguistic_inference(raw_clean_records)
    
    # 3. Synchronize Records with Versioned Storage
    storage = DataLakeManager()
    storage.append_and_sync(processed_payload)
    
    logger.info("="*60)
    logger.info("CYCLE COMPLETE: 0-SHOT ENTITY EXTRACTION RESOLVED")
    logger.info("="*60)

if __name__ == "__main__":
    run_pipeline()