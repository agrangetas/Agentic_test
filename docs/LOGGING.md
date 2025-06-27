# 📊 Système de Logging Avancé

## Vue d'ensemble

Le système de logging avancé de l'agent d'investigation d'entreprises offre une gestion fine et structurée des logs avec :

- **Fichiers séparés par agent** avec rotation quotidienne
- **Logs structurés** avec métadonnées détaillées  
- **Niveaux configurables** par composant et type d'événement
- **Compression automatique** et rétention configurable
- **Métriques et statistiques** en temps réel

## 🏗️ Architecture

```
logs/
├── app_2024-12-19.log              # Logs généraux
├── app_2024-12-19.log.gz           # Archives compressées
├── agents/                         # Logs par agent
│   ├── normalization_2024-12-19.log
│   ├── identification_2024-12-19.log
│   ├── validation_2024-12-19.log
│   └── ...
└── metrics/                        # Métriques exportées (optionnel)
    └── metrics_2024-12-19.json
```

## 📝 Configuration

### Fichier de configuration : `config/logging_config.yaml`

```yaml
logs_directory: "logs"

# Logging console
console:
  enabled: true
  level: "INFO"
  format: "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>"

# Logging fichier principal
file:
  enabled: true
  level: "DEBUG"
  rotation: "1 day"
  retention: "30 days"
  compression: "gz"

# Logging par agent
agents:
  enabled: true
  level: "DEBUG"
  rotation: "1 day"
  retention: "30 days"
  compression: "gz"
  format: "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {function}:{line} | {extra[session_id]:-} | {message}"

# Niveaux par composant
components:
  orchestrator:
    level: "DEBUG"
    include_metrics: true
    
  cache_manager:
    level: "DEBUG"
    log_operations: true
    
  agents:
    normalization:
      level: "DEBUG"
      log_fake_data: true
```

## 🚀 Utilisation

### Initialisation du système

```python
from orchestrator.logging_config import setup_logging, get_agent_logger

# Configuration du logging global
setup_logging()

# Logger pour un agent spécifique
logger = get_agent_logger("normalization", session_id="session-123")
```

### Logs structurés avec métadonnées

```python
# Log avec contexte détaillé
logger.info("Agent execution started", extra={
    "session_id": "session-123",
    "enterprise_name": "LVMH",
    "agent_name": "normalization",
    "execution_time": 1.234,
    "event_type": "agent_execution_start"
})

# Log d'erreur avec contexte
logger.error("Processing failed", extra={
    "session_id": "session-123",
    "error_type": "ValidationError",
    "error_message": "Invalid SIREN format",
    "function": "validate_siren",
    "event_type": "processing_error"
})
```

### Logs de performance

```python
# Métriques de performance
logger.info("Cache performance", extra={
    "metric_name": "cache_hit_rate",
    "metric_value": 85.2,
    "metric_unit": "%",
    "event_type": "performance_metric"
})

# Temps d'exécution
logger.info("Agent completed", extra={
    "agent_name": "normalization",
    "execution_time": 2.456,
    "confidence_score": 0.95,
    "event_type": "agent_completion"
})
```

## 📊 Types d'événements

### Événements de session
- `session_start` : Début de session d'exploration
- `session_end` : Fin de session
- `session_error` : Erreur de session

### Événements d'agents
- `agent_init` : Initialisation d'agent
- `agent_execution_start` : Début d'exécution
- `agent_execution_completed` : Fin d'exécution
- `agent_execution_errors` : Erreurs d'exécution

### Événements de cache
- `cache_hit` : Succès de cache
- `cache_miss` : Échec de cache
- `cache_error` : Erreur de cache

### Événements de données
- `data_quality` : Qualité des données
- `validation_errors` : Erreurs de validation
- `conflict_detected` : Conflit détecté
- `conflict_resolved` : Conflit résolu

## 🔍 Analyse des logs

### Commandes utiles

```bash
# Voir tous les logs en temps réel
tail -f logs/app_*.log

# Logs d'un agent spécifique
tail -f logs/agents/normalization_*.log

# Rechercher des erreurs
grep "ERROR" logs/app_*.log

# Rechercher par session
grep "session-123" logs/**/*.log

# Rechercher par type d'événement
grep "agent_execution_start" logs/**/*.log

# Statistiques d'erreurs
grep "ERROR" logs/app_*.log | wc -l

# Top des erreurs
grep "ERROR" logs/app_*.log | cut -d'|' -f5 | sort | uniq -c | sort -nr
```

### Filtrage par métadonnées

```bash
# Sessions avec erreurs
grep "session_error" logs/app_*.log

# Agents avec faible confiance
grep "confidence_score.*0\.[0-4]" logs/agents/*.log

# Opérations de cache lentes
grep "cache_operation.*[5-9]\." logs/app_*.log

# Conflits de données
grep "conflict_detected" logs/agents/validation_*.log
```

## 📈 Métriques et statistiques

### Obtention des statistiques

```python
from orchestrator.logging_config import get_log_stats

stats = get_log_stats()
print(f"Fichiers de log: {stats['total_log_files']}")
print(f"Taille totale: {stats['total_size_mb']} MB")
print(f"Agents avec logs: {stats['agents_with_logs']}")
```

### Métriques disponibles

- **Nombre de fichiers de log**
- **Taille totale des logs**
- **Agents actifs**
- **Fichier le plus ancien/récent**
- **Répartition par agent**

## 🛠️ Tests

### Script de test complet

```bash
# Lancer les tests du système de logging
python test_logging.py
```

### Tests inclus

1. **Configuration du logging**
2. **Logs généraux** (INFO, WARNING, ERROR, DEBUG)
3. **Logs par agent** avec session ID
4. **Exécution d'agents** avec contexte réel
5. **Test de performance** et volume
6. **Métriques et statistiques**
7. **Événements de session**
8. **Logs d'erreur** avec contexte
9. **Test de l'orchestrateur**

## 🔧 Maintenance

### Rotation automatique

Les logs sont automatiquement :
- **Archivés** chaque jour à minuit
- **Compressés** en format .gz
- **Supprimés** après la période de rétention (30 jours par défaut)

### Nettoyage manuel

```python
from orchestrator.logging_config import get_logging_manager

log_manager = get_logging_manager()
log_manager.cleanup_old_logs(days_to_keep=15)
```

### Surveillance de l'espace disque

```bash
# Taille des logs
du -sh logs/

# Logs les plus volumineux
du -h logs/**/*.log | sort -hr | head -10

# Nettoyage des archives anciennes
find logs/ -name "*.gz" -mtime +30 -delete
```

## 🚨 Alertes et monitoring

### Configuration des alertes (optionnel)

```yaml
alerts:
  enabled: true
  error_threshold: 10  # Erreurs par heure
  webhook_url: "https://hooks.slack.com/..."
```

### Métriques Prometheus (optionnel)

Le système peut exporter des métriques vers Prometheus :

```python
from prometheus_client import start_http_server

# Démarrage du serveur de métriques
start_http_server(8000)
```

Métriques disponibles :
- `agent_executions_total`
- `agent_execution_duration_seconds`
- `agent_confidence_scores`
- `system_resources`

## 🎯 Bonnes pratiques

### 1. Niveaux de log appropriés

```python
# DEBUG : Détails de débogage
logger.debug("Processing step 1/5", extra={"step": 1})

# INFO : Informations importantes
logger.info("Agent completed successfully", extra={"success": True})

# WARNING : Situations anormales mais récupérables
logger.warning("Low confidence score", extra={"confidence": 0.3})

# ERROR : Erreurs nécessitant une attention
logger.error("Failed to process data", extra={"error": str(e)})
```

### 2. Métadonnées structurées

Toujours inclure :
- `session_id` : Identifiant de session
- `function` : Nom de la fonction
- `event_type` : Type d'événement
- `execution_time` : Temps d'exécution (si applicable)

### 3. Messages descriptifs

```python
# ❌ Mauvais
logger.info("Done")

# ✅ Bon
logger.info("Enterprise normalization completed", extra={
    "enterprise_name": "LVMH",
    "variants_found": 5,
    "confidence_score": 0.95
})
```

### 4. Gestion des erreurs

```python
try:
    result = process_data()
except Exception as e:
    logger.error("Data processing failed", extra={
        "error_type": type(e).__name__,
        "error_message": str(e),
        "input_data": data_summary,
        "event_type": "processing_error"
    })
    raise
```

## 📚 Références

- [Loguru Documentation](https://loguru.readthedocs.io/)
- [Structured Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [Log Analysis with grep/awk](https://www.gnu.org/software/gawk/manual/gawk.html)

---

**Note :** Ce système de logging est conçu pour être performant et non-bloquant. Tous les logs sont écrits de manière asynchrone pour ne pas impacter les performances du système principal. 