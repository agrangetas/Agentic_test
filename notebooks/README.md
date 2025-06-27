# 📓 Notebooks Jupyter - Agent Company

Ce dossier contient les notebooks Jupyter pour tester et développer interactivement le système Agent Company.

## 🚀 Démarrage Rapide

### 1. Accès au Jupyter Lab
```bash
# Le service Jupyter est accessible sur :
http://localhost:8888

# Token d'accès : agent_token_2024
```

### 2. Notebook Principal : `01_Test_System.ipynb`

Ce notebook **complet** permet de tester tous les composants du système de manière interactive et approfondie.

## 📋 Contenu du Notebook Principal

### 🏗️ **1. Tests d'Infrastructure**
- ✅ **Connexions Redis et PostgreSQL** : Vérification des connexions, latence, opérations CRUD
- ✅ **Gestionnaire de cache avancé** : Tests de performance, TTL, invalidation par catégorie
- ✅ **Système de logging** : Logs par agent, rotation quotidienne, métriques détaillées
- ✅ **Gestionnaire de base de données** : Transactions, requêtes complexes, gestion d'erreurs
- ✅ **Test d'intégration infrastructure** : Workflow complet entre tous les composants

### 🔧 **2. Tests des Outils (Tools)**
- ✅ **Normalisation de noms** : Nettoyage, variantes, scoring de confiance
- ✅ **Matching d'entreprises** : Recherche floue, SIREN, correspondances multiples
- ✅ **Extraction NER** : Entités nommées, entreprises, personnes, lieux
- ✅ **Identification de sites web** : URLs, validation, statuts de réponse
- ✅ **Validation de cohérence** : Détection de conflits entre sources
- ✅ **Résolution de conflits** : Algorithmes de résolution automatique
- ✅ **Tests de performance** : Opérations parallèles, gestion d'erreurs

### 🤖 **3. Tests des Agents**
- ✅ **Agent Normalization** : Tests détaillés avec validation, cache, métriques
- ✅ **Agent Identification** : Recherche SIREN, URL, vérification croisée
- ✅ **Agent Validation** : Détection/résolution de conflits, scores de qualité
- ✅ **Tests d'intégration** : Workflow séquentiel entre agents
- ✅ **Tests de performance** : Traitement de multiples entreprises
- ✅ **Gestion du cache** : Hit/miss rates, invalidation par agent

### 🎯 **4. Tests de l'Orchestrateur**
- ✅ **Initialisation et configuration** : Paramètres, modèles, critères de récursivité
- ✅ **Création de sessions** : Contextes, états, transitions
- ✅ **Gestion d'erreurs** : Fallbacks, retry, timeout
- ✅ **Métriques et monitoring** : Temps d'exécution, succès/échecs
- ✅ **Tests de charge** : Sessions multiples, concurrence

### 🔗 **5. Tests d'Intégration Complète**
- ✅ **Workflow bout en bout** : Du nom d'entreprise au résultat final
- ✅ **Cohérence des données** : Validation croisée entre composants
- ✅ **Performance globale** : Temps de réponse, throughput
- ✅ **Rapports détaillés** : Métriques, statistiques, recommandations

### 🎮 **6. Tests Interactifs Personnalisés**
- ✅ **Test entreprise unique** : Nom personnalisable, mode détaillé
- ✅ **Test multi-entreprises** : Liste personnalisable, statistiques
- ✅ **Test workflow orchestrateur** : Session complète via orchestrateur
- ✅ **Test performance cache** : Benchmarks lecture/écriture

## 🛠️ Scripts de Test Spécialisés

Le notebook utilise des **scripts de test spécialisés** pour chaque composant :

### `test_infrastructure.py`
```bash
python /app/test_scripts/test_infrastructure.py
```
- Tests Redis, PostgreSQL, Cache, Logging
- Tests d'intégration infrastructure
- Métriques de performance

### `test_tools_comprehensive.py`
```bash
python /app/test_scripts/test_tools_comprehensive.py
```
- Tests de tous les outils (6 principaux)
- Tests asynchrones et gestion d'erreurs
- Benchmarks de performance

### `test_agents_detailed.py`
```bash
python /app/test_scripts/test_agents_detailed.py
```
- Tests détaillés des 3 agents
- Tests d'intégration entre agents
- Tests de performance sur plusieurs entreprises

### `test_orchestrator.py`
```bash
python /app/test_scripts/test_orchestrator.py
```
- Tests complets de l'orchestrateur
- Gestion de sessions et contextes
- Tests de charge et métriques

### `test_interactive.py`
```bash
# Test entreprise unique
python /app/test_scripts/test_interactive.py single "Apple Inc" detailed

# Test multi-entreprises
python /app/test_scripts/test_interactive.py multiple "Apple,Microsoft,Google"

# Test orchestrateur
python /app/test_scripts/test_interactive.py orchestrator "Tesla Inc"

# Test performance cache
python /app/test_scripts/test_interactive.py cache
```

## 📊 Rapports et Métriques

Le notebook génère des **rapports détaillés** incluant :

- **Statistiques globales** : Taux de réussite, temps d'exécution
- **Métriques par composant** : Performance, erreurs, confiance
- **Recommandations** : Actions à prendre selon les résultats
- **Logs détaillés** : Disponibles dans `/app/logs/`

## 🎯 Utilisation Recommandée

### 1. **Tests de Développement**
- Exécutez le notebook complet pour valider vos modifications
- Utilisez les tests interactifs pour des cas spécifiques
- Consultez les logs détaillés pour le debugging

### 2. **Tests de Validation**
- Lancez tous les tests avant un déploiement
- Vérifiez que le taux de réussite est > 90%
- Analysez les métriques de performance

### 3. **Tests de Production**
- Utilisez les tests interactifs avec de vraies entreprises
- Monitorez les performances et la cohérence des données
- Ajustez les configurations selon les résultats

## 🔧 Configuration

### Variables Personnalisables dans le Notebook :

```python
# Tests interactifs
company_to_test = "Apple Inc"          # Entreprise à tester
detailed_mode = True                   # Mode détaillé
companies_to_test = ["Apple", "Google"] # Liste d'entreprises
orchestrator_company = "Amazon Inc"    # Test orchestrateur
```

### Paramètres Avancés :

```python
# Timeout des scripts
timeout = 300  # 5 minutes max par script

# Configuration cache
redis_db = 1  # Base Redis pour tests

# Mode détaillé
detailed_logs = True  # Logs verbeux
```

## 🚨 Troubleshooting

### Problèmes Courants :

1. **Timeout des tests** : Augmentez le timeout dans `run_test_script()`
2. **Erreurs Redis** : Vérifiez que le service Redis est démarré
3. **Erreurs PostgreSQL** : Vérifiez les paramètres de connexion
4. **Import errors** : Vérifiez que tous les modules sont installés

### Logs de Debug :
```python
# Consultez les logs détaillés
!ls -la /app/logs/
!tail -f /app/logs/app_$(date +%Y-%m-%d).log
```

## 🎉 Fonctionnalités Avancées

- **Tests parallèles** : Plusieurs agents en simultané
- **Métriques temps réel** : Performance monitoring
- **Cache intelligent** : Optimisation des performances
- **Gestion d'erreurs** : Fallbacks et retry automatiques
- **Rapports visuels** : Statistiques et graphiques
- **Tests de charge** : Simulation de charge élevée

---

**🎯 Objectif :** Ce notebook vous permet de tester, valider et optimiser tous les aspects du système Agent Company de manière interactive et complète. 