"""
Module core de l'orchestrateur - Classes principales et moteur d'orchestration.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import time
import uuid
from loguru import logger
from .logging_config import get_logging_manager, get_agent_logger


class ExecutionState(Enum):
    """États d'exécution des tâches."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priorités des tâches pour l'ordonnancement."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskContext:
    """Context partagé entre tous les agents durant une session."""
    session_id: str
    enterprise_name: str
    current_depth: int
    max_depth: int
    collected_data: Dict[str, Any] = field(default_factory=dict)
    graph: Optional[Any] = None
    cache: Optional[Any] = None
    config: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    api_calls_count: int = 0
    
    def add_error(self, error: str) -> None:
        """Ajoute une erreur au contexte."""
        self.errors.append(error)
        logger.error(f"Session {self.session_id}: {error}", extra={
            "session_id": self.session_id,
            "error_count": len(self.errors),
            "event_type": "session_error"
        })
    
    def add_warning(self, warning: str) -> None:
        """Ajoute un avertissement au contexte."""
        self.warnings.append(warning)
        logger.warning(f"Session {self.session_id}: {warning}", extra={
            "session_id": self.session_id,
            "warning_count": len(self.warnings),
            "event_type": "session_warning"
        })
    
    def increment_api_calls(self) -> None:
        """Incrémente le compteur d'appels API."""
        self.api_calls_count += 1
        logger.debug(f"API call #{self.api_calls_count} for session {self.session_id}", extra={
            "session_id": self.session_id,
            "api_calls_count": self.api_calls_count,
            "event_type": "api_call_increment"
        })
    
    def get_elapsed_time(self) -> float:
        """Retourne le temps écoulé depuis le début de la session."""
        return time.time() - self.start_time


class AgentTask(ABC):
    """Interface pour toutes les tâches d'agents."""
    
    def __init__(self, task_id: str, agent_name: str, priority: TaskPriority = TaskPriority.MEDIUM):
        self.task_id = task_id
        self.agent_name = agent_name
        self.priority = priority
        self.state = ExecutionState.PENDING
        self.dependencies: List[str] = []
        self.result: Optional[Any] = None
        self.error: Optional[Exception] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self._retry_count = 0
    
    @abstractmethod
    async def execute(self, context: TaskContext) -> Any:
        """Exécute la tâche de manière asynchrone."""
        pass
    
    def can_run(self, completed_tasks: List[str]) -> bool:
        """Vérifie si la tâche peut être exécutée."""
        return all(dep in completed_tasks for dep in self.dependencies)


class OrchestrationEngine:
    """Moteur principal d'orchestration des agents."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []
        self.max_concurrent_tasks = config.get('max_concurrent_tasks', 5)
        self.session_timeout = config.get('session_timeout_minutes', 30) * 60
        
        # Configuration du logging
        self.log_manager = get_logging_manager()
        self.logger = logger.bind(component="orchestrator")
        
        self.logger.info("OrchestrationEngine initialized", extra={
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "session_timeout_minutes": config.get('session_timeout_minutes', 30),
            "config_keys": list(config.keys()),
            "event_type": "orchestrator_init"
        })
    
    @property
    def session_timeout_minutes(self) -> int:
        """Retourne le timeout de session en minutes (pour compatibilité)."""
        return int(self.session_timeout / 60)
    
    async def execute_session(self, enterprise_name: str, session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Point d'entrée principal pour une session d'exploration."""
        session_id = str(uuid.uuid4())
        session_start_time = time.time()
        
        self.logger.info("Starting exploration session", extra={
            "session_id": session_id,
            "enterprise_name": enterprise_name,
            "session_config": session_config,
            "event_type": "session_start"
        })
        
        try:
            # Création du contexte
            context = await self._create_context(session_id, enterprise_name, session_config)
            
            self.logger.debug("Session context created", extra={
                "session_id": session_id,
                "max_depth": context.max_depth,
                "current_depth": context.current_depth,
                "event_type": "context_created"
            })
            
            # Pour l'instant, retour simple (pipeline complet à implémenter)
            execution_time = time.time() - session_start_time
            
            self.logger.info("Session initialized successfully", extra={
                "session_id": session_id,
                "execution_time": execution_time,
                "event_type": "session_initialized"
            })
            
            return {
                "session_id": session_id,
                "enterprise_name": enterprise_name,
                "status": "initialized",
                "message": "Session created successfully",
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - session_start_time
            self.logger.error("Session initialization failed", extra={
                "session_id": session_id,
                "enterprise_name": enterprise_name,
                "error": str(e),
                "execution_time": execution_time,
                "event_type": "session_error"
            })
            raise
    
    async def _create_context(self, session_id: str, enterprise_name: str, session_config: Dict[str, Any]) -> TaskContext:
        """Crée le contexte de session."""
        self.logger.debug("Creating session context", extra={
            "session_id": session_id,
            "enterprise_name": enterprise_name,
            "function": "_create_context"
        })
        
        context = TaskContext(
            session_id=session_id,
            enterprise_name=enterprise_name,
            current_depth=0,
            max_depth=session_config.get('max_depth', 3),
            config=session_config
        )
        
        self.logger.debug("Session context created successfully", extra={
            "session_id": session_id,
            "max_depth": context.max_depth,
            "function": "_create_context"
        })
        
        return context 