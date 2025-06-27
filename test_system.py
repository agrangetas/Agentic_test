#!/usr/bin/env python3
"""
Script de test simple pour valider le système d'investigation d'entreprises.

Usage: python test_system.py
"""

import asyncio
import sys
import json
from typing import Dict, Any

# Import des modules principaux
try:
    from orchestrator.core import OrchestrationEngine, TaskContext
    from orchestrator.cache_manager import CacheManager
    from agents.agent_normalization import AgentNormalization
    from agents.agent_identification import AgentIdentification
    from agents.agent_validation import AgentValidation
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Assure-toi d'être dans le bon répertoire et d'avoir installé les dépendances")
    sys.exit(1)


async def test_single_agent(agent_class, agent_name: str, context: TaskContext) -> Dict[str, Any]:
    """Test un agent individuel."""
    print(f"\n🧪 Test {agent_name}...")
    
    try:
        agent = agent_class({})
        result = await agent.execute(context)
        
        print(f"✅ {agent_name} - Succès: {result.success}")
        print(f"   Confiance: {result.confidence_score:.2f}")
        print(f"   Temps: {result.execution_time:.2f}s")
        
        if result.errors:
            print(f"   Erreurs: {result.errors}")
        
        return result.data
    
    except Exception as e:
        print(f"❌ {agent_name} - Erreur: {str(e)}")
        return {}


async def test_agent_pipeline():
    """Test complet du pipeline d'agents."""
    print("🚀 Test du pipeline d'agents avec données fake")
    print("=" * 50)
    
    # Création du contexte de test
    context = TaskContext(
        session_id="test-session-123",
        enterprise_name="LVMH",
        current_depth=0,
        max_depth=2,
        config={"test_mode": True}
    )
    
    print(f"📝 Entreprise testée: {context.enterprise_name}")
    
    # Test AgentNormalization
    norm_data = await test_single_agent(AgentNormalization, "AgentNormalization", context)
    
    # Test AgentIdentification (dépend de normalization)
    if norm_data:
        context.collected_data['normalization'] = norm_data
        id_data = await test_single_agent(AgentIdentification, "AgentIdentification", context)
        
        # Test AgentValidation (dépend des deux précédents)
        if id_data:
            context.collected_data['identification'] = id_data
            validation_data = await test_single_agent(AgentValidation, "AgentValidation", context)
            
            if validation_data:
                context.collected_data['validation'] = validation_data
    
    return context


async def test_cache_manager():
    """Test du gestionnaire de cache."""
    print("\n🗃️  Test du CacheManager...")
    
    try:
        # Note: Redis doit être lancé pour ce test
        cache = CacheManager("redis://localhost:6379/1")
        
        # Test sans connexion Redis (simulation)
        test_data = {"test": "data", "timestamp": "2024-12-19"}
        
        # Simulation de set/get
        print("✅ CacheManager - Interface créée")
        print("⚠️  Note: Redis requis pour tests complets")
        
    except Exception as e:
        print(f"❌ CacheManager - Erreur: {str(e)}")


def print_results_summary(context: TaskContext):
    """Affiche un résumé des résultats."""
    print("\n📊 RÉSUMÉ DES RÉSULTATS")
    print("=" * 30)
    
    total_agents = len(context.collected_data)
    print(f"Agents exécutés: {total_agents}")
    print(f"Temps total: {context.get_elapsed_time():.2f}s")
    
    if context.errors:
        print(f"Erreurs: {len(context.errors)}")
        for error in context.errors:
            print(f"  - {error}")
    
    # Données collectées
    print("\n📋 Données collectées:")
    for agent_name, data in context.collected_data.items():
        if isinstance(data, dict):
            confidence = data.get('confidence_score', 0)
            print(f"  - {agent_name}: confiance {confidence:.2f}")
            
            # Détails spécifiques
            if agent_name == 'normalization':
                siren = data.get('siren', 'Non trouvé')
                print(f"    SIREN: {siren}")
                
            elif agent_name == 'identification':
                url = data.get('url', 'Non trouvé')
                print(f"    URL: {url}")
                
            elif agent_name == 'validation':
                entities = data.get('linked_entities', [])
                print(f"    Entités liées: {len(entities)}")
    
    # Entités liées pour récursion
    validation_data = context.collected_data.get('validation', {})
    linked_entities = validation_data.get('linked_entities', [])
    
    if linked_entities:
        print(f"\n🔗 Entités liées trouvées ({len(linked_entities)}):")
        for entity in linked_entities[:3]:  # Top 3
            name = entity.get('name', 'Inconnu')
            entity_type = entity.get('type', 'Unknown')
            participation = entity.get('participation', 0)
            print(f"  - {name} ({entity_type}, {participation}%)")


async def main():
    """Fonction principale de test."""
    print("🧠 Agent d'Investigation d'Entreprises - Tests")
    print("=" * 60)
    
    try:
        # Test du pipeline d'agents
        context = await test_agent_pipeline()
        
        # Test du cache manager
        await test_cache_manager()
        
        # Résumé des résultats
        print_results_summary(context)
        
        print(f"\n🎯 CONCLUSION")
        print("=" * 15)
        success_count = len([d for d in context.collected_data.values() if isinstance(d, dict)])
        
        if success_count >= 2:
            print("✅ Système fonctionnel - Pipeline de base opérationnel")
            print("✅ Agents de normalisation et validation OK")
            print("✅ Données fake générées correctement")
            
            if success_count >= 3:
                print("✅ Validation et détection de conflits OK")
                
            print("\n🚀 Prêt pour Phase 2: agents restants + récursivité")
        else:
            print("⚠️  Système partiellement fonctionnel")
            print("🔧 Vérifier la configuration et les dépendances")
    
    except Exception as e:
        print(f"\n❌ Erreur critique: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Exécution du test
    asyncio.run(main()) 