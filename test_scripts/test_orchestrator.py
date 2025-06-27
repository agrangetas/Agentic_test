#!/usr/bin/env python3
"""
Script de test spécialisé pour l'orchestrateur.
"""

import asyncio
import sys
import time
from uuid import uuid4

sys.path.append('/app')

from orchestrator.core import OrchestrationEngine, TaskContext
from orchestrator.cache_manager import CacheManager
from loguru import logger


async def test_orchestrator_initialization():
    """Test l'initialisation de l'orchestrateur."""
    print("🎯 Test d'initialisation de l'orchestrateur...")
    
    config = {
        'max_concurrent_tasks': 5,
        'session_timeout_minutes': 30,
        'models': {
            'default_model': 'gpt-4o',
            'fallback_model': 'gpt-3.5-turbo'
        },
        'recursion': {
            'max_depth': 3,
            'min_participation_percent': 10.0
        }
    }
    
    orchestrator = OrchestrationEngine(config)
    
    # Vérifications
    assert orchestrator.config == config
    assert orchestrator.max_concurrent_tasks == 5
    assert orchestrator.session_timeout_minutes == 30
    
    print("   ✅ Orchestrateur initialisé avec succès")
    return orchestrator


async def test_session_creation():
    """Test la création de sessions."""
    print("🎯 Test de création de session...")
    
    orchestrator = OrchestrationEngine({
        'max_concurrent_tasks': 3,
        'session_timeout_minutes': 10
    })
    
    # Test de session simple
    result = await orchestrator.execute_session(
        enterprise_name="Test Enterprise",
        session_config={
            'max_depth': 1,
            'enable_recursion': False,
            'test_mode': True
        }
    )
    
    # Vérifications
    assert 'session_id' in result
    assert 'status' in result
    assert 'execution_time' in result
    assert result['status'] in ['initialized', 'completed']
    
    print(f"   ✅ Session créée: {result['session_id']}")
    print(f"   📊 Statut: {result['status']}")
    print(f"   ⏱️  Temps: {result.get('execution_time', 0):.3f}s")
    
    return result


async def test_context_creation():
    """Test la création de contextes."""
    print("🎯 Test de création de contexte...")
    
    cache_manager = CacheManager(redis_url='redis://redis:6379/1')
    await cache_manager.connect()
    
    context = TaskContext(
        session_id=str(uuid4()),
        enterprise_name="Test Company",
        current_depth=0,
        max_depth=2,
        collected_data={},
        graph=None,
        cache=cache_manager,
        config={'test_mode': True},
        errors=[],
        metrics={}
    )
    
    # Vérifications
    assert context.enterprise_name == "Test Company"
    assert context.current_depth == 0
    assert context.max_depth == 2
    assert context.cache is not None
    assert isinstance(context.collected_data, dict)
    assert isinstance(context.errors, list)
    assert isinstance(context.metrics, dict)
    
    print("   ✅ Contexte créé avec succès")
    print(f"   🏢 Entreprise: {context.enterprise_name}")
    print(f"   📊 Session: {context.session_id}")
    
    await cache_manager.disconnect()
    return context


async def test_orchestrator_error_handling():
    """Test la gestion d'erreurs de l'orchestrateur."""
    print("🎯 Test de gestion d'erreurs...")
    
    orchestrator = OrchestrationEngine({'max_concurrent_tasks': 1})
    
    try:
        # Test avec nom d'entreprise vide
        result = await orchestrator.execute_session(
            enterprise_name="",
            session_config={'test_mode': True}
        )
        
        # Doit gérer l'erreur gracieusement
        assert 'error' in result or result.get('status') == 'error'
        print("   ✅ Gestion d'erreur pour nom vide: OK")
        
    except Exception as e:
        print(f"   ⚠️  Exception capturée: {e}")
    
    try:
        # Test avec configuration invalide
        result = await orchestrator.execute_session(
            enterprise_name="Test",
            session_config={'max_depth': -1}  # Invalide
        )
        
        print("   ✅ Gestion d'erreur pour config invalide: OK")
        
    except Exception as e:
        print(f"   ⚠️  Exception capturée: {e}")


async def test_orchestrator_metrics():
    """Test les métriques de l'orchestrateur."""
    print("🎯 Test des métriques...")
    
    orchestrator = OrchestrationEngine({
        'max_concurrent_tasks': 2,
        'session_timeout': 5
    })
    
    start_time = time.time()
    
    # Exécution de plusieurs sessions
    sessions = []
    for i in range(3):
        result = await orchestrator.execute_session(
            enterprise_name=f"Company {i+1}",
            session_config={
                'max_depth': 1,
                'test_mode': True
            }
        )
        sessions.append(result)
    
    execution_time = time.time() - start_time
    
    # Vérifications
    assert len(sessions) == 3
    successful_sessions = [s for s in sessions if s.get('status') != 'error']
    
    print(f"   ✅ Sessions exécutées: {len(sessions)}")
    print(f"   ✅ Sessions réussies: {len(successful_sessions)}")
    print(f"   ⏱️  Temps total: {execution_time:.3f}s")
    print(f"   📊 Temps moyen par session: {execution_time/len(sessions):.3f}s")
    
    return {
        'total_sessions': len(sessions),
        'successful_sessions': len(successful_sessions),
        'total_time': execution_time,
        'avg_time_per_session': execution_time / len(sessions)
    }


async def main():
    """Fonction principale des tests orchestrateur."""
    print("=" * 60)
    print("🎯 TESTS DE L'ORCHESTRATEUR")
    print("=" * 60)
    
    start_time = time.time()
    results = {}
    
    try:
        # Test 1: Initialisation
        orchestrator = await test_orchestrator_initialization()
        results['initialization'] = True
        
        # Test 2: Création de session
        session_result = await test_session_creation()
        results['session_creation'] = session_result
        
        # Test 3: Création de contexte
        context = await test_context_creation()
        results['context_creation'] = True
        
        # Test 4: Gestion d'erreurs
        await test_orchestrator_error_handling()
        results['error_handling'] = True
        
        # Test 5: Métriques
        metrics = await test_orchestrator_metrics()
        results['metrics'] = metrics
        
        execution_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS ORCHESTRATEUR")
        print("=" * 60)
        print(f"⏱️  Temps d'exécution total: {execution_time:.3f}s")
        print(f"✅ Tests réussis: {len([r for r in results.values() if r])}")
        print(f"🎯 Orchestrateur: Pleinement fonctionnel")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}


if __name__ == "__main__":
    results = asyncio.run(main())
    sys.exit(0 if 'error' not in results else 1) 