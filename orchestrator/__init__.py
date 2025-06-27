"""
Orchestrateur maison pour l'agent d'investigation d'entreprises.

Ce module contient l'orchestrateur personnalisé qui gère l'exécution des agents,
la gestion des dépendances, le cache, et la coordination des tâches.
"""

__version__ = "0.1.0"
__author__ = "Agent Company Intelligence Team"

from .core import OrchestrationEngine, TaskContext, AgentTask
from .model_router import ModelRouter
from .cache_manager import CacheManager
from .queue_manager import QueueManager

__all__ = [
    "OrchestrationEngine",
    "TaskContext", 
    "AgentTask",
    "ModelRouter",
    "CacheManager",
    "QueueManager"
] 