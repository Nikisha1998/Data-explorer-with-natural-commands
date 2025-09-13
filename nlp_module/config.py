from typing import Dict, Any

class NLPConfig:
    """Configuration for NLP module"""
    
    # Query classification patterns
    SPECIFIC_PATTERNS = [
        r'\b(top|bottom)\s+\d+\b',
        r'\b\w+\s*[=<>]+\s*\w+\b', 
        r'\bsum|count|avg|mean|median|min|max\b',
        r'\bfilter|sort|group|pivot\b',
        r'\b\d{4}\b|\b(january|february|march|q1|q2|quarter)\b'
    ]
    
    AMBIGUOUS_PATTERNS = [
        r'\b(performance|analysis|trends?|patterns?)\b',
        r'\b(best|top|good)\b(?!\s+\d+)',
        r'\bseasonality\b',
        r'\bcompare\b(?!\s+\w+\s+to\s+\w+)',
    ]
    
    VAGUE_PATTERNS = [
        r'\b(show|tell|give)\s+me\b',
        r'\bwhat\s+about\b',
        r'\bhow\s+is\b',
        r'\banything\s+(interesting|good|useful)\b',
        r'^(hi|hello|help)$'
    ]
    
    # Default suggestions limits
    MAX_SUGGESTIONS = 3
    MAX_ALTERNATIVES = 2
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.6
    LOW_CONFIDENCE = 0.4
