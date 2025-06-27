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
        logger.error(f"Session {self.session_id}: {error}")
    
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
        logger.info(f"OrchestrationEngine initialized")
    
    async def execute_session(self, enterprise_name: str, session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Point d'entrée principal pour une session d'exploration."""
        session_id = str(uuid.uuid4())
        logger.info(f"Starting session {session_id} for: {enterprise_name}")
        
        # Création du contexte
        context = TaskContext(
            session_id=session_id,
            enterprise_name=enterprise_name,
            current_depth=0,
            max_depth=session_config.get('max_depth', 3),
            config=session_config
        )
        
        return {
            "session_id": session_id,
            "enterprise_name": enterprise_name,
            "status": "initialized",
            "message": "Session created successfully"
        } 