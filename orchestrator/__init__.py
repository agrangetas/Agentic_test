"""
Orchestrateur maison pour l'agent d'investigation d'entreprises.

Ce module contient l'orchestrateur personnalisé qui gère l'exécution des agents,
la gestion des dépendances, le cache, et la coordination des tâches.
"""

__version__ = "0.1.0"
__author__ = "Agent Company Intelligence Team"

from .core import OrchestrationEngine, TaskContext, AgentTask
from .cache_manager import CacheManager
from .logging_config import LoggingManager, get_agent_logger, setup_logging
from .model_router import ModelRouter
from .queue_manager import SimpleQueueManager

__all__ = [
    "OrchestrationEngine",
    "TaskContext", 
    "AgentTask",
    "CacheManager",
    "LoggingManager",
    "get_agent_logger",
    "setup_logging",
    "ModelRouter",
    "SimpleQueueManager"
] 