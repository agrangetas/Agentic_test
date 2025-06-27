"""
Classes de base pour tous les agents.

Définit l'interface commune et les fonctionnalités partagées entre agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import logging
from enum import Enum
from loguru import logger


class AgentState(Enum):
    """États possibles d'un agent."""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentResult:
    """Résultat standardisé d'un agent."""
    agent_name: str
    success: bool
    data: Dict[str, Any]
    confidence_score: float
    execution_time: float
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        """Validation post-initialisation."""
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("confidence_score must be between 0.0 and 1.0")
        if self.execution_time < 0:
            raise ValueError("execution_time must be positive")


class BaseAgent(ABC):
    """Classe de base pour tous les agents."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.state = AgentState.IDLE
        self.memory: Dict[str, Any] = {}
        self.tools: List[Any] = []
        self.llm_client: Optional[Any] = None
        
        # Configuration du logging spécifique à l'agent
        try:
            from orchestrator.logging_config import get_agent_logger
            self.logger = get_agent_logger(name)
        except ImportError:
            self.logger = logger.bind(agent_name=name)
        
        self.logger.info("Agent initialized", extra={
            "agent_name": name,
            "config_keys": list(config.keys()) if config else [],
            "state": self.state.value,
            "event_type": "agent_init"
        })
        
    @abstractmethod
    async def execute(self, context: 'TaskContext') -> AgentResult:
        """Méthode principale d'exécution."""
        pass
    
    @abstractmethod
    def validate_input(self, context: 'TaskContext') -> bool:
        """Valide les données d'entrée."""
        pass
    
    async def pre_execute(self, context: 'TaskContext'):
        """Préparation avant exécution."""
        self.state = AgentState.PROCESSING
        self.logger.info("Starting agent execution", extra={
            "agent_name": self.name,
            "session_id": context.session_id,
            "enterprise_name": context.enterprise_name,
            "current_depth": context.current_depth,
            "state": self.state.value,
            "event_type": "agent_execution_start"
        })
    
    async def post_execute(self, result: AgentResult, context: 'TaskContext'):
        """Nettoyage après exécution."""
        self.state = AgentState.COMPLETED if result.success else AgentState.ERROR
        
        # Mise à jour du contexte
        context.collected_data[self.name] = result.data
        context.metrics[f"{self.name}_confidence"] = result.confidence_score
        context.metrics[f"{self.name}_execution_time"] = result.execution_time
        
        # Logging détaillé
        self.logger.info("Agent execution completed", extra={
            "agent_name": self.name,
            "session_id": context.session_id,
            "success": result.success,
            "confidence_score": result.confidence_score,
            "execution_time": result.execution_time,
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
            "state": self.state.value,
            "event_type": "agent_execution_completed"
        })
        
        if result.errors:
            self.logger.warning("Agent execution had errors", extra={
                "agent_name": self.name,
                "session_id": context.session_id,
                "errors": result.errors,
                "event_type": "agent_execution_errors"
            })


class DataValidationMixin:
    """Mixin pour validation des données."""
    
    def validate_data_consistency(self, data: Dict[str, Any]) -> List[str]:
        """Valide la cohérence des données."""
        errors = []
        
        # Validation des champs obligatoires
        required_fields = getattr(self, 'REQUIRED_FIELDS', [])
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validation des types
        field_types = getattr(self, 'FIELD_TYPES', {})
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                errors.append(f"Invalid type for {field}: expected {expected_type}, got {type(data[field])}")
        
        return errors


class CacheableMixin:
    """Mixin pour gestion du cache."""
    
    def get_cache_key(self, context: 'TaskContext') -> str:
        """Génère une clé de cache."""
        return f"{self.name}:{context.enterprise_name}:{hash(str(context.config))}"
    
    async def get_cached_result(self, context: 'TaskContext') -> Optional[AgentResult]:
        """Récupère un résultat depuis le cache."""
        if not context.cache:
            return None
            
        cache_key = self.get_cache_key(context)
        return await context.cache.get('agent_result', cache_key)
    
    async def cache_result(self, result: AgentResult, context: 'TaskContext'):
        """Met en cache un résultat."""
        if not context.cache:
            return
            
        cache_key = self.get_cache_key(context)
        ttl = self.config.get('cache_ttl', 3600)
        await context.cache.set('agent_result', cache_key, result, ttl)


# Classes d'agents mixtes pour faciliter l'héritage
class CacheableAgent(BaseAgent, CacheableMixin):
    """Agent avec capacités de cache."""
    pass


class ValidatedAgent(BaseAgent, DataValidationMixin):
    """Agent avec validation de données."""
    pass


class FullFeaturedAgent(BaseAgent, DataValidationMixin, CacheableMixin):
    """Agent avec toutes les fonctionnalités."""
    pass 