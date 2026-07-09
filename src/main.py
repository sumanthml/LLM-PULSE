from data_ingestion import process_pipeline_ingestion
from inference import SentimentEngine
from data_storage import DataLakeManager
from src.utils.logger import setup_custom_logger

logger = setup_custom_logger("MasterOrchestrator")

def run_pipeline():
    """Master orchestration execution loop."""
    logger.info("="*60)
    logger.info("STARTING RUNTIME CYCLE: LLM-PULSE AUTOMATED INFRASTRUCTURE")
    logger.info("="*60)
    
    # Stage 1: Data Ingestion & Rule-based Targeting
    raw_target_records = process_pipeline_ingestion()
    if not raw_target_records:
        logger.warning("Pipeline Execution Halted: No fresh target ecosystem records harvested.")
        logger.info("="*60)
        return
        
    # Stage 2: Machine Learning Sentiment Analysis Inference
    ml_engine = SentimentEngine()
    enriched_records = ml_engine.analyze_batch(raw_target_records)
    
    # Stage 3: Target Data Lake Persistence & Remote Synchronization
    storage_manager = DataLakeManager()
    storage_manager.append_and_sync(enriched_records)
    
    logger.info("="*60)
    logger.info("RUNTIME CYCLE SUCCESSFUL: All pipeline stages completed.")
    logger.info("="*60)

if __name__ == "__main__":
    run_pipeline()