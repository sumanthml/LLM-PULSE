import numpy as np
from src.utils.logger import setup_custom_logger

logger = setup_custom_logger("MLOpsDriftTelemetry")

def calculate_sentiment_psi(baseline_labels: list, target_labels: list) -> float:
    """
    Computes Population Stability Index (PSI) to detect concept drift
    between historical sentiment profiles and fresh ingestion batches.
    PSI < 0.1: Stable | PSI 0.1 - 0.2: Moderate Drift | PSI > 0.2: Significant Shift
    """
    if not baseline_labels or not target_labels:
        return 0.0

    categories = ["Positive", "Neutral", "Negative"]
    
    # Calculate categorical frequency distributions
    b_counts = {cat: baseline_labels.count(cat) for cat in categories}
    t_counts = {cat: target_labels.count(cat) for cat in categories}
    
    # Convert to probability distributions with minimal epsilon smoothing to avoid division-by-zero
    len_b, len_t = len(baseline_labels), len(target_labels)
    b_expected = np.array([(b_counts[cat] / len_b) if len_b > 0 else 1/3 for cat in categories]) + 1e-4
    t_actual = np.array([(t_counts[cat] / len_t) if len_t > 0 else 1/3 for cat in categories]) + 1e-4
    
    # Normalize back to exact 1.0 probability boundaries
    b_expected /= np.sum(b_expected)
    t_actual /= np.sum(t_actual)
    
    # Execute the formal PSI statistical mathematical computation equation
    psi_value = np.sum((t_actual - b_expected) * np.log(t_actual / b_expected))
    
    logger.info(f"Calculated Sentiment Population Stability Index (PSI): {psi_value:.4f}")
    if psi_value > 0.2:
        logger.warning("ALERT: Significant real-world sentiment drift detected in production streams!")
        
    return float(psi_value)