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
        self.logger = logging.getLogger(f"agent.{name}")
        self.memory: Dict[str, Any] = {}
        self.tools: List[Any] = []
        self.llm_client: Optional[Any] = None
        
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
        self.logger.info(f"Starting execution for {context.enterprise_name}")
    
    async def post_execute(self, result: AgentResult, context: 'TaskContext'):
        """Nettoyage après exécution."""
        self.state = AgentState.COMPLETED if result.success else AgentState.ERROR
        
        # Mise à jour du contexte
        context.collected_data[self.name] = result.data
        context.metrics[f"{self.name}_confidence"] = result.confidence_score
        context.metrics[f"{self.name}_execution_time"] = result.execution_time
        
        # Logging
        self.logger.info(f"Completed execution: success={result.success}, confidence={result.confidence_score}")


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