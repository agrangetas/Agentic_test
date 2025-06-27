#!/usr/bin/env python3
"""
Script de test simple du système Agent Company Intelligence.

Ce script peut être exécuté depuis Jupyter ou directement en Python
pour tester les composants principaux du système.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Ajout du répertoire parent au path pour les imports
sys.path.append('/app')

from orchestrator.logging_config import setup_logging, get_agent_logger, get_logging_manager
from orchestrator.cache_manager import CacheManager
from orchestrator.core import OrchestrationEngine, TaskContext
from agents.agent_normalization import AgentNormalization
from agents.agent_identification import AgentIdentification
from agents.agent_validation import AgentValidation


async def test_logging():
    """Test du système de logging."""
    print("🔧 Test du système de logging...")
    
    # Configuration du logging
    setup_logging()
    log_manager = get_logging_manager()
    
    # Test des logs généraux
    from loguru import logger
    logger.info("Test du système de logging depuis script", extra={
        "event_type": "script_test",
        "script": "test_system_simple"
    })
    
    # Test des logs par agent
    agent_logger = get_agent_logger("test_agent")
    agent_logger.info("Test de log spécifique à un agent", extra={
        "function": "test_logging",
        "test_data": {"script": "test_system_simple"}
    })
    
    # Statistiques des logs
    log_stats = log_manager.get_log_stats()
    print(f"   📊 Statistiques: {log_stats['total_log_files']} fichiers, {log_stats['total_size_mb']} MB")
    
    return log_manager


async def test_cache():
    """Test du cache Redis."""
    print("💾 Test du cache Redis...")
    
    # Initialisation du cache
    cache_manager = CacheManager(
        redis_url=os.getenv('REDIS_URL', 'redis://redis:6379/1'),
        config_path="/app/config/cache_policy.yaml"
    )
    
    # Connexion
    await cache_manager.connect()
    
    # Test de cache
    test_key = "script_test_key"
    test_data = {"message": "Hello from test script!", "timestamp": time.time()}
    
    # Set
    await cache_manager.set("test", test_key, test_data, ttl=300)
    
    # Get
    cached_data = await cache_manager.get("test", test_key)
    
    # Statistiques
    cache_stats = await cache_manager.get_stats()
    print(f"   📊 Statistiques: {cache_stats['hits']} hits, {cache_stats['misses']} misses")
    
    return cache_manager


async def test_agents(cache_manager):
    """Test des agents."""
    print("🤖 Test des agents...")
    
    # Configuration des agents
    agent_config = {
        "cache_ttl": 3600,
        "test_mode": True
    }
    
    # Création du contexte de test
    from uuid import uuid4
    context = TaskContext(
        session_id=str(uuid4()),
        enterprise_name="Test Company SARL",
        current_depth=0,
        max_depth=2,
        collected_data={},
        graph=None,
        cache=cache_manager,
        config={"test_mode": True},
        errors=[],
        metrics={}
    )
    
    results = {}
    
    # Test Agent Normalization
    agent_norm = AgentNormalization(agent_config)
    result_norm = await agent_norm.execute(context)
    results['normalization'] = result_norm
    print(f"   🔄 Normalization: {'✅' if result_norm.success else '❌'} (confiance: {result_norm.confidence_score:.2f})")
    
    # Test Agent Identification
    agent_id = AgentIdentification(agent_config)
    result_id = await agent_id.execute(context)
    results['identification'] = result_id
    print(f"   🔍 Identification: {'✅' if result_id.success else '❌'} (confiance: {result_id.confidence_score:.2f})")
    
    # Test Agent Validation
    agent_val = AgentValidation(agent_config)
    result_val = await agent_val.execute(context)
    results['validation'] = result_val
    print(f"   ✅ Validation: {'✅' if result_val.success else '❌'} (confiance: {result_val.confidence_score:.2f})")
    
    return results


async def test_orchestrator():
    """Test de l'orchestrateur."""
    print("🎯 Test de l'orchestrateur...")
    
    # Configuration de l'orchestrateur
    orchestrator_config = {
        'max_concurrent_tasks': 3,
        'session_timeout_minutes': 10,
        'models': {'default_model': 'gpt-4o'},
        'recursion': {'max_depth': 2}
    }
    
    orchestrator = OrchestrationEngine(orchestrator_config)
    
    # Test d'une session complète
    session_result = await orchestrator.execute_session(
        enterprise_name="LVMH Group",
        session_config={
            'max_depth': 1,
            'enable_recursion': False,
            'test_mode': True
        }
    )
    
    print(f"   🚀 Session: {session_result.get('status')} ({session_result.get('execution_time', 0):.3f}s)")
    
    return session_result


async def main():
    """Fonction principale du test."""
    print("=" * 60)
    print("🧠 TEST DU SYSTÈME AGENT COMPANY INTELLIGENCE")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Test du logging
        log_manager = await test_logging()
        
        # Test du cache
        cache_manager = await test_cache()
        
        # Test des agents
        agent_results = await test_agents(cache_manager)
        
        # Test de l'orchestrateur
        orchestrator_result = await test_orchestrator()
        
        # Résumé
        execution_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        
        print(f"⏱️  Temps d'exécution total: {execution_time:.3f}s")
        
        print(f"\n🤖 Agents testés:")
        for agent_name, result in agent_results.items():
            status = "✅" if result.success else "❌"
            print(f"   {status} {agent_name}: {result.confidence_score:.2f} confiance")
        
        print(f"\n🎯 Orchestrateur: {orchestrator_result.get('status')}")
        
        # Statistiques finales
        final_log_stats = log_manager.get_log_stats()
        final_cache_stats = await cache_manager.get_stats()
        
        print(f"\n📊 Statistiques finales:")
        print(f"   📝 Logs: {final_log_stats['total_log_files']} fichiers")
        print(f"   💾 Cache: {final_cache_stats['hit_rate']:.1%} hit rate")
        
        # Nettoyage
        await cache_manager.disconnect()
        
        print(f"\n🎉 Tous les tests sont terminés avec succès !")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 