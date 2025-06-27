#!/usr/bin/env python3
"""
Script de test détaillé pour tous les agents.
"""

import asyncio
import sys
import time
from uuid import uuid4

sys.path.append('/app')

from orchestrator.cache_manager import CacheManager
from orchestrator.core import TaskContext
from agents.agent_normalization import AgentNormalization
from agents.agent_identification import AgentIdentification
from agents.agent_validation import AgentValidation
from loguru import logger


async def setup_test_context(enterprise_name="Test Company SARL"):
    """Crée un contexte de test."""
    cache_manager = CacheManager(redis_url='redis://redis:6379/1')
    await cache_manager.connect()
    
    context = TaskContext(
        session_id=str(uuid4()),
        enterprise_name=enterprise_name,
        current_depth=0,
        max_depth=2,
        collected_data={},
        graph=None,
        cache=cache_manager,
        config={'test_mode': True},
        errors=[],
        metrics={}
    )
    
    return context, cache_manager


async def test_agent_normalization_detailed():
    """Test détaillé de l'agent de normalisation."""
    print("🔄 Test détaillé Agent Normalization...")
    
    context, cache_manager = await setup_test_context("Société Test SARL")
    
    agent = AgentNormalization({
        'cache_ttl': 3600,
        'test_mode': True,
        'confidence_threshold': 0.5
    })
    
    # Test 1: Exécution normale
    result = await agent.execute(context)
    
    print(f"   📊 Résultat: {'✅' if result.success else '❌'}")
    print(f"   🎯 Confiance: {result.confidence_score:.2f}")
    print(f"   ⏱️  Temps: {result.execution_time:.3f}s")
    print(f"   📝 Données: {list(result.data.keys())}")
    
    # Vérifications spécifiques
    assert 'normalized_name' in result.data
    assert 'variants' in result.data
    assert 'siren' in result.data
    assert isinstance(result.data['variants'], list)
    
    # Test 2: Validation des données
    validation_errors = agent.validate_data_consistency(result.data)
    print(f"   🔍 Erreurs de validation: {len(validation_errors)}")
    
    # Test 3: Cache
    cache_key = agent.get_cache_key(context)
    cached_result = await agent.get_cached_result(context)
    print(f"   💾 Cache key: {cache_key[:50]}...")
    print(f"   💾 Résultat en cache: {'Oui' if cached_result else 'Non'}")
    
    await cache_manager.disconnect()
    
    return {
        'success': result.success,
        'confidence': result.confidence_score,
        'execution_time': result.execution_time,
        'data_keys': list(result.data.keys()),
        'validation_errors': len(validation_errors),
        'cached': cached_result is not None
    }


async def test_agent_identification_detailed():
    """Test détaillé de l'agent d'identification."""
    print("🔍 Test détaillé Agent Identification...")
    
    context, cache_manager = await setup_test_context("LVMH Group")
    
    # Simuler des données de normalisation
    context.collected_data['normalization'] = {
        'normalized_name': 'LVMH GROUP',
        'siren': '123456789',
        'confidence_score': 0.8
    }
    
    agent = AgentIdentification({
        'cache_ttl': 3600,
        'test_mode': True,
        'url_verification': True
    })
    
    # Test 1: Exécution avec données de normalisation
    result = await agent.execute(context)
    
    print(f"   📊 Résultat: {'✅' if result.success else '❌'}")
    print(f"   🎯 Confiance: {result.confidence_score:.2f}")
    print(f"   ⏱️  Temps: {result.execution_time:.3f}s")
    print(f"   🌐 URL trouvée: {result.data.get('url', 'N/A')}")
    print(f"   🏢 SIREN: {result.data.get('siren', 'N/A')}")
    
    # Vérifications spécifiques
    assert 'siren' in result.data
    assert 'url' in result.data
    assert 'verification_status' in result.data
    
    # Test 2: Sans données de normalisation
    context_empty = await setup_test_context("Unknown Company")
    context_empty[0].collected_data = {}
    
    result_empty = await agent.execute(context_empty[0])
    print(f"   📊 Sans normalisation: {'✅' if result_empty.success else '❌'}")
    
    await cache_manager.disconnect()
    await context_empty[1].disconnect()
    
    return {
        'success': result.success,
        'confidence': result.confidence_score,
        'execution_time': result.execution_time,
        'url_found': 'url' in result.data and result.data['url'],
        'siren_found': 'siren' in result.data and result.data['siren'],
        'without_normalization': result_empty.success
    }


async def test_agent_validation_detailed():
    """Test détaillé de l'agent de validation."""
    print("✅ Test détaillé Agent Validation...")
    
    context, cache_manager = await setup_test_context("Microsoft Corporation")
    
    # Simuler des données de plusieurs agents
    context.collected_data = {
        'normalization': {
            'normalized_name': 'MICROSOFT CORPORATION',
            'siren': '123456789',
            'confidence_score': 0.8
        },
        'identification': {
            'siren': '123456789',  # Cohérent
            'url': 'https://www.microsoft.com',
            'confidence_score': 0.7
        }
    }
    
    agent = AgentValidation({
        'cache_ttl': 3600,
        'test_mode': True,
        'conflict_resolution': True
    })
    
    # Test 1: Validation avec données cohérentes
    result = await agent.execute(context)
    
    print(f"   📊 Résultat: {'✅' if result.success else '❌'}")
    print(f"   🎯 Confiance: {result.confidence_score:.2f}")
    print(f"   ⏱️  Temps: {result.execution_time:.3f}s")
    print(f"   🔍 Conflits détectés: {len(result.data.get('conflicts_detected', []))}")
    print(f"   🔧 Conflits résolus: {len(result.data.get('conflicts_resolved', []))}")
    print(f"   📊 Score qualité: {result.data.get('data_quality_score', 0):.2f}")
    
    # Test 2: Validation avec conflits
    context_conflict = await setup_test_context("Conflict Company")
    context_conflict[0].collected_data = {
        'normalization': {
            'siren': '123456789',
            'confidence_score': 0.8
        },
        'identification': {
            'siren': '987654321',  # Conflit !
            'confidence_score': 0.6
        }
    }
    
    result_conflict = await agent.execute(context_conflict[0])
    print(f"   ⚠️  Avec conflits: {'✅' if result_conflict.success else '❌'}")
    print(f"   🔍 Conflits: {len(result_conflict.data.get('conflicts_detected', []))}")
    
    await cache_manager.disconnect()
    await context_conflict[1].disconnect()
    
    return {
        'success': result.success,
        'confidence': result.confidence_score,
        'execution_time': result.execution_time,
        'conflicts_detected': len(result.data.get('conflicts_detected', [])),
        'conflicts_resolved': len(result.data.get('conflicts_resolved', [])),
        'quality_score': result.data.get('data_quality_score', 0),
        'handles_conflicts': result_conflict.success
    }


async def test_agents_integration():
    """Test d'intégration des agents."""
    print("🔗 Test d'intégration des agents...")
    
    context, cache_manager = await setup_test_context("Apple Inc")
    
    # Configuration des agents
    agent_config = {
        'cache_ttl': 3600,
        'test_mode': True
    }
    
    agents = {
        'normalization': AgentNormalization(agent_config),
        'identification': AgentIdentification(agent_config),
        'validation': AgentValidation(agent_config)
    }
    
    results = {}
    
    # Exécution séquentielle (comme dans l'orchestrateur)
    for agent_name, agent in agents.items():
        print(f"   🔄 Exécution {agent_name}...")
        
        start_time = time.time()
        result = await agent.execute(context)
        execution_time = time.time() - start_time
        
        results[agent_name] = {
            'success': result.success,
            'confidence': result.confidence_score,
            'execution_time': execution_time,
            'data_keys': list(result.data.keys()),
            'errors': result.errors
        }
        
        print(f"      {'✅' if result.success else '❌'} {agent_name}: {result.confidence_score:.2f}")
    
    # Vérifications d'intégration
    normalization_data = context.collected_data.get('normalization', {})
    identification_data = context.collected_data.get('identification', {})
    validation_data = context.collected_data.get('validation', {})
    
    # Cohérence des données
    siren_consistency = (
        normalization_data.get('siren') == identification_data.get('siren')
        if normalization_data.get('siren') and identification_data.get('siren')
        else True
    )
    
    print(f"   🔍 Cohérence SIREN: {'✅' if siren_consistency else '❌'}")
    print(f"   📊 Données collectées: {len(context.collected_data)} agents")
    print(f"   ⏱️  Temps total: {sum(r['execution_time'] for r in results.values()):.3f}s")
    
    await cache_manager.disconnect()
    
    return {
        'agents_results': results,
        'data_consistency': siren_consistency,
        'total_agents': len(results),
        'successful_agents': len([r for r in results.values() if r['success']]),
        'total_execution_time': sum(r['execution_time'] for r in results.values())
    }


async def test_agents_performance():
    """Test de performance des agents."""
    print("⚡ Test de performance des agents...")
    
    companies = [
        "Google LLC", "Amazon.com Inc", "Meta Platforms Inc",
        "Tesla Inc", "Netflix Inc"
    ]
    
    agent_config = {'cache_ttl': 3600, 'test_mode': True}
    agent = AgentNormalization(agent_config)
    
    start_time = time.time()
    results = []
    
    for company in companies:
        context, cache_manager = await setup_test_context(company)
        
        result = await agent.execute(context)
        results.append({
            'company': company,
            'success': result.success,
            'execution_time': result.execution_time,
            'confidence': result.confidence_score
        })
        
        await cache_manager.disconnect()
    
    total_time = time.time() - start_time
    successful = [r for r in results if r['success']]
    avg_time = sum(r['execution_time'] for r in results) / len(results)
    avg_confidence = sum(r['confidence'] for r in successful) / len(successful) if successful else 0
    
    print(f"   📊 Entreprises testées: {len(companies)}")
    print(f"   ✅ Succès: {len(successful)}/{len(results)}")
    print(f"   ⏱️  Temps total: {total_time:.3f}s")
    print(f"   📊 Temps moyen: {avg_time:.3f}s")
    print(f"   🎯 Confiance moyenne: {avg_confidence:.2f}")
    
    return {
        'total_companies': len(companies),
        'successful_companies': len(successful),
        'total_time': total_time,
        'average_time': avg_time,
        'average_confidence': avg_confidence,
        'results': results
    }


async def main():
    """Fonction principale des tests agents."""
    print("=" * 60)
    print("🤖 TESTS DÉTAILLÉS DES AGENTS")
    print("=" * 60)
    
    start_time = time.time()
    all_results = {}
    
    try:
        # Test 1: Agent Normalization
        print("\n" + "=" * 40)
        norm_results = await test_agent_normalization_detailed()
        all_results['normalization'] = norm_results
        
        # Test 2: Agent Identification
        print("\n" + "=" * 40)
        id_results = await test_agent_identification_detailed()
        all_results['identification'] = id_results
        
        # Test 3: Agent Validation
        print("\n" + "=" * 40)
        val_results = await test_agent_validation_detailed()
        all_results['validation'] = val_results
        
        # Test 4: Intégration
        print("\n" + "=" * 40)
        integration_results = await test_agents_integration()
        all_results['integration'] = integration_results
        
        # Test 5: Performance
        print("\n" + "=" * 40)
        perf_results = await test_agents_performance()
        all_results['performance'] = perf_results
        
        execution_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS AGENTS")
        print("=" * 60)
        
        print(f"⏱️  Temps d'exécution total: {execution_time:.3f}s")
        print(f"🤖 Agents testés: 3 (Normalization, Identification, Validation)")
        
        # Résumé par agent
        for agent_name in ['normalization', 'identification', 'validation']:
            if agent_name in all_results:
                result = all_results[agent_name]
                print(f"   {'✅' if result['success'] else '❌'} {agent_name.title()}: {result['confidence']:.2f} confiance")
        
        # Résumé intégration
        integration = all_results.get('integration', {})
        print(f"🔗 Intégration: {integration.get('successful_agents', 0)}/{integration.get('total_agents', 0)} agents")
        
        # Résumé performance
        performance = all_results.get('performance', {})
        print(f"⚡ Performance: {performance.get('average_time', 0):.3f}s/agent moyen")
        
        return all_results
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}


if __name__ == "__main__":
    results = asyncio.run(main())
    sys.exit(0 if 'error' not in results else 1) 