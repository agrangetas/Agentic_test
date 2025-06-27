# 🧠 Plan d'Implémentation : Agent d'Investigation d'Entreprises


# Rappel Objectif
Construire un système agentique personnalisable, orchestré maison, capable de collecter, structurer et résumer les données d'une entreprise (et de ses entreprises liées), avec stockage et mémoire, en utilisant différents LLM et outils, dans un environnement Dockerisé.


## 🎯 Objectif

Construire un **agent autonome** capable, à partir du nom d'une entreprise, de :

* Identifier son site et informations de base
* Extraire et structurer ses activités, liens capitalistiques, CA, actualités
* Explorer récursivement les entreprises liées
* Stocker les résultats structurés dans une base de données PostgreSQL

## 🏗️ Architecture Globale

```
[ Entrée utilisateur (nom entreprise) ]
              │
              ▼
     [ Orchestrateur Maison ]
              │
    ┌─────────┼─────────────────────┐
    ▼         ▼                     ▼
[ Agent Normalization ] [ Agent Info ] [ Agent INPI ]
    │                      │             │
    ▼                      ▼             ▼
[ Agent Validation ] [ Agent News ] [ Agent Capital ]
    │                      │             │
    ▼                      ▼             ▼
[Tools & LLMs] ─────> [Tools & LLMs] <─── [Tools & LLMs]
    │                      │             │
              ▼
[ Graph de connaissance temporaire ]
              │
              ▼
[ Récursivité contrôlée (entreprises liées) ]
              │
              ▼
[ Base PostgreSQL ]
```

## 🧩 Composants

### 1. Orchestrateur Maison

**Rôle :** orchestrer les agents, gérer la stratégie, contrôler la récursivité et la profondeur, historiser les actions.

**À inclure :**

* File d'exécution des agents (ordonnancement avec dépendances)
* Arbre d'actions avec mémoire locale temporaire
* Logique de choix du modèle (GPT-4 / Mistral / Claude) en fonction de la tâche
* Gestion de profondeur et cycles avec critères d'arrêt intelligents
* État local de session (par entreprise) avec cache TTL
* Moteur de raisonnement (via prompts LLM ou règles)
* **Système de scoring de fiabilité des sources**
* **Gestion des conflits de données entre sources**
* **Fallback automatique en cas d'échec d'API**

**Stratégie de démarrage :**
```
1. AgentNormalization (normalise le nom d'entrée)
2. AgentIdentification (trouve SIREN + URL)
3. Parallèle: [AgentWebData, AgentINPI, AgentNews]
4. AgentCapital (utilise données INPI)
5. AgentValidation (vérifie cohérence)
6. AgentRecursion (si pertinent)
7. AgentSynthese (génère résumé final)
```

### 2. Agents spécialisés

Chaque agent est un module avec :

* Objectif précis
* Modèle LLM spécifique (ajusté selon complexité)
* Outils associés
* Mémoire locale optionnelle
* Interprétation des résultats et renvoi structuré
* **Système de scoring de confiance des données**

**Agents principaux :**

* `AgentNormalization` → **[NOUVEAU]** Normalise et déduplique les noms d'entreprises
* `AgentIdentification` → Trouve SIREN/URL via matching + API externe
* `AgentWebData` → Interroge PostgreSQL pour info extraite du site web
* `AgentINPI` → Récupère doc INPI, appelle outil de parsing
* `AgentCapitalLinks` → Extrait capital/filiales depuis INPI structuré
* `AgentNewsIntel` → Analyse actualités extraites, identifie événements clés
* `AgentValidation` → **[NOUVEAU]** Vérifie cohérence des données entre sources
* `AgentRecursion` → Détecte entités liées et redémarre avec critères intelligents
* `AgentSynthese` → Génère résumé structuré multi-format

**Détail des nouveaux agents :**

#### AgentNormalization
- **Entrée :** Nom d'entreprise brut (ex: "LVMH", "Louis Vuitton SA")
- **Sortie :** Nom normalisé + variantes possibles + score de confiance
- **Outils :** `tool_normalize_name`, `tool_match_enterprise`, `tool_ner_extraction`

#### AgentValidation
- **Entrée :** Données collectées de multiple sources
- **Sortie :** Données validées + conflits identifiés + scores de fiabilité
- **Outils :** `tool_validate_consistency`, `tool_resolve_conflicts`

### 3. Outils

**Rôle :** Exécuter les actions concrètes, renvoyer un format standard (type JSON).

**Caractéristiques :**

* Retourne données **factices mais formatées** pour tests
* Chaque outil = module Python indépendant, avec `run(input) → output`
* **Gestion d'erreurs gracieuse avec fallbacks**
* **Système de cache intégré**
* Peut être mocké ou branché sur une API réelle plus tard

**Outils existants améliorés :**

* `tool_identify_website(name)` → avec fallback si échec
* `tool_fetch_site_data(url)` → avec timeout et retry
* `tool_get_inpi_documents(name_or_siren)` → avec cache
* `tool_parse_inpi_documents(documents)` → avec validation
* `tool_extract_news(name_or_siren)` → avec déduplication
* `tool_extract_links(structured_data)` → avec scoring
* `tool_store_pg(data)` → avec gestion de conflits

**Nouveaux outils :**

* `tool_normalize_name(raw_name)` → Normalise un nom d'entreprise
* `tool_match_enterprise(name_variants)` → Trouve SIREN/ID via matching flou
* `tool_ner_extraction(text)` → Extrait entités nommées (entreprises, personnes)
* `tool_validate_consistency(data_sources)` → Valide cohérence entre sources
* `tool_resolve_conflicts(conflicting_data)` → Résout conflits avec règles
* `tool_prioritize_entities(entities_list)` → Priorise entités pour récursion
* `tool_generate_report(data, format)` → Génère rapport (JSON/HTML/PDF)

### 4. Modèles LLM (pluggables)

**Stratégie améliorée :**

```yaml
defaults:
  provider: openai
  model: gpt-4o
  fallback_model: gpt-3.5-turbo

per_task:
  normalize_name:
    provider: openai
    model: gpt-3.5-turbo
  
  extract_site_info:
    provider: openai
    model: gpt-3.5-turbo

  parse_inpi_docs:
    provider: openai
    model: gpt-4-turbo
    fallback_model: gpt-4o

  ner_extraction:
    provider: openai
    model: gpt-4o

  validate_consistency:
    provider: openai
    model: gpt-4-turbo

  summarization:
    provider: openai
    model: gpt-4o

  conflict_resolution:
    provider: openai
    model: gpt-4-turbo

  reasoning:
    provider: openai
    model: gpt-4o

  link_analysis:
    provider: openai
    model: gpt-4-turbo
```

**Routing basé sur :**

* Tâche (analyse > extraction)
* Taille des données
* Précision attendue
* **Disponibilité des modèles (fallback automatique)**

### 5. Graph de connaissance temporaire

**Structure :** Graph orienté temporaire par session (en mémoire ou Redis pour perfs).

**Contenu :**

* Nœuds : entités (entreprise, personne, événement) avec scores de confiance
* Arêtes : relations (filiale, partenaire, mentionnée dans, CA lié à, etc.) avec poids
* Annoté par agent/source + timestamp
* **Système de versioning pour tracking des modifications**
* Peut être exporté en JSON-Graph, GraphQL ou visualisé via D3.js

**Nouvelles fonctionnalités :**
* Détection automatique de cycles
* Calcul de centralité pour identifier entités clés
* Merge intelligent de nœuds similaires

### 6. Contrôle de récursivité intelligente

**Objectif :** éviter cycles et explosion combinatoire avec critères intelligents

**Critères d'arrêt précis :**

```python
RECURSION_CRITERIA = {
    "max_depth": 3,
    "min_participation_percent": 10.0,  # % de participation minimum
    "min_ca_threshold": 1_000_000,      # CA minimum en euros
    "relevant_sectors": ["tech", "finance", "pharma"],  # Secteurs prioritaires
    "max_entities_per_level": 5,        # Max entités par niveau
    "similarity_threshold": 0.8,        # Éviter doublons
    "time_limit_minutes": 30            # Limite temps par session
}
```

**Mécanisme amélioré :**

* Niveau de profondeur max configurable par session
* **Scoring de pertinence des entreprises liées** (CA, %, secteur)
* Cache mémoire / DB pour éviter de re-traiter
* **Priorisation intelligente** via `tool_prioritize_entities`
* **Arrêt anticipé** si trop d'entités découvertes

### 7. Système de cache et mémoire

**Mémoire des agents :**
* Contexte local par agent (session-based)
* Mémoire court terme (Redis avec TTL configurable)
* Mémoire long terme (PostgreSQL avec historique)

**Politique de cache :**
```python
CACHE_POLICY = {
    "enterprise_data": {"ttl": "7d", "invalidate_on": ["inpi_update"]},
    "news_data": {"ttl": "1d", "invalidate_on": ["time"]},
    "web_data": {"ttl": "3d", "invalidate_on": ["url_change"]},
    "inpi_data": {"ttl": "30d", "invalidate_on": ["manual_refresh"]}
}
```

---

## 🗄️ Base de Données PostgreSQL

**Schéma amélioré :**

```sql
-- Table principale des entreprises
entreprises (
  id UUID PRIMARY KEY,
  nom TEXT NOT NULL,
  nom_normalise TEXT, -- Nouveau : nom normalisé
  variantes_nom TEXT[], -- Nouveau : variantes du nom
  siren TEXT UNIQUE,
  url TEXT,
  date_creation DATE,
  secteur TEXT,
  ca_estime BIGINT, -- Nouveau : CA estimé
  taille_entreprise TEXT, -- Nouveau : PME/ETI/GE
  resume TEXT,
  score_confiance FLOAT DEFAULT 0.5,
  date_maj TIMESTAMP DEFAULT NOW(),
  source_principale TEXT -- Nouveau : source principale des données
);

-- Nouveau : table des sources de données
sources_donnees (
  id UUID PRIMARY KEY,
  nom TEXT NOT NULL,
  type TEXT, -- inpi, web, news, api
  fiabilite_score FLOAT DEFAULT 0.5,
  derniere_maj TIMESTAMP DEFAULT NOW()
);

documents_inpi (
  id UUID PRIMARY KEY,
  entreprise_id UUID REFERENCES entreprises(id),
  type TEXT,
  contenu JSONB,
  date_maj TIMESTAMP DEFAULT NOW(),
  score_confiance FLOAT DEFAULT 0.8
);

liens_capitaux (
  id UUID PRIMARY KEY,
  entreprise_source UUID REFERENCES entreprises(id),
  entreprise_cible UUID REFERENCES entreprises(id),
  type_lien TEXT,
  pourcentage FLOAT,
  montant BIGINT, -- Nouveau : montant en euros
  date_lien DATE, -- Nouveau : date du lien
  source_id UUID REFERENCES sources_donnees(id),
  score_confiance FLOAT DEFAULT 0.5
);

actualites (
  id UUID PRIMARY KEY,
  entreprise_id UUID REFERENCES entreprises(id),
  date DATE,
  type TEXT,
  titre TEXT, -- Nouveau : titre de l'actualité
  resume TEXT,
  impact_estime TEXT, -- Nouveau : impact estimé (positif/négatif/neutre)
  source TEXT,
  url_source TEXT, -- Nouveau : URL de la source
  score_confiance FLOAT DEFAULT 0.3
);

-- Nouveau : table des conflits de données
conflits_donnees (
  id UUID PRIMARY KEY,
  entreprise_id UUID REFERENCES entreprises(id),
  champ_conflit TEXT,
  valeur_source1 TEXT,
  valeur_source2 TEXT,
  source1_id UUID REFERENCES sources_donnees(id),
  source2_id UUID REFERENCES sources_donnees(id),
  statut TEXT DEFAULT 'non_resolu', -- non_resolu, resolu, ignore
  resolution TEXT,
  date_detection TIMESTAMP DEFAULT NOW()
);

exploration_logs (
  id UUID PRIMARY KEY,
  session_id UUID, -- Nouveau : ID de session
  entreprise_id UUID REFERENCES entreprises(id),
  agent TEXT,
  input JSONB,
  output JSONB,
  duree_execution INTEGER, -- Nouveau : durée en secondes
  statut TEXT, -- Nouveau : success, error, timeout
  date_executed TIMESTAMP DEFAULT NOW()
);

-- Nouveau : table des sessions d'exploration
sessions_exploration (
  id UUID PRIMARY KEY,
  entreprise_initiale TEXT,
  parametres JSONB, -- Critères de récursivité, profondeur, etc.
  statut TEXT DEFAULT 'en_cours', -- en_cours, termine, erreur
  nb_entreprises_trouvees INTEGER DEFAULT 0,
  date_debut TIMESTAMP DEFAULT NOW(),
  date_fin TIMESTAMP,
  resume_final TEXT
);
```

---

## 🧪 Tests et Debugging

### Mode "FAKE" amélioré

* Chaque outil retourne des données simulées **avec variabilité réaliste**
* **Simulation de conflits de données** pour tester la validation
* **Simulation d'échecs d'API** pour tester les fallbacks
* Données avec scores de confiance variables

### Mode "TRACE" amélioré

* Activation d'une trace JSON de toutes les décisions, outputs intermédiaires
* **Dashboard web temps réel** pour visualiser l'exploration
* **Métriques de performance** par agent et par outil
* **Export des conflits détectés** pour analyse

### Mode "BENCHMARK"

* **Nouveau :** Comparaison de performance entre modèles LLM
* Métriques de qualité des résultats (précision, rappel)
* Temps d'exécution par composant

---

## 🔧 Stack technique recommandée

| Composant         | Techno                             |
| ----------------- | ---------------------------------- |
| Langage principal | Python 3.11                        |
| Framework agent   | Custom orchestrateur maison        |
| Stockage          | PostgreSQL 15+                     |
| Mémoire rapide    | Redis 7+ (pour cache et sessions)  |
| LLM access        | OpenAI, Anthropic, Mistral via API |
| Env. dev          | Cursor, Poetry, Pytest             |
| Graph             | NetworkX / Graphviz / D3.js        |
| Dashboard         | FastAPI + React (optionnel)        |
| Logging           | Loguru avec structured logging     |
| Monitoring        | Prometheus + Grafana (optionnel)   |
| Docker            | Docker compose                     |
| Queue             | Celery + Redis (pour async)        |

---

### Structure envisagée améliorée:
```
project-root/
│
├── docker-compose.yml
├── config/
│   ├── models.yaml
│   ├── recursion_criteria.yaml
│   └── cache_policy.yaml
├── orchestrator/
│   ├── main.py
│   ├── model_router.py
│   ├── orchestrator.py
│   ├── conflict_resolver.py          # Nouveau
│   ├── cache_manager.py              # Nouveau
│   └── agents/
│       ├── agent_master.py
│       ├── agent_normalization.py    # Nouveau
│       ├── agent_identification.py
│       ├── agent_webdata.py
│       ├── agent_inpi.py
│       ├── agent_capital.py
│       ├── agent_news.py
│       ├── agent_validation.py       # Nouveau
│       ├── agent_recursion.py
│       └── agent_synthese.py  
│
├── tools/
│   ├── tool_normalize_name.py        # Nouveau
│   ├── tool_match_enterprise.py      # Nouveau
│   ├── tool_ner_extraction.py        # Nouveau
│   ├── tool_identify_website.py
│   ├── tool_fetch_site_data.py
│   ├── tool_get_inpi_documents.py
│   ├── tool_parse_inpi_documents.py
│   ├── tool_extract_news.py
│   ├── tool_extract_links.py
│   ├── tool_validate_consistency.py  # Nouveau
│   ├── tool_resolve_conflicts.py     # Nouveau
│   ├── tool_prioritize_entities.py   # Nouveau
│   ├── tool_generate_report.py       # Nouveau
│   └── tool_store_pg.py
│
├── memory/
│   ├── memory_manager.py
│   ├── cache_manager.py              # Nouveau
│   └── graph_temp.py
│
├── validation/                       # Nouveau dossier
│   ├── data_validator.py
│   ├── conflict_detector.py
│   └── scoring_engine.py
│
├── monitoring/                       # Nouveau dossier
│   ├── metrics_collector.py
│   ├── dashboard_api.py
│   └── performance_tracker.py
│
├── db/
│   ├── init.sql
│   ├── migrations/
│   └── seeds/                        # Données de test
│
├── frontend/                         # Nouveau (optionnel)
│   ├── dashboard/
│   └── visualization/
│
└── tests/
    ├── test_fake_flows.py
    ├── test_conflict_resolution.py   # Nouveau
    ├── test_recursion_limits.py      # Nouveau
    └── test_performance.py           # Nouveau
```

## 📊 Métriques de Succès

**Quantitatives :**
- Temps moyen d'exploration : < 5 minutes pour profondeur 2
- Taux de succès d'identification : > 95%
- Précision des liens capitalistiques : > 90%
- Taux de conflits résolus automatiquement : > 80%

**Qualitatives :**
- Résumés cohérents et complets
- Détection proactive des incohérences
- Exploration intelligente sans explosion combinatoire
- Fallbacks gracieux en cas d'échec

---



## 🔧 Exemple d'architecture Technique Détaillée

### 1. Orchestrateur Custom - Design Patterns & Classes

#### Pattern Principal : **State Machine + Command Pattern**

```python
# orchestrator/core.py
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import asyncio
from celery import Celery

class ExecutionState(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class TaskContext:
    """Context partagé entre tous les agents"""
    session_id: str
    enterprise_name: str
    current_depth: int
    max_depth: int
    collected_data: Dict[str, Any]
    graph: 'TemporaryGraph'
    cache: 'CacheManager'
    config: Dict[str, Any]
    errors: List[str]
    metrics: Dict[str, float]

class AgentTask(ABC):
    """Interface pour toutes les tâches d'agents"""
    
    def __init__(self, task_id: str, priority: TaskPriority = TaskPriority.MEDIUM):
        self.task_id = task_id
        self.priority = priority
        self.state = ExecutionState.PENDING
        self.dependencies: List[str] = []
        self.result: Optional[Any] = None
        self.error: Optional[Exception] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    @abstractmethod
    async def execute(self, context: TaskContext) -> Any:
        """Exécute la tâche de manière asynchrone"""
        pass
    
    @abstractmethod
    def can_run(self, completed_tasks: List[str]) -> bool:
        """Vérifie si la tâche peut être exécutée"""
        pass
    
    def get_retry_count(self) -> int:
        return getattr(self, '_retry_count', 0)
    
    def increment_retry(self):
        self._retry_count = getattr(self, '_retry_count', 0) + 1

class OrchestrationEngine:
    """Moteur principal d'orchestration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.celery_app = Celery('agent_orchestrator')
        self.task_queue = asyncio.PriorityQueue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []
        self.max_concurrent_tasks = config.get('max_concurrent_tasks', 5)
        self.retry_policy = config.get('retry_policy', {
            'max_retries': 3,
            'delay': 1.0,
            'backoff_factor': 2.0
        })
    
    async def execute_session(self, enterprise_name: str, session_config: Dict[str, Any]) -> 'SessionResult':
        """Point d'entrée principal pour une session d'exploration"""
        context = await self._create_context(enterprise_name, session_config)
        
        # Création du pipeline de tâches
        tasks = await self._create_task_pipeline(context)
        
        # Exécution avec gestion des dépendances
        result = await self._execute_with_dependencies(tasks, context)
        
        return result
    
    async def _execute_with_dependencies(self, tasks: List[AgentTask], context: TaskContext) -> 'SessionResult':
        """Exécute les tâches en respectant les dépendances"""
        pending_tasks = {task.task_id: task for task in tasks}
        
        while pending_tasks or self.running_tasks:
            # Trouve les tâches prêtes à être exécutées
            ready_tasks = [
                task for task in pending_tasks.values()
                if task.can_run(self.completed_tasks) and len(self.running_tasks) < self.max_concurrent_tasks
            ]
            
            # Lance les tâches prêtes
            for task in ready_tasks:
                await self._execute_task_async(task, context)
                del pending_tasks[task.task_id]
            
            # Attend qu'au moins une tâche se termine
            if self.running_tasks:
                done, pending = await asyncio.wait(
                    self.running_tasks.values(),
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in done:
                    task_id = self._get_task_id_from_task(task)
                    await self._handle_task_completion(task_id, task, context)
            
            await asyncio.sleep(0.1)  # Évite la busy loop
        
        return await self._build_session_result(context)
    
    async def _execute_task_async(self, agent_task: AgentTask, context: TaskContext):
        """Exécute une tâche de manière asynchrone avec retry"""
        
        async def task_wrapper():
            for attempt in range(self.retry_policy['max_retries'] + 1):
                try:
                    agent_task.state = ExecutionState.RUNNING
                    agent_task.start_time = time.time()
                    
                    result = await agent_task.execute(context)
                    
                    agent_task.result = result
                    agent_task.state = ExecutionState.COMPLETED
                    agent_task.end_time = time.time()
                    
                    return result
                
                except Exception as e:
                    agent_task.error = e
                    agent_task.increment_retry()
                    
                    if attempt < self.retry_policy['max_retries']:
                        delay = self.retry_policy['delay'] * (self.retry_policy['backoff_factor'] ** attempt)
                        await asyncio.sleep(delay)
                    else:
                        agent_task.state = ExecutionState.FAILED
                        agent_task.end_time = time.time()
                        raise
        
        task = asyncio.create_task(task_wrapper())
        self.running_tasks[agent_task.task_id] = task
        return task
```

#### Queue Management avec Celery

```python
# orchestrator/queue_manager.py
from celery import Celery
from kombu import Queue, Exchange
from typing import Dict, Any, Optional

class QueueManager:
    """Gestionnaire des queues Celery pour les tâches lourdes"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.celery_app = Celery('agent_tasks')
        self.celery_app.conf.update(
            broker_url=redis_url,
            result_backend=redis_url,
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            task_routes={
                'agent_tasks.heavy_processing': {'queue': 'heavy'},
                'agent_tasks.llm_calls': {'queue': 'llm'},
                'agent_tasks.web_scraping': {'queue': 'web'},
                'agent_tasks.data_processing': {'queue': 'data'}
            }
        )
        
        # Définition des queues avec priorités
        self.celery_app.conf.task_queues = (
            Queue('heavy', Exchange('heavy'), routing_key='heavy',
                  queue_arguments={'x-max-priority': 10}),
            Queue('llm', Exchange('llm'), routing_key='llm',
                  queue_arguments={'x-max-priority': 8}),
            Queue('web', Exchange('web'), routing_key='web',
                  queue_arguments={'x-max-priority': 6}),
            Queue('data', Exchange('data'), routing_key='data',
                  queue_arguments={'x-max-priority': 4}),
        )
    
    @celery_app.task(bind=True, name='agent_tasks.llm_processing')
    def process_with_llm(self, agent_name: str, input_data: Dict[str, Any], model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Tâche Celery pour les appels LLM"""
        from agents.base import create_agent
        
        agent = create_agent(agent_name, model_config)
        result = agent.process_sync(input_data)
        
        return {
            'agent': agent_name,
            'result': result,
            'execution_time': time.time() - self.request.started,
            'model_used': model_config.get('model', 'unknown')
        }
    
    @celery_app.task(bind=True, name='agent_tasks.heavy_processing')
    def process_heavy_task(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tâche Celery pour les traitements lourds"""
        from tools.factory import create_tool
        
        tool = create_tool(tool_name)
        result = tool.run(input_data)
        
        return {
            'tool': tool_name,
            'result': result,
            'execution_time': time.time() - self.request.started
        }
```

### 2. Gestion Synchrone vs Asynchrone

#### Stratégie Hybride

```python
# orchestrator/execution_strategy.py
import asyncio
from typing import List, Dict, Any, Union, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

class ExecutionStrategy:
    """Détermine la stratégie d'exécution optimale"""
    
    ASYNC_TASKS = {
        'web_scraping', 'api_calls', 'database_queries', 'file_io'
    }
    
    SYNC_HEAVY_TASKS = {
        'pdf_parsing', 'nlp_processing', 'image_processing'
    }
    
    PARALLEL_TASKS = {
        'data_validation', 'entity_extraction', 'conflict_resolution'
    }
    
    def __init__(self, max_workers: int = 4):
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers)
    
    async def execute_optimal(self, task_type: str, func: Callable, *args, **kwargs) -> Any:
        """Exécute la fonction avec la stratégie optimale"""
        
        if task_type in self.ASYNC_TASKS:
            # Exécution asynchrone native
            return await func(*args, **kwargs)
            
        elif task_type in self.SYNC_HEAVY_TASKS:
            # Exécution dans un processus séparé
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.process_pool, func, *args
            )
            
        elif task_type in self.PARALLEL_TASKS:
            # Exécution dans un thread séparé
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.thread_pool, func, *args
            )
            
        else:
            # Exécution synchrone par défaut
            return func(*args, **kwargs)

# Exemple d'utilisation dans un agent
class AgentINPI(BaseAgent):
    
    async def execute(self, context: TaskContext) -> Dict[str, Any]:
        strategy = ExecutionStrategy()
        
        # Récupération des documents (I/O intensif -> async)
        documents = await strategy.execute_optimal(
            'api_calls',
            self._fetch_inpi_documents,
            context.enterprise_name
        )
        
        # Parsing des PDFs (CPU intensif -> process)
        parsed_data = await strategy.execute_optimal(
            'pdf_parsing',
            self._parse_documents_heavy,
            documents
        )
        
        # Extraction d'entités (parallélisable -> thread)
        entities = await strategy.execute_optimal(
            'entity_extraction',
            self._extract_entities,
            parsed_data
        )
        
        return {
            'documents': documents,
            'parsed_data': parsed_data,
            'entities': entities
        }
```

### 3. Classes et Interfaces Détaillées

#### Base Classes pour Agents

```python
# agents/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
from enum import Enum

class AgentState(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AgentResult:
    """Résultat standardisé d'un agent"""
    agent_name: str
    success: bool
    data: Dict[str, Any]
    confidence_score: float
    execution_time: float
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]

class BaseAgent(ABC):
    """Classe de base pour tous les agents"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.state = AgentState.IDLE
        self.logger = logging.getLogger(f"agent.{name}")
        self.memory = {}
        self.tools = []
        self.llm_client = None
        
    @abstractmethod
    async def execute(self, context: TaskContext) -> AgentResult:
        """Méthode principale d'exécution"""
        pass
    
    @abstractmethod
    def validate_input(self, context: TaskContext) -> bool:
        """Valide les données d'entrée"""
        pass
    
    async def pre_execute(self, context: TaskContext):
        """Préparation avant exécution"""
        self.state = AgentState.PROCESSING
        self.logger.info(f"Starting execution for {context.enterprise_name}")
    
    async def post_execute(self, result: AgentResult, context: TaskContext):
        """Nettoyage après exécution"""
        self.state = AgentState.COMPLETED if result.success else AgentState.ERROR
        
        # Mise à jour du contexte
        context.collected_data[self.name] = result.data
        context.metrics[f"{self.name}_confidence"] = result.confidence_score
        context.metrics[f"{self.name}_execution_time"] = result.execution_time
        
        # Logging
        self.logger.info(f"Completed execution: success={result.success}, confidence={result.confidence_score}")

class DataValidationMixin:
    """Mixin pour validation des données"""
    
    def validate_data_consistency(self, data: Dict[str, Any]) -> List[str]:
        """Valide la cohérence des données"""
        errors = []
        
        # Validation des champs obligatoires
        required_fields = getattr(self, 'REQUIRED_FIELDS', [])
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validation des types
        field_types = getattr(self, 'FIELD_TYPES', {})
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                errors.append(f"Invalid type for {field}: expected {expected_type}, got {type(data[field])}")
        
        return errors

class CacheableMixin:
    """Mixin pour gestion du cache"""
    
    def get_cache_key(self, context: TaskContext) -> str:
        """Génère une clé de cache"""
        return f"{self.name}:{context.enterprise_name}:{hash(str(context.config))}"
    
    async def get_cached_result(self, context: TaskContext) -> Optional[AgentResult]:
        """Récupère un résultat depuis le cache"""
        cache_key = self.get_cache_key(context)
        return await context.cache.get(cache_key)
    
    async def cache_result(self, result: AgentResult, context: TaskContext):
        """Met en cache un résultat"""
        cache_key = self.get_cache_key(context)
        ttl = self.config.get('cache_ttl', 3600)
        await context.cache.set(cache_key, result, ttl)
```

#### Implémentation Concrète d'Agents

```python
# agents/agent_normalization.py
from typing import Dict, Any, List
from .base import BaseAgent, AgentResult, DataValidationMixin
from tools.factory import create_tool

class AgentNormalization(BaseAgent, DataValidationMixin):
    """Agent de normalisation des noms d'entreprises"""
    
    REQUIRED_FIELDS = ['enterprise_name']
    FIELD_TYPES = {'enterprise_name': str}
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__('normalization', config)
        self.normalize_tool = create_tool('normalize_name')
        self.match_tool = create_tool('match_enterprise')
        self.ner_tool = create_tool('ner_extraction')
    
    async def execute(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            await self.pre_execute(context)
            
            # Validation des entrées
            if not self.validate_input(context):
                raise ValueError("Invalid input data")
            
            # Normalisation du nom
            normalized_result = await self.normalize_tool.run_async({
                'raw_name': context.enterprise_name
            })
            
            # Matching avec base de données
            match_result = await self.match_tool.run_async({
                'name_variants': normalized_result['variants']
            })
            
            # Extraction d'entités nommées
            ner_result = await self.ner_tool.run_async({
                'text': context.enterprise_name
            })
            
            # Consolidation des résultats
            consolidated_data = {
                'original_name': context.enterprise_name,
                'normalized_name': normalized_result['normalized'],
                'variants': normalized_result['variants'],
                'matched_entities': match_result['matches'],
                'siren': match_result.get('best_match', {}).get('siren'),
                'confidence_score': match_result.get('confidence', 0.0),
                'named_entities': ner_result['entities']
            }
            
            # Validation des données
            validation_errors = self.validate_data_consistency(consolidated_data)
            if validation_errors:
                errors.extend(validation_errors)
            
            execution_time = time.time() - start_time
            
            result = AgentResult(
                agent_name=self.name,
                success=len(errors) == 0,
                data=consolidated_data,
                confidence_score=consolidated_data['confidence_score'],
                execution_time=execution_time,
                errors=errors,
                warnings=warnings,
                metadata={
                    'variants_found': len(normalized_result['variants']),
                    'matches_found': len(match_result['matches']),
                    'entities_extracted': len(ner_result['entities'])
                }
            )
            
            await self.post_execute(result, context)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            errors.append(str(e))
            
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={},
                confidence_score=0.0,
                execution_time=execution_time,
                errors=errors,
                warnings=warnings,
                metadata={}
            )
    
    def validate_input(self, context: TaskContext) -> bool:
        if not context.enterprise_name or not context.enterprise_name.strip():
            return False
        return True
```

### 4. Gestion des États et Transitions

```python
# orchestrator/state_manager.py
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import asyncio

class SessionState(Enum):
    INITIALIZING = "initializing"
    NORMALIZING = "normalizing"
    IDENTIFYING = "identifying"
    COLLECTING = "collecting"
    VALIDATING = "validating"
    RECURSING = "recursing"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class StateTransition:
    from_state: SessionState
    to_state: SessionState
    condition: Callable[[TaskContext], bool]
    action: Optional[Callable[[TaskContext], Any]] = None

class StateManager:
    """Gestionnaire d'états pour les sessions d'exploration"""
    
    def __init__(self):
        self.transitions: List[StateTransition] = []
        self._setup_transitions()
    
    def _setup_transitions(self):
        """Définit les transitions d'états autorisées"""
        self.transitions = [
            StateTransition(
                SessionState.INITIALIZING,
                SessionState.NORMALIZING,
                lambda ctx: ctx.enterprise_name is not None
            ),
            StateTransition(
                SessionState.NORMALIZING,
                SessionState.IDENTIFYING,
                lambda ctx: 'normalization' in ctx.collected_data and ctx.collected_data['normalization'].get('normalized_name')
            ),
            StateTransition(
                SessionState.IDENTIFYING,
                SessionState.COLLECTING,
                lambda ctx: 'identification' in ctx.collected_data and ctx.collected_data['identification'].get('siren')
            ),
            StateTransition(
                SessionState.COLLECTING,
                SessionState.VALIDATING,
                lambda ctx: len(ctx.collected_data) >= 3  # Au moins 3 agents ont collecté des données
            ),
            StateTransition(
                SessionState.VALIDATING,
                SessionState.RECURSING,
                lambda ctx: (
                    'validation' in ctx.collected_data and
                    ctx.current_depth < ctx.max_depth and
                    len(ctx.collected_data.get('validation', {}).get('linked_entities', [])) > 0
                )
            ),
            StateTransition(
                SessionState.VALIDATING,
                SessionState.SYNTHESIZING,
                lambda ctx: (
                    ctx.current_depth >= ctx.max_depth or
                    len(ctx.collected_data.get('validation', {}).get('linked_entities', [])) == 0
                )
            ),
            StateTransition(
                SessionState.RECURSING,
                SessionState.COLLECTING,
                lambda ctx: True  # Retour à la collecte pour les entités liées
            ),
            StateTransition(
                SessionState.SYNTHESIZING,
                SessionState.COMPLETED,
                lambda ctx: 'synthesis' in ctx.collected_data
            )
        ]
    
    def get_next_state(self, current_state: SessionState, context: TaskContext) -> Optional[SessionState]:
        """Détermine l'état suivant basé sur les conditions"""
        for transition in self.transitions:
            if transition.from_state == current_state and transition.condition(context):
                if transition.action:
                    transition.action(context)
                return transition.to_state
        return None
    
    def can_transition(self, from_state: SessionState, to_state: SessionState, context: TaskContext) -> bool:
        """Vérifie si une transition est autorisée"""
        for transition in self.transitions:
            if transition.from_state == from_state and transition.to_state == to_state:
                return transition.condition(context)
        return False
```

### 5. Monitoring et Métriques

```python
# monitoring/metrics_collector.py
from typing import Dict, Any, List
from dataclasses import dataclass, field
import time
import psutil
import asyncio
from prometheus_client import Counter, Histogram, Gauge

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    timestamp: float = field(default_factory=time.time)

@dataclass
class AgentMetrics:
    agent_name: str
    execution_count: int
    success_rate: float
    avg_execution_time: float
    confidence_scores: List[float]
    error_count: int
    cache_hit_rate: float

class MetricsCollector:
    """Collecteur de métriques pour monitoring"""
    
    def __init__(self):
        # Métriques Prometheus
        self.agent_executions = Counter('agent_executions_total', 'Total agent executions', ['agent_name', 'status'])
        self.execution_duration = Histogram('agent_execution_duration_seconds', 'Agent execution duration', ['agent_name'])
        self.confidence_scores = Histogram('agent_confidence_scores', 'Agent confidence scores', ['agent_name'])
        self.system_resources = Gauge('system_resources', 'System resource usage', ['resource_type'])
        
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.system_metrics: List[SystemMetrics] = []
        
    async def collect_agent_metrics(self, agent_name: str, result: AgentResult):
        """Collecte les métriques d'un agent"""
        # Prometheus metrics
        status = 'success' if result.success else 'error'
        self.agent_executions.labels(agent_name=agent_name, status=status).inc()
        self.execution_duration.labels(agent_name=agent_name).observe(result.execution_time)
        self.confidence_scores.labels(agent_name=agent_name).observe(result.confidence_score)
        
        # Métriques internes
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentMetrics(
                agent_name=agent_name,
                execution_count=0,
                success_rate=0.0,
                avg_execution_time=0.0,
                confidence_scores=[],
                error_count=0,
                cache_hit_rate=0.0
            )
        
        metrics = self.agent_metrics[agent_name]
        metrics.execution_count += 1
        metrics.confidence_scores.append(result.confidence_score)
        
        if not result.success:
            metrics.error_count += 1
        
        # Recalculer les moyennes
        metrics.success_rate = (metrics.execution_count - metrics.error_count) / metrics.execution_count
        metrics.avg_execution_time = (
            (metrics.avg_execution_time * (metrics.execution_count - 1) + result.execution_time) / 
            metrics.execution_count
        )
    
    async def collect_system_metrics(self):
        """Collecte les métriques système"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        system_metrics = SystemMetrics(
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_io={
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            }
        )
        
        self.system_metrics.append(system_metrics)
        
        # Prometheus metrics
        self.system_resources.labels(resource_type='cpu').set(cpu_percent)
        self.system_resources.labels(resource_type='memory').set(memory.percent)
        self.system_resources.labels(resource_type='disk').set(disk.percent)
        
        # Garder seulement les 1000 dernières mesures
        if len(self.system_metrics) > 1000:
            self.system_metrics = self.system_metrics[-1000:]
    
    def get_summary_report(self) -> Dict[str, Any]:
        """Génère un rapport de synthèse"""
        return {
            'agents': {
                name: {
                    'execution_count': metrics.execution_count,
                    'success_rate': metrics.success_rate,
                    'avg_execution_time': metrics.avg_execution_time,
                    'avg_confidence': sum(metrics.confidence_scores) / len(metrics.confidence_scores) if metrics.confidence_scores else 0.0,
                    'error_count': metrics.error_count
                }
                for name, metrics in self.agent_metrics.items()
            },
            'system': {
                'current_cpu': self.system_metrics[-1].cpu_usage if self.system_metrics else 0.0,
                'current_memory': self.system_metrics[-1].memory_usage if self.system_metrics else 0.0,
                'current_disk': self.system_metrics[-1].disk_usage if self.system_metrics else 0.0
            },
            'timestamp': time.time()
        }
```




## 🪜 Étapes de développement

### Phase 1 – Base agent + outils fake + validation

* [ ] Implémentation de l'orchestrateur avec gestion d'erreurs
* [ ] **AgentNormalization avec outils de matching**
* [ ] Implémentation des agents avec modules d'outils factices
* [ ] **Système de validation et résolution de conflits**
* [ ] Structure du graph mémoire local avec scoring
* [ ] Connecteurs PostgreSQL avec nouveau schéma
* [ ] **Système de cache Redis**

### Phase 2 – Mémoire, récursivité intelligente, profondeur

* [ ] Ajout mémoire locale/long terme par agent
* [ ] **Critères d'arrêt intelligents avec scoring de pertinence**
* [ ] Limiteur de profondeur + prévention des doublons
* [ ] **Priorisation automatique des entités**
* [ ] Ajout d'un cache LRU avec TTL configurable

### Phase 3 – Interopérabilité LLM et monitoring

* [ ] Module `model_router.py` avec fallbacks
* [ ] **Dashboard de monitoring en temps réel**
* [ ] Bench simple entre 3 modèles sur 5 tâches
* [ ] **Métriques de qualité et performance**
* [ ] Tests de raisonnement + logs de décision

### Phase 4 – Tests bout en bout et optimisation

* [ ] Tests sur cas d'entreprises fictives avec conflits
* [ ] **Tests de charge et limites de récursivité**
* [ ] Exports JSON / visualisation Graph avancée
* [ ] **Optimisation des performances**
* [ ] Définition API REST (si besoin plus tard)

### Phase 5 – Production ready (optionnel)

* [ ] Interface web pour configuration
* [ ] Système d'alertes et notifications
* [ ] Backup automatique et restauration
* [ ] Documentation utilisateur complète

---