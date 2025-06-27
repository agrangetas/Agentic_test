#!/usr/bin/env python3
"""
Script de test simplifié pour le notebook (environnement Docker).
"""

import asyncio
import sys
import time
from uuid import uuid4

sys.path.append('/app')

print("🧪 TEST SYSTÈME SIMPLIFIÉ POUR NOTEBOOK")
print("=" * 50)

async def test_system_components():
    """Test rapide des composants principaux."""
    results = {}
    
    # Test 1: Imports
    print("\n1️⃣ Test des imports...")
    try:
        from orchestrator.logging_config import LoggingManager
        from orchestrator.cache_manager import CacheManager
        from agents.agent_normalization import AgentNormalization
        from agents.agent_identification import AgentIdentification
        from agents.agent_validation import AgentValidation
        print("   ✅ Tous les imports réussis")
        results['imports'] = True
    except Exception as e:
        print(f"   ❌ Erreur imports: {e}")
        results['imports'] = False
    
    # Test 2: Logging
    print("\n2️⃣ Test du logging...")
    try:
        logging_manager = LoggingManager()
        logging_manager.setup_logging()
        
        from loguru import logger
        logger.info("Test logging depuis notebook")
        
        # Statistiques des logs
        log_stats = logging_manager.get_log_stats()
        print(f"   📊 Statistiques: {log_stats['log_files_count']} fichiers, {log_stats['total_size_mb']} MB")
        print(f"   ✅ Logging OK - {log_stats.get('log_files_count', 0)} fichiers")
        results['logging'] = True
    except Exception as e:
        print(f"   ❌ Erreur logging: {e}")
        results['logging'] = False
    
    # Test 3: Cache
    print("\n3️⃣ Test du cache...")
    try:
        cache_manager = CacheManager(redis_url='redis://redis:6379/5')
        await cache_manager.connect()
        
        # Test simple
        await cache_manager.set("notebook", "notebook_test", {"test": True}, ttl=60)
        data = await cache_manager.get("notebook", "notebook_test")
        
        await cache_manager.disconnect()
        
        print(f"   ✅ Cache OK - données: {data}")
        results['cache'] = True
    except Exception as e:
        print(f"   ❌ Erreur cache: {e}")
        results['cache'] = False
    
    # Test 4: Agent simple
    print("\n4️⃣ Test d'un agent...")
    try:
        # Setup minimal
        cache_manager = CacheManager(redis_url='redis://redis:6379/6')
        await cache_manager.connect()
        
        from orchestrator.core import TaskContext
        
        context = TaskContext(
            session_id=str(uuid4()),
            enterprise_name="Test Company",
            current_depth=0,
            max_depth=1,
            collected_data={},
            graph=None,
            cache=cache_manager,
            config={'test_mode': True},
            errors=[],
            metrics={}
        )
        
        # Test agent
        agent = AgentNormalization({'test_mode': True})
        result = await agent.execute(context)
        
        await cache_manager.disconnect()
        
        print(f"   ✅ Agent OK - succès: {result.success}, confiance: {result.confidence_score:.2f}")
        results['agent'] = True
    except Exception as e:
        print(f"   ❌ Erreur agent: {e}")
        results['agent'] = False
    
    return results

async def main():
    """Fonction principale."""
    start_time = time.time()
    
    results = await test_system_components()
    
    execution_time = time.time() - start_time
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    total_tests = len(results)
    successful_tests = sum(1 for success in results.values() if success)
    
    print(f"⏱️  Temps d'exécution: {execution_time:.3f}s")
    print(f"📊 Tests réussis: {successful_tests}/{total_tests}")
    
    for test_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {test_name.title()}")
    
    if successful_tests == total_tests:
        print("\n🎉 Tous les tests sont réussis ! Système opérationnel.")
    elif successful_tests >= total_tests * 0.75:
        print("\n⚠️  La plupart des tests réussis, quelques problèmes mineurs.")
    else:
        print("\n🚨 Plusieurs échecs détectés, vérifiez la configuration.")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main()) 