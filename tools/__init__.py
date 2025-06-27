"""
Module des outils (tools) pour Agent Company.
"""

# Import des outils disponibles
try:
    from .tool_normalize_name import ToolNormalizeName
    from .tool_match_enterprise import ToolMatchEnterprise
    from .tool_ner_extraction import ToolNERExtraction
    from .tool_identify_website import ToolIdentifyWebsite
    from .tool_validate_consistency import ToolValidateConsistency
    from .tool_resolve_conflicts import ToolResolveConflicts
except ImportError as e:
    print(f"⚠️  Certains outils ne sont pas disponibles: {e}")

__all__ = [
    'ToolNormalizeName',
    'ToolMatchEnterprise', 
    'ToolNERExtraction',
    'ToolIdentifyWebsite',
    'ToolValidateConsistency',
    'ToolResolveConflicts'
] 