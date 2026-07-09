import re
import html
import unicodedata

def sanitize_text(raw_text: str) -> str:
    """
    Advanced Text Cleansing Pipeline:
    Applies Unicode NFKC normalization, eliminates URL fragments, sanitizes 
    HTML escapes, and reduces chaotic punctuation patterns.
    """
    if not raw_text or not isinstance(raw_text, str):
        return ""
    
    # 1. Standardize character variants via Unicode Compatibility Composition (NFKC)
    text = unicodedata.normalize('NFKC', raw_text)
    
    # 2. Extract and translate complex HTML entities safely
    text = html.unescape(text)
    
    # 3. Strip out URLs so they don't impact model tokenization loops
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # 4. Clean up common markdown anomalies or stray symbols frequently found on hacker news
    text = re.sub(r'[*_`\[\]()]', '', text)
    
    # 5. Restrict character layout strictly to valid keyboard alphanumerics and core punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"\-]', '', text)
    
    # 6. Compress multiple white spaces into a clean single frame
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text