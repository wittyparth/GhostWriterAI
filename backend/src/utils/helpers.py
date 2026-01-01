"""
Utility functions for the LinkedIn AI Agent.

Common helpers used across the codebase.
"""

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def count_characters(text: str) -> int:
    """Count characters in text (excluding whitespace)."""
    return len(re.sub(r'\s', '', text))


def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Estimate reading time in seconds."""
    words = count_words(text)
    minutes = words / words_per_minute
    return int(minutes * 60)


def extract_hashtags(text: str) -> list[str]:
    """Extract hashtags from text."""
    pattern = r'#(\w+)'
    return re.findall(pattern, text)


def validate_linkedin_content(content: str) -> dict[str, Any]:
    """
    Validate content against LinkedIn constraints.
    
    Returns validation result with issues.
    """
    from src.config.constants import (
        LINKEDIN_MAX_POST_LENGTH,
        LINKEDIN_MAX_HASHTAGS,
    )
    
    issues = []
    warnings = []
    
    char_count = len(content)
    word_count = count_words(content)
    hashtags = extract_hashtags(content)
    
    # Check character limit
    if char_count > LINKEDIN_MAX_POST_LENGTH:
        issues.append(f"Content exceeds {LINKEDIN_MAX_POST_LENGTH} chars (current: {char_count})")
    elif char_count > LINKEDIN_MAX_POST_LENGTH * 0.9:
        warnings.append(f"Content is close to limit ({char_count}/{LINKEDIN_MAX_POST_LENGTH})")
    
    # Check hashtag limit
    if len(hashtags) > LINKEDIN_MAX_HASHTAGS:
        issues.append(f"Too many hashtags ({len(hashtags)} > {LINKEDIN_MAX_HASHTAGS})")
    elif len(hashtags) > LINKEDIN_MAX_HASHTAGS - 2:
        warnings.append(f"Close to hashtag limit ({len(hashtags)}/{LINKEDIN_MAX_HASHTAGS})")
    
    # Check for very long paragraphs
    paragraphs = content.split('\n\n')
    for i, p in enumerate(paragraphs):
        if len(p) > 500:
            warnings.append(f"Paragraph {i+1} is very long ({len(p)} chars)")
    
    return {
        "valid": len(issues) == 0,
        "character_count": char_count,
        "word_count": word_count,
        "hashtag_count": len(hashtags),
        "paragraph_count": len(paragraphs),
        "reading_time_seconds": estimate_reading_time(content),
        "issues": issues,
        "warnings": warnings,
    }


def format_post_for_display(
    hook: str,
    body: str,
    cta: str,
    hashtags: list[str] | None = None,
) -> str:
    """Format post components into final display format."""
    parts = [hook, "", body, "", cta]
    
    if hashtags:
        parts.append("")
        parts.append(" ".join(f"#{h}" for h in hashtags))
    
    return "\n".join(parts)


def sanitize_for_json(obj: Any) -> Any:
    """Sanitize object for JSON serialization."""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        return str(obj)


def parse_json_safely(text: str) -> dict | None:
    """Parse JSON from text, handling common issues."""
    import json
    
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code block
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON object in text
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    logger.warning(f"Failed to parse JSON from: {truncate_text(text, 200)}")
    return None
