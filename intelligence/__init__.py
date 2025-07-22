"""
Intelligence and AI functionality for Emily.Tools.

This package contains AI extraction, intelligent search, natural query
processing, and smart suggestions.
"""

from .ai_extraction import AIExtractor, EntityMatcher, ContentEnhancer
from .search import IntelligentSearchEngine
from .search_mcp import IntelligentSearchMCPTools
from .natural_query import NaturalQueryProcessor
from .smart_suggestions import SmartSuggestionsEngine

__all__ = [
    'AIExtractor',
    'EntityMatcher', 
    'ContentEnhancer',
    'IntelligentSearchEngine',
    'IntelligentSearchMCPTools',
    'NaturalQueryProcessor',
    'SmartSuggestionsEngine'
] 