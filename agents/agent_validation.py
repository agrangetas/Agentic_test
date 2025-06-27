"""
Agent de validation et résolution de conflits.

Valide la cohérence des données collectées entre différentes sources
et résout automatiquement les conflits détectés.
"""

import time
from typing import Dict, Any, List, Tuple
from .base import FullFeaturedAgent, AgentResult


class AgentValidation(FullFeaturedAgent):
    """Agent de validation et résolution de conflits entre sources."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__('validation', config)
    
    def validate_input(self, context: 'TaskContext') -> bool:
        """Valide les données d'entrée."""
        # Besoin d'au moins 2 sources de données pour valider
        return len(context.collected_data) >= 2
    
    async def execute(self, context: 'TaskContext') -> AgentResult:
        """Exécute la validation des données collectées."""
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            await self.pre_execute(context)
            
            if not self.validate_input(context):
                raise ValueError("Need at least 2 data sources to validate")
            
            # 1. Détection des conflits entre sources
            conflicts = await self._detect_conflicts_fake(context.collected_data)
            
            # 2. Résolution automatique des conflits
            resolved_conflicts = await self._resolve_conflicts_fake(conflicts)
            
            # 3. Calcul du score de cohérence global
            consistency_score = await self._calculate_consistency_score(
                context.collected_data, conflicts, resolved_conflicts
            )
            
            # 4. Identification des entités liées pour récursion
            linked_entities = await self._identify_linked_entities_fake(context.collected_data)
            
            # Données de validation consolidées
            validation_data = {
                'conflicts_detected': conflicts,
                'conflicts_resolved': resolved_conflicts,
                'consistency_score': consistency_score,
                'data_quality_score': self._calculate_quality_score(context.collected_data),
                'linked_entities': linked_entities,
                'validation_summary': self._generate_validation_summary(conflicts, resolved_conflicts),
                'recommendations': self._generate_recommendations(conflicts, consistency_score)
            }
            
            execution_time = time.time() - start_time
            
            result = AgentResult(
                agent_name=self.name,
                success=True,
                data=validation_data,
                confidence_score=consistency_score,
                execution_time=execution_time,
                errors=errors,
                warnings=warnings,
                metadata={
                    'conflicts_found': len(conflicts),
                    'conflicts_resolved': len(resolved_conflicts),
                    'linked_entities_found': len(linked_entities),
                    'mode': 'fake_testing'
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
                metadata={'mode': 'fake_testing_error'}
            )
    
    async def _detect_conflicts_fake(self, collected_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Détecte les conflits entre sources de données (VERSION FAKE)."""
        conflicts = []
        
        # Vérification des conflits sur le SIREN
        sirens = {}
        for source, data in collected_data.items():
            if isinstance(data, dict) and 'siren' in data:
                siren = data['siren']
                if siren:
                    if siren in sirens:
                        if sirens[siren] != source:
                            conflicts.append({
                                'type': 'siren_mismatch',
                                'field': 'siren',
                                'value1': siren,
                                'source1': sirens[siren],
                                'value2': siren,
                                'source2': source,
                                'severity': 'low'  # Même valeur, sources différentes
                            })
                    else:
                        sirens[siren] = source
        
        # Simulation de conflits sur le nom
        names = {}
        for source, data in collected_data.items():
            if isinstance(data, dict) and 'normalized_name' in data:
                name = data['normalized_name']
                if name:
                    if name in names and names[name] != source:
                        # Pas vraiment un conflit si même nom
                        pass
                    else:
                        names[name] = source
        
        # Simulation de conflit d'URL (exemple)
        if 'normalization' in collected_data and 'identification' in collected_data:
            norm_data = collected_data['normalization']
            id_data = collected_data['identification']
            
            if (isinstance(norm_data, dict) and isinstance(id_data, dict) and
                norm_data.get('confidence_score', 0) < 0.7 and id_data.get('confidence_score', 0) < 0.7):
                conflicts.append({
                    'type': 'low_confidence',
                    'field': 'confidence',
                    'value1': norm_data.get('confidence_score', 0),
                    'source1': 'normalization',
                    'value2': id_data.get('confidence_score', 0),
                    'source2': 'identification',
                    'severity': 'medium'
                })
        
        return conflicts
    
    async def _resolve_conflicts_fake(self, conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Résout automatiquement les conflits (VERSION FAKE)."""
        resolved = []
        
        for conflict in conflicts:
            resolution = {
                'conflict_id': conflict.get('type', 'unknown'),
                'resolution_method': 'fake_auto_resolution',
                'resolved_value': None,
                'confidence': 0.8
            }
            
            if conflict['type'] == 'siren_mismatch':
                # Pour un mismatch de SIREN identique, on garde la première source
                resolution['resolved_value'] = conflict['value1']
                resolution['resolution_method'] = 'keep_first_source'
                
            elif conflict['type'] == 'low_confidence':
                # Pour une faible confiance, on fait une moyenne
                avg_confidence = (conflict['value1'] + conflict['value2']) / 2
                resolution['resolved_value'] = avg_confidence
                resolution['resolution_method'] = 'average_confidence'
            
            resolved.append(resolution)
        
        return resolved
    
    async def _calculate_consistency_score(self, collected_data: Dict[str, Any], 
                                         conflicts: List[Dict[str, Any]], 
                                         resolved: List[Dict[str, Any]]) -> float:
        """Calcule un score de cohérence global."""
        if not collected_data:
            return 0.0
        
        # Score de base selon le nombre de sources
        base_score = min(0.8, len(collected_data) * 0.2)
        
        # Pénalité pour les conflits
        conflict_penalty = len(conflicts) * 0.1
        
        # Bonus pour les résolutions
        resolution_bonus = len(resolved) * 0.05
        
        final_score = max(0.0, min(1.0, base_score - conflict_penalty + resolution_bonus))
        return final_score
    
    def _calculate_quality_score(self, collected_data: Dict[str, Any]) -> float:
        """Calcule un score de qualité des données."""
        if not collected_data:
            return 0.0
        
        total_confidence = 0.0
        count = 0
        
        for source, data in collected_data.items():
            if isinstance(data, dict) and 'confidence_score' in data:
                total_confidence += data['confidence_score']
                count += 1
        
        return total_confidence / count if count > 0 else 0.5
    
    async def _identify_linked_entities_fake(self, collected_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifie les entités liées pour récursion (VERSION FAKE)."""
        linked_entities = []
        
        # Simulation d'entités liées basée sur les données collectées
        enterprise_name = ""
        for source, data in collected_data.items():
            if isinstance(data, dict) and 'original_name' in data:
                enterprise_name = data['original_name']
                break
        
        if "LVMH" in enterprise_name.upper():
            linked_entities.extend([
                {
                    'name': 'Louis Vuitton',
                    'type': 'subsidiary',
                    'participation': 100.0,
                    'priority': 'high',
                    'siren': '421048806'
                },
                {
                    'name': 'Moët & Chandon',
                    'type': 'subsidiary', 
                    'participation': 100.0,
                    'priority': 'high',
                    'siren': '391478688'
                },
                {
                    'name': 'Hennessy',
                    'type': 'subsidiary',
                    'participation': 100.0,
                    'priority': 'medium',
                    'siren': '572174171'
                }
            ])
        elif "GOOGLE" in enterprise_name.upper():
            linked_entities.append({
                'name': 'Alphabet Inc',
                'type': 'parent',
                'participation': 100.0,
                'priority': 'high',
                'siren': 'US_COMPANY'
            })
        
        return linked_entities
    
    def _generate_validation_summary(self, conflicts: List[Dict[str, Any]], 
                                   resolved: List[Dict[str, Any]]) -> str:
        """Génère un résumé de la validation."""
        summary = f"Validation terminée. "
        summary += f"Conflits détectés: {len(conflicts)}. "
        summary += f"Conflits résolus: {len(resolved)}. "
        
        if len(conflicts) == 0:
            summary += "Aucun conflit détecté, données cohérentes."
        elif len(resolved) == len(conflicts):
            summary += "Tous les conflits ont été résolus automatiquement."
        else:
            summary += f"{len(conflicts) - len(resolved)} conflits nécessitent une attention manuelle."
        
        return summary
    
    def _generate_recommendations(self, conflicts: List[Dict[str, Any]], 
                                consistency_score: float) -> List[str]:
        """Génère des recommandations d'amélioration."""
        recommendations = []
        
        if consistency_score < 0.5:
            recommendations.append("Score de cohérence faible - vérifier la qualité des sources")
        
        if len(conflicts) > 3:
            recommendations.append("Nombreux conflits détectés - revoir la stratégie de collecte")
        
        for conflict in conflicts:
            if conflict.get('severity') == 'high':
                recommendations.append(f"Résoudre manuellement le conflit {conflict['type']}")
        
        if not recommendations:
            recommendations.append("Données de bonne qualité, aucune action requise")
        
        return recommendations 