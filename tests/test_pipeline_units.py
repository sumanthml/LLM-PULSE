import pytest
from src.utils.preprocessor import sanitize_text
from src.utils.validator import enforce_schema_quality

def test_text_sanitization_html_and_urls():
    """Verifies that the text preprocessor strips out messy raw web artifacts cleanly."""
    input_text = "Check this model out at https://test.com &amp; it's fire! &#x27;Cool&#x27;"
    expected_output = "Check this model out at it's fire! 'Cool'"
    assert sanitize_text(input_text) == expected_output

def test_validator_contract_rejection():
    """Guarantees that our strict Pydantic layer catches empty or malformed dictionaries."""
    corrupt_payload = {
        "id": "   ",  # Invalid empty space string
        "timestamp": "2026-07-09 12:00:00",
        "source": "HackerNews",
        "raw_text": ""  # Corrupt empty string block
    }
    assert enforce_schema_quality(corrupt_payload) is None