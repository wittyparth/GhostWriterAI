"""
LLM Package - Google Gemini API integration.

Exports:
    GeminiClient: Main client for Gemini API
    get_gemini_client: Factory function for singleton client
"""

from src.llm.gemini import GeminiClient, get_gemini_client

__all__ = ["GeminiClient", "get_gemini_client"]
