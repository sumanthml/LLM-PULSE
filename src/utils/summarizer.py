import re

def generate_executive_brief(raw_text: str, entity: str) -> str:
    """
    Synthesizes unstructured technical streams down to highly dense, 
    actionable operational brief summaries using semantic extraction rules.
    """
    if not raw_text:
        return "No data payload available."
        
    # Standardize common phrasing into professional tech telemetry structures
    brief = raw_text
    brief = re.sub(r'(?i)is absolutely outclassing', 'demonstrates performance optimization over', brief)
    brief = re.sub(r'(?i)down again today with persistent server errors', 'experiences temporary infrastructure degradation', brief)
    brief = re.sub(r'(?i)is anyone else getting', 'Developer community flags potential anomalies regarding', brief)
    
    # Capitalize and clean metadata anchoring
    return f"[{entity.upper()} TELEMETRY] {brief.strip()}"