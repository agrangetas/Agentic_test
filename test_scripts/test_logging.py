#!/usr/bin/env python3
"""
Script de test pour le système de logging avancé.

Teste tous les niveaux de logs, la rotation, et les logs par agent.
"""

import asyncio
import sys
import time
from pathlib import Path

# Ajout du répertoire du projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestrator.logging_config import setup_logging, get_agent_logger, get_log_stats
from orchestrator.core import OrchestrationEngine, TaskContext
from agents.agent_normalization import AgentNormalization
from agents.agent_identification import AgentIdentification
from agents.agent_validation import AgentValidation
from loguru import logger


async def test_logging_system():
    """Test complet du système de logging."""
    
    print("🧪 Démarrage des tests du système de logging...\n")
    
    # 1. Configuration du logging
    print("1️⃣ Configuration du système de logging...")
    setup_logging()
    print("   ✅ Logging configuré\n")
    
    # 2. Test des logs généraux
    print("2️⃣ Test des logs généraux...")
    logger.info("Test message INFO", extra={"test_type": "general", "event_type": "test_info"})
    logger.warning("Test message WARNING", extra={"test_type": "general", "event_type": "test_warning"})
    logger.error("Test message ERROR", extra={"test_type": "general", "event_type": "test_error"})
    logger.debug("Test message DEBUG", extra={"test_type": "general", "event_type": "test_debug"})
    print("   ✅ Logs généraux testés\n")
    
    # 3. Test des logs par agent
    print("3️⃣ Test des logs par agent...")
    
    # Test agent Normalization
    norm_logger = get_agent_logger("normalization", "test-session-001")
    norm_logger.info("Test normalization agent", extra={"test_data": "LVMH"})
    norm_logger.debug("Normalization debug message", extra={"function": "test_normalize"})
    
    # Test agent Identification
    id_logger = get_agent_logger("identification", "test-session-001")
    id_logger.info("Test identification agent", extra={"siren": "775670417"})
    id_logger.debug("Identification debug message", extra={"function": "test_identify"})
    
    # Test agent Validation
    val_logger = get_agent_logger("validation", "test-session-001")
    val_logger.info("Test validation agent", extra={"conflicts": 2})
    val_logger.warning("Validation warning", extra={"conflict_type": "siren_mismatch"})
    
    print("   ✅ Logs par agent testés\n")
    
    # 4. Test des agents avec contexte réel
    print("4️⃣ Test des agents avec contexte de session...")
    
    # Création d'un contexte de test
    context = TaskContext(
        session_id="test-session-002",
        enterprise_name="LVMH",
        current_depth=0,
        max_depth=2,
        config={"test_mode": True}
    )
    
    # Test agent Normalization
    print("   🔄 Test AgentNormalization...")
    norm_agent = AgentNormalization({"test_mode": True})
    norm_result = await norm_agent.execute(context)
    print(f"      ✅ Normalization: success={norm_result.success}, confidence={norm_result.confidence_score:.2f}")
    
    # Test agent Identification
    print("   🔄 Test AgentIdentification...")
    id_agent = AgentIdentification({"test_mode": True})
    id_result = await id_agent.execute(context)
    print(f"      ✅ Identification: success={id_result.success}, confidence={id_result.confidence_score:.2f}")
    
    # Test agent Validation
    print("   🔄 Test AgentValidation...")
    val_agent = AgentValidation({"test_mode": True})
    val_result = await val_agent.execute(context)
    print(f"      ✅ Validation: success={val_result.success}, confidence={val_result.confidence_score:.2f}")
    
    print("   ✅ Tous les agents testés\n")
    
    # 5. Test de performance et volume
    print("5️⃣ Test de performance et volume...")
    start_time = time.time()
    
    # Génération de logs en volume
    for i in range(100):
        logger.debug(f"Volume test message {i}", extra={
            "iteration": i,
            "test_type": "volume",
            "event_type": "volume_test"
        })
        
        if i % 10 == 0:
            test_logger = get_agent_logger("volume_test", f"session-{i}")
            test_logger.info(f"Volume test for agent {i}", extra={
                "iteration": i,
                "batch": i // 10
            })
    
    volume_time = time.time() - start_time
    print(f"   ✅ 100 messages générés en {volume_time:.3f}s\n")
    
    # 6. Test des métriques et statistiques
    print("6️⃣ Test des métriques et statistiques...")
    
    # Logs de métriques
    logger.info("📊 Cache hit rate: 85.2%", extra={
        "metric_name": "cache_hit_rate",
        "metric_value": 85.2,
        "metric_unit": "%",
        "event_type": "performance_metric"
    })
    
    logger.info("⏱️ Average response time: 1.234s", extra={
        "metric_name": "avg_response_time",
        "metric_value": 1.234,
        "metric_unit": "s",
        "event_type": "performance_metric"
    })
    
    # Statistiques des logs
    log_stats = get_log_stats()
    print(f"   📊 Statistiques des logs:")
    print(f"      - Répertoire: {log_stats['logs_directory']}")
    print(f"      - Fichiers de log: {log_stats['total_log_files']}")
    print(f"      - Taille totale: {log_stats['total_size_mb']} MB")
    print(f"      - Agents avec logs: {', '.join(log_stats['agents_with_logs'])}")
    
    print("   ✅ Métriques testées\n")
    
    # 7. Test des événements de session
    print("7️⃣ Test des événements de session...")
    
    session_id = "test-session-events"
    logger.info(f"🎯 Session {session_id}: started", extra={
        "session_id": session_id,
        "session_event": "started",
        "session_details": {"enterprise": "Test Corp", "depth": 1},
        "event_type": "session_event"
    })
    
    logger.info(f"🎯 Session {session_id}: agent_completed", extra={
        "session_id": session_id,
        "session_event": "agent_completed",
        "session_details": {"agent": "normalization", "success": True},
        "event_type": "session_event"
    })
    
    logger.info(f"🎯 Session {session_id}: completed", extra={
        "session_id": session_id,
        "session_event": "completed",
        "session_details": {"total_time": 5.67, "agents_run": 3},
        "event_type": "session_event"
    })
    
    print("   ✅ Événements de session testés\n")
    
    # 8. Test des logs d'erreur avec contexte
    print("8️⃣ Test des logs d'erreur avec contexte...")
    
    try:
        # Simulation d'une erreur
        raise ValueError("Test error for logging system")
    except Exception as e:
        logger.error("❌ Test error occurred", extra={
            "error_type": type(e).__name__,
            "error_message": str(e),
            "error_context": {
                "function": "test_logging_system",
                "test_phase": "error_testing",
                "session_id": "test-session-error"
            },
            "event_type": "error"
        })
    
    print("   ✅ Logs d'erreur testés\n")
    
    # 9. Résumé final
    print("9️⃣ Résumé des tests...")
    
    final_stats = get_log_stats()
    print(f"   📈 Résultats finaux:")
    print(f"      - Fichiers de log créés: {final_stats['total_log_files']}")
    print(f"      - Taille totale: {final_stats['total_size_mb']} MB")
    print(f"      - Agents avec logs: {len(final_stats['agents_with_logs'])}")
    print(f"      - Agents testés: {', '.join(final_stats['agents_with_logs'])}")
    
    print("\n🎉 Tous les tests du système de logging réussis!")
    
    # Instructions pour l'utilisateur
    print(f"\n📁 Logs disponibles dans: {final_stats['logs_directory']}")
    print(f"   - Logs généraux: app_YYYY-MM-DD.log")
    print(f"   - Logs par agent: agents/AGENT_NAME_YYYY-MM-DD.log")
    print(f"\n🔍 Commandes utiles:")
    print(f"   - Voir tous les logs: tail -f logs/app_*.log")
    print(f"   - Voir logs d'un agent: tail -f logs/agents/normalization_*.log")
    print(f"   - Chercher des erreurs: grep 'ERROR' logs/app_*.log")
    print(f"   - Chercher par session: grep 'test-session-001' logs/**/*.log")


async def test_orchestrator_with_logging():
    """Test de l'orchestrateur avec logging complet."""
    print("\n🎯 Test de l'orchestrateur avec logging...")
    
    config = {
        'max_concurrent_tasks': 3,
        'session_timeout_minutes': 5,
        'test_mode': True
    }
    
    orchestrator = OrchestrationEngine(config)
    
    try:
        result = await orchestrator.execute_session(
            enterprise_name="Test Company",
            session_config={
                'max_depth': 1,
                'test_mode': True
            }
        )
        
        print(f"   ✅ Session orchestrateur: {result['session_id']}")
        print(f"      - Statut: {result['status']}")
        print(f"      - Temps: {result.get('execution_time', 0):.3f}s")
        
    except Exception as e:
        print(f"   ❌ Erreur orchestrateur: {e}")


async def main():
    """Fonction principale de test."""
    print("🧠 Test du Système de Logging Avancé")
    print("=" * 50)
    
    try:
        await test_logging_system()
        await test_orchestrator_with_logging()
        
        print("\n✅ Tous les tests terminés avec succès!")
        
    except Exception as e:
        logger.error("Test failed", extra={
            "error": str(e),
            "error_type": type(e).__name__,
            "event_type": "test_failure"
        })
        print(f"\n❌ Échec des tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 