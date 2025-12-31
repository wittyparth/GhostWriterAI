"""
Unit tests for utility functions.
"""

import pytest
from src.utils.helpers import (
    truncate_text,
    count_words,
    count_characters,
    estimate_reading_time,
    extract_hashtags,
    validate_linkedin_content,
    format_post_for_display,
    parse_json_safely,
)


class TestTextUtilities:
    """Tests for text utility functions."""
    
    def test_truncate_text_short(self):
        """Test truncation of short text."""
        text = "Hello world"
        result = truncate_text(text, max_length=100)
        assert result == text
    
    def test_truncate_text_long(self):
        """Test truncation of long text."""
        text = "This is a very long text that should be truncated"
        result = truncate_text(text, max_length=20)
        assert len(result) == 20
        assert result.endswith("...")
    
    def test_count_words(self):
        """Test word counting."""
        assert count_words("Hello world") == 2
        assert count_words("One") == 1
        assert count_words("") == 0  # Empty string has 0 words
    
    def test_count_characters(self):
        """Test character counting (excluding whitespace)."""
        assert count_characters("Hello world") == 10
        assert count_characters("a b c") == 3
    
    def test_estimate_reading_time(self):
        """Test reading time estimation."""
        # 200 words = 60 seconds at 200 WPM
        text = " ".join(["word"] * 200)
        result = estimate_reading_time(text, words_per_minute=200)
        assert result == 60
    
    def test_extract_hashtags(self):
        """Test hashtag extraction."""
        text = "Great post! #startup #founder #growth"
        result = extract_hashtags(text)
        assert result == ["startup", "founder", "growth"]
    
    def test_extract_hashtags_none(self):
        """Test hashtag extraction with no hashtags."""
        text = "No hashtags here"
        result = extract_hashtags(text)
        assert result == []


class TestLinkedInValidation:
    """Tests for LinkedIn content validation."""
    
    def test_valid_content(self):
        """Test validation of valid content."""
        content = "This is a valid LinkedIn post with reasonable length."
        result = validate_linkedin_content(content)
        
        assert result["valid"] is True
        assert result["issues"] == []
    
    def test_content_too_long(self):
        """Test validation catches content that's too long."""
        content = "x" * 4000  # Over limit
        result = validate_linkedin_content(content)
        
        assert result["valid"] is False
        assert len(result["issues"]) > 0


class TestPostFormatting:
    """Tests for post formatting."""
    
    def test_format_post_basic(self):
        """Test basic post formatting."""
        result = format_post_for_display(
            hook="This is the hook",
            body="This is the body",
            cta="What do you think?",
        )
        
        assert "This is the hook" in result
        assert "This is the body" in result
        assert "What do you think?" in result
    
    def test_format_post_with_hashtags(self):
        """Test post formatting with hashtags."""
        result = format_post_for_display(
            hook="Hook",
            body="Body",
            cta="CTA",
            hashtags=["startup", "growth"],
        )
        
        assert "#startup" in result
        assert "#growth" in result


class TestJSONParsing:
    """Tests for JSON parsing."""
    
    def test_parse_valid_json(self):
        """Test parsing valid JSON."""
        text = '{"key": "value"}'
        result = parse_json_safely(text)
        assert result == {"key": "value"}
    
    def test_parse_json_in_markdown(self):
        """Test parsing JSON from markdown code block."""
        text = 'Here is some JSON:\n```json\n{"key": "value"}\n```'
        result = parse_json_safely(text)
        assert result == {"key": "value"}
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON returns None."""
        text = "Not JSON at all"
        result = parse_json_safely(text)
        assert result is None
