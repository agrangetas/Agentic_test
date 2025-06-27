"""
Configuration avancée du système de logging.

Gère les logs par agent avec rotation quotidienne, formatage détaillé
et niveaux configurables.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
import json
from datetime import datetime


class LoggingManager:
    """Gestionnaire centralisé des logs avec configuration avancée."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logs_dir = Path(self.config.get('logs_directory', 'logs'))
        self.logs_dir.mkdir(exist_ok=True)
        
        # Supprime la configuration par défaut de loguru
        logger.remove()
        
        # Configure les handlers
        self._setup_console_logging()
        self._setup_file_logging()
        self._setup_agent_logging()
        
        logger.info("LoggingManager initialized", extra={
            "logs_directory": str(self.logs_dir),
            "config": self.config
        })
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut du logging."""
        return {
            "logs_directory": "logs",
            "console": {
                "enabled": True,
                "level": "INFO",
                "format": "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
            },
            "file": {
                "enabled": True,
                "level": "DEBUG",
                "rotation": "1 day",
                "retention": "30 days",
                "compression": "gz",
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {process}:{thread} | {message}"
            },
            "agents": {
                "enabled": True,
                "level": "DEBUG",
                "rotation": "1 day",
                "retention": "30 days",
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {function}:{line} | {extra[session_id]:-} | {extra[execution_time]:-} | {message}"
            },
            "structured": {
                "enabled": True,
                "include_extra": True
            }
        }
    
    def _setup_console_logging(self):
        """Configure le logging console."""
        console_config = self.config.get('console', {})
        
        if console_config.get('enabled', True):
            logger.add(
                sys.stdout,
                level=console_config.get('level', 'INFO'),
                format=console_config.get('format'),
                colorize=True,
                backtrace=True,
                diagnose=True
            )
    
    def _setup_file_logging(self):
        """Configure le logging fichier principal."""
        file_config = self.config.get('file', {})
        
        if file_config.get('enabled', True):
            log_file = self.logs_dir / "app_{time:YYYY-MM-DD}.log"
            
            logger.add(
                str(log_file),
                level=file_config.get('level', 'DEBUG'),
                format=file_config.get('format'),
                rotation=file_config.get('rotation', '1 day'),
                retention=file_config.get('retention', '30 days'),
                compression=file_config.get('compression', 'gz'),
                backtrace=True,
                diagnose=True,
                enqueue=True  # Thread-safe
            )
    
    def _setup_agent_logging(self):
        """Configure le logging par agent."""
        agents_dir = self.logs_dir / "agents"
        agents_dir.mkdir(exist_ok=True)
        self.agent_handlers = {}
    
    def get_agent_logger(self, agent_name: str, session_id: Optional[str] = None):
        """Retourne un logger configuré pour un agent spécifique."""
        if agent_name not in self.agent_handlers:
            self._create_agent_handler(agent_name)
        
        return logger.bind(agent_name=agent_name, session_id=session_id or "unknown")
    
    def _create_agent_handler(self, agent_name: str):
        """Crée un handler de log spécifique pour un agent."""
        agents_dir = self.logs_dir / "agents"
        log_file = agents_dir / f"{agent_name}_{{time:YYYY-MM-DD}}.log"
        
        handler_id = logger.add(
            str(log_file),
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {function}:{line} | {extra[session_id]:-} | {message}",
            rotation="1 day",
            retention="30 days",
            compression='gz',
            filter=lambda record: record.get("extra", {}).get("agent_name") == agent_name
        )
        
        self.agent_handlers[agent_name] = handler_id
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur les logs."""
        stats = {
            "logs_directory": str(self.logs_dir),
            "total_log_files": 0,
            "total_size_mb": 0,
            "agents_with_logs": [],
            "oldest_log": None,
            "newest_log": None
        }
        
        log_files = list(self.logs_dir.rglob("*.log*"))
        stats["total_log_files"] = len(log_files)
        
        total_size = 0
        oldest_time = None
        newest_time = None
        
        agents_dir = self.logs_dir / "agents"
        if agents_dir.exists():
            agent_files = list(agents_dir.glob("*.log*"))
            agent_names = set()
            for agent_file in agent_files:
                agent_name = agent_file.name.split('_')[0]
                agent_names.add(agent_name)
            stats["agents_with_logs"] = sorted(list(agent_names))
        
        for log_file in log_files:
            try:
                file_stat = log_file.stat()
                total_size += file_stat.st_size
                
                if oldest_time is None or file_stat.st_mtime < oldest_time:
                    oldest_time = file_stat.st_mtime
                    stats["oldest_log"] = str(log_file)
                
                if newest_time is None or file_stat.st_mtime > newest_time:
                    newest_time = file_stat.st_mtime
                    stats["newest_log"] = str(log_file)
                    
            except Exception:
                continue
        
        stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        return stats
    
    def log_function_entry(self, logger_instance, func_name: str, **kwargs):
        """Log l'entrée dans une fonction avec paramètres."""
        logger_instance.debug(
            f"→ Entering {func_name}",
            extra={
                "function": func_name,
                "parameters": kwargs,
                "event_type": "function_entry"
            }
        )
    
    def log_function_exit(self, logger_instance, func_name: str, execution_time: float, result_summary: str = ""):
        """Log la sortie d'une fonction avec temps d'exécution."""
        logger_instance.debug(
            f"← Exiting {func_name} ({execution_time:.3f}s) {result_summary}",
            extra={
                "function": func_name,
                "execution_time": execution_time,
                "result_summary": result_summary,
                "event_type": "function_exit"
            }
        )
    
    def log_performance_metric(self, logger_instance, metric_name: str, value: float, unit: str = ""):
        """Log une métrique de performance."""
        logger_instance.info(
            f"📊 {metric_name}: {value}{unit}",
            extra={
                "metric_name": metric_name,
                "metric_value": value,
                "metric_unit": unit,
                "event_type": "performance_metric"
            }
        )
    
    def log_data_quality(self, logger_instance, data_type: str, quality_score: float, details: Dict[str, Any]):
        """Log la qualité des données."""
        logger_instance.info(
            f"🔍 Data quality for {data_type}: {quality_score:.2f}",
            extra={
                "data_type": data_type,
                "quality_score": quality_score,
                "quality_details": details,
                "event_type": "data_quality"
            }
        )
    
    def log_cache_operation(self, logger_instance, operation: str, key: str, hit: bool, execution_time: float):
        """Log les opérations de cache."""
        status = "HIT" if hit else "MISS"
        logger_instance.debug(
            f"💾 Cache {operation} - {status} - {key} ({execution_time:.3f}s)",
            extra={
                "cache_operation": operation,
                "cache_key": key,
                "cache_hit": hit,
                "execution_time": execution_time,
                "event_type": "cache_operation"
            }
        )
    
    def log_api_call(self, logger_instance, api_name: str, endpoint: str, status_code: int, execution_time: float):
        """Log les appels d'API."""
        logger_instance.info(
            f"🌐 API {api_name} - {endpoint} - {status_code} ({execution_time:.3f}s)",
            extra={
                "api_name": api_name,
                "api_endpoint": endpoint,
                "status_code": status_code,
                "execution_time": execution_time,
                "event_type": "api_call"
            }
        )
    
    def log_error_with_context(self, logger_instance, error: Exception, context: Dict[str, Any]):
        """Log une erreur avec contexte détaillé."""
        logger_instance.error(
            f"❌ Error: {str(error)}",
            extra={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "error_context": context,
                "event_type": "error"
            }
        )
    
    def log_session_event(self, logger_instance, session_id: str, event: str, details: Dict[str, Any]):
        """Log un événement de session."""
        logger_instance.info(
            f"🎯 Session {session_id}: {event}",
            extra={
                "session_id": session_id,
                "session_event": event,
                "session_details": details,
                "event_type": "session_event"
            }
        )
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Nettoie les anciens fichiers de log."""
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        
        cleaned_count = 0
        for log_file in self.logs_dir.rglob("*.log*"):
            if log_file.stat().st_mtime < cutoff_date:
                try:
                    log_file.unlink()
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Could not delete old log file {log_file}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old log files")
    
    def setup_logging(self, config: Optional[Dict[str, Any]] = None):
        """Configure le système de logging (méthode d'instance)."""
        if config:
            self.config.update(config)
        
        # Reconfigure les handlers si nécessaire
        logger.info("Logging system reconfigured", extra={"config": self.config})
        return self
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur les logs."""
        stats = {
            "logs_directory": str(self.logs_dir),
            "total_log_files": 0,
            "total_size_mb": 0,
            "agents_with_logs": [],
            "oldest_log": None,
            "newest_log": None
        }
        
        log_files = list(self.logs_dir.rglob("*.log*"))
        stats["total_log_files"] = len(log_files)
        
        total_size = 0
        oldest_time = None
        newest_time = None
        
        agents_dir = self.logs_dir / "agents"
        if agents_dir.exists():
            agent_files = list(agents_dir.glob("*.log*"))
            agent_names = set()
            for agent_file in agent_files:
                agent_name = agent_file.name.split('_')[0]
                agent_names.add(agent_name)
            stats["agents_with_logs"] = sorted(list(agent_names))
        
        for log_file in log_files:
            try:
                file_stat = log_file.stat()
                total_size += file_stat.st_size
                
                if oldest_time is None or file_stat.st_mtime < oldest_time:
                    oldest_time = file_stat.st_mtime
                    stats["oldest_log"] = str(log_file)
                
                if newest_time is None or file_stat.st_mtime > newest_time:
                    newest_time = file_stat.st_mtime
                    stats["newest_log"] = str(log_file)
                    
            except Exception:
                continue
        
        stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        return stats


# Instance globale du gestionnaire de logs
_logging_manager = None


def get_logging_manager(config: Optional[Dict[str, Any]] = None) -> LoggingManager:
    """Retourne l'instance globale du gestionnaire de logs."""
    global _logging_manager
    
    if _logging_manager is None:
        _logging_manager = LoggingManager(config)
    
    return _logging_manager


def get_agent_logger(agent_name: str, session_id: Optional[str] = None):
    """Raccourci pour obtenir un logger d'agent."""
    return get_logging_manager().get_agent_logger(agent_name, session_id)


def setup_logging(config: Optional[Dict[str, Any]] = None):
    """Configure le système de logging global."""
    global _logging_manager
    _logging_manager = LoggingManager(config)
    logger.info("Logging system configured successfully")


# Fonctions utilitaires pour les logs
def log_function_entry(func_name: str, **kwargs):
    """Log l'entrée dans une fonction avec paramètres."""
    logger.debug(f"→ Entering {func_name}", extra={
        "function": func_name,
        "parameters": kwargs,
        "event_type": "function_entry"
    })


def log_function_exit(func_name: str, execution_time: float, result_summary: str = ""):
    """Log la sortie d'une fonction avec temps d'exécution."""
    logger.debug(f"← Exiting {func_name} ({execution_time:.3f}s) {result_summary}", extra={
        "function": func_name,
        "execution_time": execution_time,
        "result_summary": result_summary,
        "event_type": "function_exit"
    })


def log_performance_metric(metric_name: str, value: float, unit: str = ""):
    """Log une métrique de performance."""
    logger.info(f"📊 {metric_name}: {value}{unit}", extra={
        "metric_name": metric_name,
        "metric_value": value,
        "metric_unit": unit,
        "event_type": "performance_metric"
    })


def log_cache_operation(operation: str, key: str, hit: bool, execution_time: float):
    """Log les opérations de cache."""
    status = "HIT" if hit else "MISS"
    logger.debug(f"💾 Cache {operation} - {status} - {key} ({execution_time:.3f}s)", extra={
        "cache_operation": operation,
        "cache_key": key,
        "cache_hit": hit,
        "execution_time": execution_time,
        "event_type": "cache_operation"
    })


def log_session_event(session_id: str, event: str, details: Dict[str, Any]):
    """Log un événement de session."""
    logger.info(f"🎯 Session {session_id}: {event}", extra={
        "session_id": session_id,
        "session_event": event,
        "session_details": details,
        "event_type": "session_event"
    })


def get_log_stats() -> Dict[str, Any]:
    """Retourne des statistiques sur les logs."""
    return get_logging_manager().get_log_stats()


# Décorateur pour logger automatiquement les fonctions
def log_function(logger_instance=None):
    """Décorateur pour logger automatiquement l'entrée/sortie des fonctions."""
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            log_mgr = get_logging_manager()
            func_logger = logger_instance or logger
            
            log_mgr.log_function_entry(func_logger, func.__name__, **kwargs)
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                log_mgr.log_function_exit(func_logger, func.__name__, execution_time, "success")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                log_mgr.log_function_exit(func_logger, func.__name__, execution_time, f"error: {str(e)}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            log_mgr = get_logging_manager()
            func_logger = logger_instance or logger
            
            log_mgr.log_function_entry(func_logger, func.__name__, **kwargs)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                log_mgr.log_function_exit(func_logger, func.__name__, execution_time, "success")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                log_mgr.log_function_exit(func_logger, func.__name__, execution_time, f"error: {str(e)}")
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator 