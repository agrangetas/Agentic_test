# 🧠 Agent d'Investigation d'Entreprises

> **Système agentique personnalisé pour l'investigation intelligente d'entreprises**

[![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7+-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg)](https://www.docker.com/)

## 🎯 Objectif

Agent autonome capable, à partir du nom d'une entreprise, de :

- ✅ **Identifier** son site et informations de base  
- ✅ **Extraire** activités, liens capitalistiques, CA, actualités
- ✅ **Explorer** récursivement les entreprises liées
- ✅ **Stocker** les résultats structurés dans PostgreSQL
- ✅ **Valider** la cohérence des données entre sources
- ✅ **Résoudre** automatiquement les conflits

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Orchestrateur  │────│  Agents Métiers  │────│  Outils & APIs  │
│     Maison      │    │   Spécialisés    │    │   + Cache Redis │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │   PostgreSQL Database   │
                    │  + Graph Temporaire     │
                    └─────────────────────────┘
```

### 🧩 Composants Principaux

#### 🎭 **Orchestrateur Custom**
- **State Machine** avec gestion des dépendances
- **Execution asynchrone** avec retry automatique  
- **Gestion des timeouts** et priorités
- **Métriques** temps réel

#### 🤖 **Agents Spécialisés**
- **AgentNormalization** : Normalise les noms d'entreprises
- **AgentIdentification** : Trouve SIREN + URL officielle
- **AgentValidation** : Détecte et résout les conflits
- **AgentWebData, AgentINPI, AgentNews** : *(en développement)*

#### 🗄️ **Infrastructure**
- **PostgreSQL** : Stockage structuré avec relations
- **Redis** : Cache intelligent avec compression
- **Celery** : Tâches lourdes en arrière-plan
- **Docker** : Environnement containerisé

## 🚀 Installation

### Prérequis
- Docker & Docker Compose
- Python 3.11+
- Poetry *(optionnel pour dev)*

### 1. Clone du projet
```bash
git clone <repo>
cd agent-company-intelligence
```

### 2. Configuration
```bash
# Copie et édite les variables d'environnement
cp env.example .env

# Édite .env avec tes clés API
nano .env
```

### 3. Lancement avec Docker
```bash
# Démarre tous les services
docker-compose up -d

# Vérifie les logs
docker-compose logs -f app
```

### 4. Services disponibles
- **Application** : http://localhost:8000
- **Flower** (monitoring Celery) : http://localhost:5555
- **PostgreSQL** : localhost:5432
- **Redis** : localhost:6379

## 📝 Utilisation

### Mode Test avec Données Fake

```python
from orchestrator.core import OrchestrationEngine
import asyncio

async def test_exploration():
    # Configuration
    config = {
        'max_concurrent_tasks': 3,
        'max_depth': 2,
        'session_timeout_minutes': 10
    }
    
    # Création de l'orchestrateur
    engine = OrchestrationEngine(config)
    
    # Lancement d'une session d'exploration
    result = await engine.execute_session(
        enterprise_name="LVMH",
        session_config={'max_depth': 2}
    )
    
    print(f"Session: {result['session_id']}")
    print(f"Status: {result['status']}")

# Exécution
asyncio.run(test_exploration())
```

### Exemple de Résultat

```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "enterprise_name": "LVMH",
  "success": true,
  "data": {
    "normalization": {
      "normalized_name": "LVMH MOET HENNESSY LOUIS VUITTON",
      "siren": "775670417",
      "confidence_score": 0.95
    },
    "identification": {
      "url": "https://www.lvmh.fr",
      "verified": true
    },
    "validation": {
      "consistency_score": 0.85,
      "linked_entities": [
        {"name": "Louis Vuitton", "type": "subsidiary"},
        {"name": "Moët & Chandon", "type": "subsidiary"}
      ]
    }
  },
  "execution_time": 3.2,
  "entities_found": ["Louis Vuitton", "Moët & Chandon", "Hennessy"]
}
```

## 🧪 Tests

### Tests Unitaires
```bash
# Avec Poetry
poetry run pytest

# Avec Docker
docker-compose exec app pytest
```

### Tests d'Intégration
```bash
# Test complet avec données fake
poetry run pytest tests/test_fake_flows.py -v
```

## 📊 Monitoring

### Métriques Disponibles
- **Taux de succès** par agent
- **Temps d'exécution** moyen  
- **Cache hit rate**
- **Conflits détectés/résolus**

### Logs Structurés
```bash
# Logs de l'application
docker-compose logs app

# Logs spécifiques à un agent
docker-compose logs app | grep "agent.normalization"
```

## 🔧 Configuration Avancée

### Politiques de Cache
Édite `config/cache_policy.yaml` :
```yaml
cache_policy:
  enterprise_data:
    ttl: "7d"
    compress: true
    max_size_mb: 10
```

### Critères de Récursivité  
Édite `config/recursion_criteria.yaml` :
```yaml
recursion_criteria:
  max_depth: 3
  min_participation_percent: 10.0
  max_entities_per_level: 5
```

### Modèles LLM
Édite `config/models.yaml` :
```yaml
per_task:
  normalize_name:
    provider: openai
    model: gpt-3.5-turbo
    temperature: 0.3
```

## 🚧 État du Développement

### ✅ Phase 1 (80% complétée)
- [x] Architecture orchestrateur
- [x] Agents de base avec validation
- [x] Cache Redis + PostgreSQL
- [x] Données fake pour tests
- [ ] Graph manager
- [ ] Agents restants

### 🔄 Phase 2 (Prochaine)
- [ ] Récursivité intelligente
- [ ] Mémoire long terme
- [ ] API REST complète

### 🎯 Phase 3 (Future)  
- [ ] Interface web
- [ ] APIs réelles (INPI, web scraping)
- [ ] Monitoring avancé

## 🤝 Contribution

### Structure du Projet
```
project-root/
├── orchestrator/          # Moteur d'orchestration
├── agents/               # Agents spécialisés  
├── tools/                # Outils et APIs (à venir)
├── memory/               # Gestion mémoire/graph
├── validation/           # Validation données
├── monitoring/           # Métriques/dashboard
├── config/              # Fichiers de configuration
├── db/                  # Scripts PostgreSQL
└── tests/               # Tests automatisés
```

### Ajouter un Nouvel Agent
1. Hérite de `FullFeaturedAgent`
2. Implémente `execute()` et `validate_input()`
3. Ajoute dans `agents/__init__.py`
4. Crée les tests correspondants

## 📚 Documentation Technique

- **[Plan d'Implémentation](Implementation_plan.md)** : Architecture détaillée
- **[Objectifs](Objectives.md)** : Cahier des charges initial
- **API Reference** : *(à venir)*

## 🏷️ Licence

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.

---

🚀 **Prêt à explorer le monde des entreprises de manière intelligente !** 