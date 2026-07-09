import sys
from data_ingestion import process_pipeline_ingestion
from inference import SentimentEngine
from data_storage import DataLakeManager

def run_pipeline():
    """
    The master orchestration function that connects our ETL 
    and Continuous Inference stages into a cohesive operational loop.
    """
    print("="*60)
    print("STARTING RUNTIME CYCLE: LLM-PULSE AUTOMATED PIPELINE")
    print("="*60)
    
    # Stage 1: Data Ingestion & Rule-based Targeting
    raw_target_records = process_pipeline_ingestion()
    if not raw_target_records:
        print("Pipeline Execution Halted: No fresh target ecosystem records harvested.")
        print("="*60)
        return
        
    # Stage 2: Machine Learning Sentiment Analysis Inference
    ml_engine = SentimentEngine()
    enriched_records = ml_engine.analyze_batch(raw_target_records)
    
    # Stage 3: Target Data Lake Persistence & Remote Synchronization
    storage_manager = DataLakeManager()
    storage_manager.append_and_sync(enriched_records)
    
    print("="*60)
    print("RUNTIME CYCLE SUCCESSFUL: All pipeline stages completed.")
    print("="*60)

if __name__ == "__main__":
    run_pipeline()