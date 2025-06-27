#!/usr/bin/env python3
"""
Script principal de l'agent d'investigation d'entreprises.

Initialise le système de logging avancé et lance l'orchestrateur.
"""

import asyncio
import os
import sys
from pathlib import Path
import yaml
from typing import Dict, Any

# Ajout du répertoire du projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestrator.logging_config import setup_logging, get_logging_manager
from orchestrator.core import OrchestrationEngine
from orchestrator.cache_manager import CacheManager
from loguru import logger


async def load_config() -> Dict[str, Any]:
    """Charge la configuration depuis les fichiers YAML."""
    config = {}
    
    # Configuration du logging
    logging_config_path = project_root / "config" / "logging_config.yaml"
    if logging_config_path.exists():
        with open(logging_config_path, 'r', encoding='utf-8') as f:
            config['logging'] = yaml.safe_load(f)
    
    # Configuration des modèles
    models_config_path = project_root / "config" / "models.yaml"
    if models_config_path.exists():
        with open(models_config_path, 'r', encoding='utf-8') as f:
            config['models'] = yaml.safe_load(f)
    
    # Configuration du cache
    cache_config_path = project_root / "config" / "cache_policy.yaml"
    if cache_config_path.exists():
        with open(cache_config_path, 'r', encoding='utf-8') as f:
            config['cache'] = yaml.safe_load(f)
    
    # Configuration de la récursivité
    recursion_config_path = project_root / "config" / "recursion_criteria.yaml"
    if recursion_config_path.exists():
        with open(recursion_config_path, 'r', encoding='utf-8') as f:
            config['recursion'] = yaml.safe_load(f)
    
    return config


async def initialize_system(config: Dict[str, Any]) -> tuple:
    """Initialise tous les composants du système."""
    
    # 1. Configuration du logging
    setup_logging(config.get('logging'))
    log_manager = get_logging_manager()
    
    logger.info("System initialization started", extra={
        "config_sections": list(config.keys()),
        "event_type": "system_init_start"
    })
    
    # 2. Initialisation du cache manager
    cache_manager = CacheManager(
        redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        config_path="config/cache_policy.yaml"
    )
    
    try:
        await cache_manager.connect()
        logger.info("Cache manager initialized successfully", extra={
            "redis_url": cache_manager.redis_url,
            "event_type": "cache_init_success"
        })
    except Exception as e:
        logger.error("Failed to initialize cache manager", extra={
            "error": str(e),
            "event_type": "cache_init_error"
        })
        raise
    
    # 3. Initialisation de l'orchestrateur
    orchestrator_config = {
        'max_concurrent_tasks': config.get('orchestrator', {}).get('max_concurrent_tasks', 5),
        'session_timeout_minutes': config.get('orchestrator', {}).get('session_timeout_minutes', 30),
        'models': config.get('models', {}),
        'recursion': config.get('recursion', {})
    }
    
    orchestrator = OrchestrationEngine(orchestrator_config)
    
    logger.info("System initialization completed successfully", extra={
        "components_initialized": ["logging", "cache", "orchestrator"],
        "event_type": "system_init_success"
    })
    
    return orchestrator, cache_manager, log_manager


async def run_test_session(orchestrator: OrchestrationEngine):
    """Lance une session de test."""
    logger.info("Starting test session", extra={
        "test_company": "LVMH",
        "event_type": "test_session_start"
    })
    
    try:
        result = await orchestrator.execute_session(
            enterprise_name="LVMH",
            session_config={
                'max_depth': 2,
                'enable_recursion': False,
                'test_mode': True
            }
        )
        
        logger.info("Test session completed successfully", extra={
            "session_id": result.get('session_id'),
            "execution_time": result.get('execution_time'),
            "status": result.get('status'),
            "event_type": "test_session_success"
        })
        
        return result
        
    except Exception as e:
        logger.error("Test session failed", extra={
            "error": str(e),
            "error_type": type(e).__name__,
            "event_type": "test_session_error"
        })
        raise


async def cleanup_system(cache_manager: CacheManager, log_manager):
    """Nettoie les ressources système."""
    logger.info("Starting system cleanup", extra={
        "event_type": "system_cleanup_start"
    })
    
    try:
        # Fermeture du cache
        if cache_manager and cache_manager.redis:
            await cache_manager.disconnect()
            logger.debug("Cache manager disconnected")
        
        # Statistiques des logs
        if log_manager:
            log_stats = log_manager.get_log_stats()
            logger.info("Log statistics", extra={
                "log_stats": log_stats,
                "event_type": "log_stats"
            })
        
        logger.info("System cleanup completed", extra={
            "event_type": "system_cleanup_success"
        })
        
    except Exception as e:
        logger.error("Error during system cleanup", extra={
            "error": str(e),
            "event_type": "system_cleanup_error"
        })


def print_banner():
    """Affiche la bannière de démarrage."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🧠 Agent d'Investigation d'Entreprises               ║
    ║                                                              ║
    ║        📊 Système de logging avancé activé                  ║
    ║        📁 Logs par agent avec rotation quotidienne          ║
    ║        🔄 Cache Redis avec policies configurables           ║
    ║        🎯 Orchestrateur custom avec gestion d'erreurs       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


async def main():
    """Fonction principale."""
    print_banner()
    
    orchestrator = None
    cache_manager = None
    log_manager = None
    
    try:
        # Chargement de la configuration
        config = await load_config()
        
        # Initialisation du système
        orchestrator, cache_manager, log_manager = await initialize_system(config)
        
        # Session de test
        test_result = await run_test_session(orchestrator)
        
        print(f"\n✅ Session de test réussie!")
        print(f"   Session ID: {test_result.get('session_id')}")
        print(f"   Temps d'exécution: {test_result.get('execution_time', 0):.3f}s")
        print(f"   Statut: {test_result.get('status')}")
        
        # Affichage des statistiques de logs
        if log_manager:
            log_stats = log_manager.get_log_stats()
            print(f"\n📊 Statistiques des logs:")
            print(f"   Répertoire: {log_stats['logs_directory']}")
            print(f"   Fichiers de log: {log_stats['total_log_files']}")
            print(f"   Taille totale: {log_stats['total_size_mb']} MB")
            print(f"   Agents avec logs: {', '.join(log_stats['agents_with_logs'])}")
        
        # Affichage des statistiques de cache
        if cache_manager:
            cache_stats = await cache_manager.get_stats()
            print(f"\n💾 Statistiques du cache:")
            print(f"   Hits: {cache_stats['hits']}")
            print(f"   Misses: {cache_stats['misses']}")
            print(f"   Hit rate: {cache_stats['hit_rate']:.1%}")
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user", extra={
            "event_type": "user_interrupt"
        })
        
    except Exception as e:
        logger.error("Application failed", extra={
            "error": str(e),
            "error_type": type(e).__name__,
            "event_type": "application_error"
        })
        sys.exit(1)
        
    finally:
        # Nettoyage
        await cleanup_system(cache_manager, log_manager)
        
        print(f"\n📁 Logs disponibles dans: {project_root}/logs/")
        print(f"   - logs/app_YYYY-MM-DD.log (logs généraux)")
        print(f"   - logs/agents/AGENT_NAME_YYYY-MM-DD.log (logs par agent)")
        print(f"\n🔍 Utilisez 'tail -f logs/app_*.log' pour suivre les logs en temps réel")


if __name__ == "__main__":
    asyncio.run(main()) 