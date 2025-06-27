#!/usr/bin/env python3
"""
Script de test interactif pour des tests personnalisés depuis le notebook.
"""

import asyncio
import sys
import time
import json
from uuid import uuid4

sys.path.append('/app')

from orchestrator.cache_manager import CacheManager
from orchestrator.core import OrchestrationEngine, TaskContext
from orchestrator.logging_config import LoggingManager
from agents.agent_normalization import AgentNormalization
from agents.agent_identification import AgentIdentification
from agents.agent_validation import AgentValidation
from loguru import logger


async def test_single_company(company_name, detailed=False):
    """Test complet sur une seule entreprise."""
    print(f"🏢 Test complet pour : {company_name}")
    print("-" * 50)
    
    # Initialisation
    cache_manager = CacheManager(redis_url='redis://redis:6379/3')
    await cache_manager.connect()
    
    logging_manager = LoggingManager()
    logging_manager.setup_logging()
    
    session_id = str(uuid4())
    
    context = TaskContext(
        session_id=session_id,
        enterprise_name=company_name,
        current_depth=0,
        max_depth=2,
        collected_data={},
        graph=None,
        cache=cache_manager,
        config={'test_mode': True, 'detailed': detailed},
        errors=[],
        metrics={}
    )
    
    results = {}
    total_time = 0
    
    # Test des agents séquentiellement
    agents = [
        ('Normalization', AgentNormalization({'test_mode': True})),
        ('Identification', AgentIdentification({'test_mode': True})),
        ('Validation', AgentValidation({'test_mode': True}))
    ]
    
    for agent_name, agent in agents:
        print(f"🔄 Exécution agent {agent_name}...")
        
        start_time = time.time()
        try:
            result = await agent.execute(context)
            execution_time = time.time() - start_time
            total_time += execution_time
            
            results[agent_name.lower()] = {
                'success': result.success,
                'confidence': result.confidence_score,
                'execution_time': execution_time,
                'data_keys': list(result.data.keys()),
                'errors': result.errors
            }
            
            status = "✅" if result.success else "❌"
            print(f"   {status} {agent_name}: {result.confidence_score:.2f} confiance ({execution_time:.3f}s)")
            
            if detailed and result.data:
                print(f"      📊 Données: {json.dumps(result.data, indent=2, default=str)[:200]}...")
            
        except Exception as e:
            execution_time = time.time() - start_time
            total_time += execution_time
            
            results[agent_name.lower()] = {
                'success': False,
                'confidence': 0.0,
                'execution_time': execution_time,
                'data_keys': [],
                'errors': [str(e)]
            }
            
            print(f"   ❌ {agent_name}: Erreur - {str(e)[:100]}")
    
    await cache_manager.disconnect()
    
    # Résumé
    successful_agents = len([r for r in results.values() if r['success']])
    avg_confidence = sum(r['confidence'] for r in results.values() if r['success']) / max(successful_agents, 1)
    
    print(f"\n📊 RÉSUMÉ pour {company_name}:")
    print(f"   ✅ Agents réussis: {successful_agents}/{len(agents)}")
    print(f"   🎯 Confiance moyenne: {avg_confidence:.2f}")
    print(f"   ⏱️  Temps total: {total_time:.3f}s")
    
    return {
        'company': company_name,
        'results': results,
        'summary': {
            'successful_agents': successful_agents,
            'total_agents': len(agents),
            'average_confidence': avg_confidence,
            'total_time': total_time
        }
    }


async def test_multiple_companies(companies, detailed=False):
    """Test sur plusieurs entreprises."""
    print(f"🏢 Test sur {len(companies)} entreprises")
    print("=" * 60)
    
    all_results = []
    start_time = time.time()
    
    for i, company in enumerate(companies, 1):
        print(f"\n[{i}/{len(companies)}] Traitement de {company}...")
        result = await test_single_company(company, detailed=detailed)
        all_results.append(result)
    
    total_time = time.time() - start_time
    
    # Statistiques globales
    successful_companies = len([r for r in all_results if r['summary']['successful_agents'] > 0])
    avg_confidence = sum(r['summary']['average_confidence'] for r in all_results) / len(all_results)
    avg_time_per_company = sum(r['summary']['total_time'] for r in all_results) / len(all_results)
    
    print(f"\n" + "=" * 60)
    print(f"📊 STATISTIQUES GLOBALES")
    print(f"   🏢 Entreprises testées: {len(companies)}")
    print(f"   ✅ Entreprises avec succès: {successful_companies}")
    print(f"   🎯 Confiance moyenne globale: {avg_confidence:.2f}")
    print(f"   ⏱️  Temps moyen par entreprise: {avg_time_per_company:.3f}s")
    print(f"   ⏱️  Temps total: {total_time:.3f}s")
    
    return {
        'companies': companies,
        'results': all_results,
        'global_stats': {
            'total_companies': len(companies),
            'successful_companies': successful_companies,
            'average_confidence': avg_confidence,
            'average_time_per_company': avg_time_per_company,
            'total_time': total_time
        }
    }


async def test_orchestrator_workflow(company_name):
    """Test du workflow complet via l'orchestrateur."""
    print(f"🎯 Test workflow orchestrateur pour : {company_name}")
    print("-" * 50)
    
    config = {
        'max_concurrent_tasks': 3,
        'session_timeout_minutes': 10,
        'test_mode': True
    }
    
    orchestrator = OrchestrationEngine(config)
    
    start_time = time.time()
    
    try:
        result = await orchestrator.execute_session(
            enterprise_name=company_name,
            session_config={
                'max_depth': 1,
                'enable_recursion': False,
                'test_mode': True
            }
        )
        
        execution_time = time.time() - start_time
        
        print(f"✅ Workflow terminé en {execution_time:.3f}s")
        print(f"📊 Session ID: {result.get('session_id', 'N/A')}")
        print(f"📊 Statut: {result.get('status', 'N/A')}")
        
        if 'collected_data' in result:
            data_keys = list(result['collected_data'].keys())
            print(f"📊 Données collectées: {data_keys}")
        
        return {
            'success': True,
            'company': company_name,
            'execution_time': execution_time,
            'result': result
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Erreur workflow: {str(e)}")
        
        return {
            'success': False,
            'company': company_name,
            'execution_time': execution_time,
            'error': str(e)
        }


async def test_cache_performance():
    """Test de performance du cache."""
    print("💾 Test de performance du cache")
    print("-" * 30)
    
    cache_manager = CacheManager(redis_url='redis://redis:6379/4')
    await cache_manager.connect()
    
    # Test d'écriture
    test_data = {"company": "Performance Test", "data": list(range(1000))}
    
    write_times = []
    read_times = []
    
    for i in range(10):
        # Test écriture
        start_time = time.time()
        await cache_manager.set("performance", f"perf_test_{i}", test_data, ttl=60)
        write_time = time.time() - start_time
        write_times.append(write_time)
        
        # Test lecture
        start_time = time.time()
        retrieved = await cache_manager.get("performance", f"perf_test_{i}")
        read_time = time.time() - start_time
        read_times.append(read_time)
    
    # Nettoyage
    await cache_manager.invalidate_pattern("performance", "*")
    await cache_manager.disconnect()
    
    avg_write = sum(write_times) / len(write_times)
    avg_read = sum(read_times) / len(read_times)
    
    print(f"📊 Résultats (10 opérations):")
    print(f"   ✍️  Écriture moyenne: {avg_write*1000:.2f}ms")
    print(f"   📖 Lecture moyenne: {avg_read*1000:.2f}ms")
    print(f"   📊 Ratio lecture/écriture: {avg_read/avg_write:.2f}")
    
    return {
        'write_times': write_times,
        'read_times': read_times,
        'avg_write_ms': avg_write * 1000,
        'avg_read_ms': avg_read * 1000,
        'ratio': avg_read / avg_write
    }


def main():
    """Fonction principale pour tests via arguments."""
    if len(sys.argv) < 2:
        print("Usage: python test_interactive.py <command> [args...]")
        print("Commands:")
        print("  single <company_name> [detailed]")
        print("  multiple <company1,company2,...> [detailed]")
        print("  orchestrator <company_name>")
        print("  cache")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "single":
        if len(sys.argv) < 3:
            print("Usage: python test_interactive.py single <company_name> [detailed]")
            sys.exit(1)
        
        company_name = sys.argv[2]
        detailed = len(sys.argv) > 3 and sys.argv[3].lower() == "detailed"
        
        result = asyncio.run(test_single_company(company_name, detailed))
        print(f"\n📋 Résultat final: {json.dumps(result, indent=2, default=str)}")
    
    elif command == "multiple":
        if len(sys.argv) < 3:
            print("Usage: python test_interactive.py multiple <company1,company2,...> [detailed]")
            sys.exit(1)
        
        companies = sys.argv[2].split(',')
        detailed = len(sys.argv) > 3 and sys.argv[3].lower() == "detailed"
        
        result = asyncio.run(test_multiple_companies(companies, detailed))
        print(f"\n📋 Résultat final: {json.dumps(result['global_stats'], indent=2)}")
    
    elif command == "orchestrator":
        if len(sys.argv) < 3:
            print("Usage: python test_interactive.py orchestrator <company_name>")
            sys.exit(1)
        
        company_name = sys.argv[2]
        result = asyncio.run(test_orchestrator_workflow(company_name))
        print(f"\n📋 Résultat final: {json.dumps(result, indent=2, default=str)}")
    
    elif command == "cache":
        result = asyncio.run(test_cache_performance())
        print(f"\n📋 Résultat final: {json.dumps(result, indent=2)}")
    
    else:
        print(f"Commande inconnue: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main() 