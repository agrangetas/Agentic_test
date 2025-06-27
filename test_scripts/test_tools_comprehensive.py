#!/usr/bin/env python3
"""
Script de test complet pour tous les outils (tools).
"""

import asyncio
import sys
import time
import json

sys.path.append('/app')

from tools.tool_normalize_name import ToolNormalizeName
from tools.tool_match_enterprise import ToolMatchEnterprise
from tools.tool_ner_extraction import ToolNERExtraction
from tools.tool_identify_website import ToolIdentifyWebsite
from tools.tool_validate_consistency import ToolValidateConsistency
from tools.tool_resolve_conflicts import ToolResolveConflicts
from loguru import logger


def test_tool_normalize_name():
    """Test l'outil de normalisation de noms."""
    print("🔤 Test ToolNormalizeName...")
    
    tool = ToolNormalizeName()
    
    test_cases = [
        "LVMH Moët Hennessy Louis Vuitton SE",
        "société test sarl",
        "Apple Inc.",
        "Microsoft Corporation",
        "Google LLC"
    ]
    
    results = []
    
    for test_name in test_cases:
        start_time = time.time()
        result = tool.run({'raw_name': test_name})
        execution_time = time.time() - start_time
        
        results.append({
            'input': test_name,
            'normalized': result.get('normalized', ''),
            'variants': result.get('variants', []),
            'confidence': result.get('confidence', 0),
            'execution_time': execution_time
        })
        
        print(f"   📝 {test_name}")
        print(f"      ➡️  {result.get('normalized', 'N/A')}")
        print(f"      🔄 {len(result.get('variants', []))} variantes")
        print(f"      🎯 {result.get('confidence', 0):.2f} confiance")
    
    avg_time = sum(r['execution_time'] for r in results) / len(results)
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    
    print(f"   📊 Temps moyen: {avg_time:.3f}s")
    print(f"   🎯 Confiance moyenne: {avg_confidence:.2f}")
    
    return {
        'tool_name': 'normalize_name',
        'test_cases': len(test_cases),
        'average_time': avg_time,
        'average_confidence': avg_confidence,
        'results': results
    }


def test_tool_match_enterprise():
    """Test l'outil de matching d'entreprises."""
    print("🔍 Test ToolMatchEnterprise...")
    
    tool = ToolMatchEnterprise()
    
    test_cases = [
        {
            'name_variants': ['APPLE INC', 'Apple Inc.', 'Apple Incorporated'],
            'expected_matches': 1
        },
        {
            'name_variants': ['MICROSOFT CORP', 'Microsoft Corporation'],
            'expected_matches': 1
        },
        {
            'name_variants': ['Unknown Company XYZ'],
            'expected_matches': 0
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        start_time = time.time()
        result = tool.run({'name_variants': test_case['name_variants']})
        execution_time = time.time() - start_time
        
        matches = result.get('matches', [])
        best_match = result.get('best_match', {})
        
        results.append({
            'variants': test_case['name_variants'],
            'matches_found': len(matches),
            'best_match_siren': best_match.get('siren', 'N/A'),
            'confidence': result.get('confidence', 0),
            'execution_time': execution_time
        })
        
        print(f"   📝 {test_case['name_variants'][0]}")
        print(f"      🎯 {len(matches)} correspondances")
        print(f"      🏢 SIREN: {best_match.get('siren', 'N/A')}")
        print(f"      📊 {result.get('confidence', 0):.2f} confiance")
    
    avg_time = sum(r['execution_time'] for r in results) / len(results)
    successful_matches = len([r for r in results if r['matches_found'] > 0])
    
    print(f"   📊 Temps moyen: {avg_time:.3f}s")
    print(f"   ✅ Correspondances trouvées: {successful_matches}/{len(test_cases)}")
    
    return {
        'tool_name': 'match_enterprise',
        'test_cases': len(test_cases),
        'successful_matches': successful_matches,
        'average_time': avg_time,
        'results': results
    }


def test_tool_ner_extraction():
    """Test l'outil d'extraction d'entités nommées."""
    print("🏷️  Test ToolNERExtraction...")
    
    tool = ToolNERExtraction()
    
    test_texts = [
        "Apple Inc. est une entreprise dirigée par Tim Cook, basée à Cupertino.",
        "Microsoft Corporation a été fondée par Bill Gates et Paul Allen.",
        "LVMH est contrôlée par Bernard Arnault via sa holding Groupe Arnault.",
        "Tesla Inc. développe des véhicules électriques sous la direction d'Elon Musk."
    ]
    
    results = []
    
    for text in test_texts:
        start_time = time.time()
        result = tool.run({'text': text})
        execution_time = time.time() - start_time
        
        entities = result.get('entities', [])
        companies = [e for e in entities if e.get('type') == 'COMPANY']
        persons = [e for e in entities if e.get('type') == 'PERSON']
        
        results.append({
            'text': text[:50] + '...',
            'total_entities': len(entities),
            'companies': len(companies),
            'persons': len(persons),
            'confidence': result.get('confidence', 0),
            'execution_time': execution_time
        })
        
        print(f"   📝 {text[:50]}...")
        print(f"      🏢 {len(companies)} entreprises")
        print(f"      👤 {len(persons)} personnes")
        print(f"      📊 {result.get('confidence', 0):.2f} confiance")
    
    avg_time = sum(r['execution_time'] for r in results) / len(results)
    total_entities = sum(r['total_entities'] for r in results)
    
    print(f"   📊 Temps moyen: {avg_time:.3f}s")
    print(f"   🏷️  Total entités: {total_entities}")
    
    return {
        'tool_name': 'ner_extraction',
        'test_cases': len(test_texts),
        'total_entities': total_entities,
        'average_time': avg_time,
        'results': results
    }


def test_tool_identify_website():
    """Test l'outil d'identification de site web."""
    print("🌐 Test ToolIdentifyWebsite...")
    
    tool = ToolIdentifyWebsite()
    
    test_companies = [
        "Apple Inc",
        "Microsoft Corporation", 
        "Google LLC",
        "Unknown Company XYZ"
    ]
    
    results = []
    
    for company in test_companies:
        start_time = time.time()
        result = tool.run({'name': company})
        execution_time = time.time() - start_time
        
        url = result.get('url', '')
        status = result.get('status', '')
        
        results.append({
            'company': company,
            'url_found': bool(url and url != 'N/A'),
            'url': url,
            'status': status,
            'confidence': result.get('confidence', 0),
            'execution_time': execution_time
        })
        
        print(f"   🏢 {company}")
        print(f"      🌐 {url if url else 'N/A'}")
        print(f"      📊 {status} - {result.get('confidence', 0):.2f}")
    
    avg_time = sum(r['execution_time'] for r in results) / len(results)
    urls_found = len([r for r in results if r['url_found']])
    
    print(f"   📊 Temps moyen: {avg_time:.3f}s")
    print(f"   🌐 URLs trouvées: {urls_found}/{len(test_companies)}")
    
    return {
        'tool_name': 'identify_website',
        'test_cases': len(test_companies),
        'urls_found': urls_found,
        'average_time': avg_time,
        'results': results
    }


def test_tool_validate_consistency():
    """Test l'outil de validation de cohérence."""
    print("✅ Test ToolValidateConsistency...")
    
    tool = ToolValidateConsistency()
    
    # Test avec données cohérentes
    consistent_data = {
        'source1': {
            'siren': '123456789',
            'name': 'Apple Inc',
            'url': 'https://www.apple.com'
        },
        'source2': {
            'siren': '123456789',  # Cohérent
            'name': 'APPLE INC',   # Variante acceptable
            'url': 'https://apple.com'  # Variante acceptable
        }
    }
    
    # Test avec données incohérentes
    inconsistent_data = {
        'source1': {
            'siren': '123456789',
            'name': 'Apple Inc'
        },
        'source2': {
            'siren': '987654321',  # Conflit !
            'name': 'Microsoft Corp'  # Conflit !
        }
    }
    
    test_cases = [
        {'data': consistent_data, 'expected_conflicts': 0},
        {'data': inconsistent_data, 'expected_conflicts': 2}
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        start_time = time.time()
        result = tool.run({'data_sources': test_case['data']})
        execution_time = time.time() - start_time
        
        conflicts = result.get('conflicts', [])
        is_consistent = result.get('is_consistent', False)
        quality_score = result.get('quality_score', 0)
        
        results.append({
            'test_case': i + 1,
            'conflicts_found': len(conflicts),
            'is_consistent': is_consistent,
            'quality_score': quality_score,
            'execution_time': execution_time
        })
        
        print(f"   📊 Test case {i + 1}")
        print(f"      ⚠️  {len(conflicts)} conflits")
        print(f"      ✅ Cohérent: {is_consistent}")
        print(f"      📊 Score qualité: {quality_score:.2f}")
    
    avg_time = sum(r['execution_time'] for r in results) / len(results)
    
    print(f"   📊 Temps moyen: {avg_time:.3f}s")
    
    return {
        'tool_name': 'validate_consistency',
        'test_cases': len(test_cases),
        'average_time': avg_time,
        'results': results
    }


def test_tool_resolve_conflicts():
    """Test l'outil de résolution de conflits."""
    print("🔧 Test ToolResolveConflicts...")
    
    tool = ToolResolveConflicts()
    
    # Conflits de test
    test_conflicts = [
        {
            'field': 'siren',
            'values': [
                {'value': '123456789', 'source': 'inpi', 'confidence': 0.9},
                {'value': '987654321', 'source': 'web', 'confidence': 0.6}
            ]
        },
        {
            'field': 'url',
            'values': [
                {'value': 'https://www.apple.com', 'source': 'web', 'confidence': 0.8},
                {'value': 'https://apple.com', 'source': 'api', 'confidence': 0.7}
            ]
        }
    ]
    
    start_time = time.time()
    result = tool.run({'conflicting_data': test_conflicts})
    execution_time = time.time() - start_time
    
    resolved = result.get('resolved_data', {})
    resolutions = result.get('resolutions', [])
    confidence = result.get('confidence', 0)
    
    print(f"   🔧 {len(test_conflicts)} conflits traités")
    print(f"   ✅ {len(resolutions)} résolutions")
    print(f"   📊 Confiance globale: {confidence:.2f}")
    print(f"   ⏱️  Temps: {execution_time:.3f}s")
    
    # Vérifications
    for resolution in resolutions:
        field = resolution.get('field')
        chosen_value = resolution.get('chosen_value')
        reason = resolution.get('reason', '')
        print(f"      {field}: {chosen_value} ({reason})")
    
    return {
        'tool_name': 'resolve_conflicts',
        'conflicts_processed': len(test_conflicts),
        'resolutions_made': len(resolutions),
        'confidence': confidence,
        'execution_time': execution_time,
        'resolved_data': resolved
    }


async def test_tools_async_operations():
    """Test les opérations asynchrones des outils."""
    print("⚡ Test opérations asynchrones...")
    
    tools = [
        ToolNormalizeName(),
        ToolMatchEnterprise(),
        ToolNERExtraction(),
        ToolIdentifyWebsite()
    ]
    
    test_data = [
        {'raw_name': 'Apple Inc'},
        {'name_variants': ['Microsoft Corp']},
        {'text': 'Google LLC est une entreprise technologique.'},
        {'name': 'Tesla Inc'}
    ]
    
    start_time = time.time()
    
    # Test exécution parallèle
    tasks = []
    for tool, data in zip(tools, test_data):
        if hasattr(tool, 'run_async'):
            tasks.append(tool.run_async(data))
        else:
            # Fallback synchrone
            tasks.append(asyncio.create_task(asyncio.to_thread(tool.run, data)))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    execution_time = time.time() - start_time
    
    successful = len([r for r in results if not isinstance(r, Exception)])
    
    print(f"   ⚡ {len(tools)} outils testés en parallèle")
    print(f"   ✅ {successful}/{len(tools)} succès")
    print(f"   ⏱️  Temps total: {execution_time:.3f}s")
    
    return {
        'tools_tested': len(tools),
        'successful_executions': successful,
        'parallel_execution_time': execution_time,
        'results': [r for r in results if not isinstance(r, Exception)]
    }


def test_tools_error_handling():
    """Test la gestion d'erreurs des outils."""
    print("🚨 Test gestion d'erreurs...")
    
    tools_and_invalid_data = [
        (ToolNormalizeName(), {}),  # Données manquantes
        (ToolMatchEnterprise(), {'name_variants': None}),  # Données nulles
        (ToolNERExtraction(), {'text': ''}),  # Texte vide
        (ToolIdentifyWebsite(), {'name': None})  # Nom null
    ]
    
    results = []
    
    for tool, invalid_data in tools_and_invalid_data:
        try:
            start_time = time.time()
            result = tool.run(invalid_data)
            execution_time = time.time() - start_time
            
            # L'outil doit gérer l'erreur gracieusement
            results.append({
                'tool': tool.__class__.__name__,
                'handled_gracefully': True,
                'result_type': type(result).__name__,
                'execution_time': execution_time
            })
            
        except Exception as e:
            results.append({
                'tool': tool.__class__.__name__,
                'handled_gracefully': False,
                'error': str(e),
                'execution_time': 0
            })
    
    graceful_handling = len([r for r in results if r['handled_gracefully']])
    
    print(f"   🛡️  {graceful_handling}/{len(tools_and_invalid_data)} outils gèrent les erreurs")
    
    for result in results:
        status = "✅" if result['handled_gracefully'] else "❌"
        print(f"      {status} {result['tool']}")
    
    return {
        'tools_tested': len(tools_and_invalid_data),
        'graceful_error_handling': graceful_handling,
        'results': results
    }


async def main():
    """Fonction principale des tests outils."""
    print("=" * 60)
    print("🔧 TESTS COMPLETS DES OUTILS")
    print("=" * 60)
    
    start_time = time.time()
    all_results = {}
    
    try:
        # Test 1: Normalisation de noms
        print("\n" + "=" * 40)
        norm_results = test_tool_normalize_name()
        all_results['normalize_name'] = norm_results
        
        # Test 2: Matching d'entreprises
        print("\n" + "=" * 40)
        match_results = test_tool_match_enterprise()
        all_results['match_enterprise'] = match_results
        
        # Test 3: Extraction NER
        print("\n" + "=" * 40)
        ner_results = test_tool_ner_extraction()
        all_results['ner_extraction'] = ner_results
        
        # Test 4: Identification de sites
        print("\n" + "=" * 40)
        website_results = test_tool_identify_website()
        all_results['identify_website'] = website_results
        
        # Test 5: Validation de cohérence
        print("\n" + "=" * 40)
        validation_results = test_tool_validate_consistency()
        all_results['validate_consistency'] = validation_results
        
        # Test 6: Résolution de conflits
        print("\n" + "=" * 40)
        conflict_results = test_tool_resolve_conflicts()
        all_results['resolve_conflicts'] = conflict_results
        
        # Test 7: Opérations asynchrones
        print("\n" + "=" * 40)
        async_results = await test_tools_async_operations()
        all_results['async_operations'] = async_results
        
        # Test 8: Gestion d'erreurs
        print("\n" + "=" * 40)
        error_results = test_tools_error_handling()
        all_results['error_handling'] = error_results
        
        execution_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS OUTILS")
        print("=" * 60)
        
        print(f"⏱️  Temps d'exécution total: {execution_time:.3f}s")
        print(f"🔧 Outils testés: 6 principaux + tests transversaux")
        
        # Résumé par outil
        tool_names = ['normalize_name', 'match_enterprise', 'ner_extraction', 
                     'identify_website', 'validate_consistency', 'resolve_conflicts']
        
        for tool_name in tool_names:
            if tool_name in all_results:
                result = all_results[tool_name]
                avg_time = result.get('average_time', result.get('execution_time', 0))
                print(f"   ✅ {tool_name}: {avg_time:.3f}s moyen")
        
        # Tests transversaux
        async_success = all_results.get('async_operations', {}).get('successful_executions', 0)
        error_handling = all_results.get('error_handling', {}).get('graceful_error_handling', 0)
        
        print(f"⚡ Async: {async_success}/4 outils")
        print(f"🛡️  Gestion erreurs: {error_handling}/4 outils")
        
        return all_results
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}


if __name__ == "__main__":
    results = asyncio.run(main())
    sys.exit(0 if 'error' not in results else 1) 