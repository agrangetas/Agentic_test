"""
Routeur de modèles LLM avec fallbacks automatiques.

Pour l'instant, version simplifiée. La version complète avec
multiple providers sera implémentée dans la Phase 3.
"""

from typing import Dict, Any, Optional
from loguru import logger


class ModelRouter:
    """Routeur de modèles LLM simplifié."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logger.bind(component="model_router")
        
        self.logger.info("ModelRouter initialized", extra={
            "config_loaded": bool(config),
            "default_model": self.config.get("default_model", "gpt-4o"),
            "mode": "simple_without_providers",
            "event_type": "model_router_init"
        })
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut."""
        return {
            "default_model": "gpt-4o",
            "fallback_model": "gpt-3.5-turbo",
            "providers": ["openai"],
            "per_task": {
                "normalize_name": {"model": "gpt-3.5-turbo"},
                "extract_site_info": {"model": "gpt-3.5-turbo"},
                "parse_inpi_docs": {"model": "gpt-4-turbo"},
                "ner_extraction": {"model": "gpt-4o"},
                "validate_consistency": {"model": "gpt-4-turbo"},
                "summarization": {"model": "gpt-4o"},
                "conflict_resolution": {"model": "gpt-4-turbo"},
                "reasoning": {"model": "gpt-4o"},
                "link_analysis": {"model": "gpt-4-turbo"}
            }
        }
    
    def get_model_for_task(self, task_name: str) -> Dict[str, Any]:
        """Retourne la configuration de modèle pour une tâche."""
        self.logger.debug("Getting model for task", extra={
            "task_name": task_name,
            "function": "get_model_for_task"
        })
        
        # Configuration spécifique à la tâche
        task_config = self.config.get("per_task", {}).get(task_name, {})
        
        # Configuration par défaut
        default_config = {
            "provider": "openai",
            "model": task_config.get("model", self.config.get("default_model", "gpt-4o")),
            "fallback_model": self.config.get("fallback_model", "gpt-3.5-turbo"),
            "temperature": task_config.get("temperature", 0.1),
            "max_tokens": task_config.get("max_tokens", 2000)
        }
        
        self.logger.debug("Model configuration selected", extra={
            "task_name": task_name,
            "model": default_config["model"],
            "provider": default_config["provider"],
            "function": "get_model_for_task"
        })
        
        return default_config
    
    def get_model_for_agent(self, agent_name: str) -> Dict[str, Any]:
        """Retourne la configuration de modèle pour un agent."""
        self.logger.debug("Getting model for agent", extra={
            "agent_name": agent_name,
            "function": "get_model_for_agent"
        })
        
        # Mapping agent -> tâche principale
        agent_task_mapping = {
            "normalization": "normalize_name",
            "identification": "extract_site_info",
            "validation": "validate_consistency",
            "webdata": "extract_site_info",
            "inpi": "parse_inpi_docs",
            "news": "ner_extraction",
            "capital": "link_analysis",
            "recursion": "reasoning",
            "synthese": "summarization"
        }
        
        task_name = agent_task_mapping.get(agent_name, "default")
        return self.get_model_for_task(task_name)
    
    async def call_model(self, model_config: Dict[str, Any], prompt: str, 
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Appelle un modèle LLM (version simplifiée)."""
        self.logger.debug("Calling model (simple mode)", extra={
            "model": model_config.get("model"),
            "provider": model_config.get("provider"),
            "prompt_length": len(prompt),
            "function": "call_model"
        })
        
        # Pour l'instant, simulation de réponse
        # TODO: Implémenter les vrais appels LLM dans la Phase 3
        
        fake_response = {
            "content": f"Fake response for model {model_config.get('model', 'unknown')}",
            "model_used": model_config.get("model"),
            "provider": model_config.get("provider"),
            "tokens_used": len(prompt.split()) * 2,  # Estimation
            "execution_time": 0.5,
            "mode": "fake_for_testing"
        }
        
        self.logger.debug("Model call completed (fake mode)", extra={
            "model": model_config.get("model"),
            "tokens_used": fake_response["tokens_used"],
            "execution_time": fake_response["execution_time"],
            "function": "call_model"
        })
        
        return fake_response
    
    def get_available_models(self) -> Dict[str, Any]:
        """Retourne la liste des modèles disponibles."""
        return {
            "openai": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-sonnet", "claude-3-haiku"],  # Futur
            "mistral": ["mistral-large", "mistral-medium"],      # Futur
            "current_provider": "openai",
            "mode": "simple_configuration"
        }


# Instance globale pour compatibilité
model_router = ModelRouter() 