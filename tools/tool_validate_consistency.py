#!/usr/bin/env python3
"""
Outil de validation de cohérence des données.
"""

import time
from typing import Dict, Any, List


class ToolValidateConsistency:
    """Outil pour valider la cohérence des données entre sources."""
    
    def __init__(self):
        self.name = "validate_consistency"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide la cohérence des données entre sources.
        
        Args:
            input_data: Dict avec 'data_sources'
            
        Returns:
            Dict avec conflicts, is_consistent, quality_score
        """
        start_time = time.time()
        
        try:
            data_sources = input_data.get('data_sources', {})
            
            if len(data_sources) < 2:
                return {
                    'conflicts': [],
                    'is_consistent': True,
                    'quality_score': 0.5,
                    'execution_time': time.time() - start_time,
                    'error': 'Besoin d\'au moins 2 sources pour validation'
                }
            
            # Détection des conflits
            conflicts = self._detect_conflicts(data_sources)
            
            # Évaluation de la cohérence
            is_consistent = len(conflicts) == 0
            
            # Score de qualité
            quality_score = self._calculate_quality_score(data_sources, conflicts)
            
            return {
                'conflicts': conflicts,
                'is_consistent': is_consistent,
                'quality_score': quality_score,
                'execution_time': time.time() - start_time,
                'sources_count': len(data_sources)
            }
            
        except Exception as e:
            return {
                'conflicts': [],
                'is_consistent': False,
                'quality_score': 0.0,
                'execution_time': time.time() - start_time,
                'error': str(e)
            }
    
    def _detect_conflicts(self, data_sources: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Détecte les conflits entre sources de données."""
        conflicts = []
        source_names = list(data_sources.keys())
        
        # Comparaison de tous les champs entre toutes les sources
        for i, source1_name in enumerate(source_names):
            for j, source2_name in enumerate(source_names[i+1:], i+1):
                source1 = data_sources[source1_name]
                source2 = data_sources[source2_name]
                
                # Vérification des champs communs
                common_fields = set(source1.keys()).intersection(set(source2.keys()))
                
                for field in common_fields:
                    value1 = source1[field]
                    value2 = source2[field]
                    
                    if not self._values_are_consistent(value1, value2, field):
                        conflicts.append({
                            'field': field,
                            'source1': source1_name,
                            'value1': value1,
                            'source2': source2_name,
                            'value2': value2,
                            'severity': self._get_conflict_severity(field)
                        })
        
        return conflicts
    
    def _values_are_consistent(self, value1: Any, value2: Any, field: str) -> bool:
        """Vérifie si deux valeurs sont cohérentes."""
        if value1 == value2:
            return True
        
        # Cas spéciaux selon le type de champ
        if field == 'name':
            # Normalisation pour comparaison de noms
            norm1 = str(value1).upper().strip()
            norm2 = str(value2).upper().strip()
            return norm1 == norm2
        
        elif field == 'url':
            # Normalisation pour URLs
            url1 = str(value1).lower().strip().rstrip('/')
            url2 = str(value2).lower().strip().rstrip('/')
            # Accepter avec ou sans www
            url1_clean = url1.replace('www.', '')
            url2_clean = url2.replace('www.', '')
            return url1_clean == url2_clean
        
        elif field == 'siren':
            # SIREN doit être exactement identique
            return str(value1).strip() == str(value2).strip()
        
        else:
            # Comparaison générale
            return str(value1).strip() == str(value2).strip()
    
    def _get_conflict_severity(self, field: str) -> str:
        """Détermine la sévérité d'un conflit selon le champ."""
        critical_fields = ['siren', 'id']
        important_fields = ['name', 'url']
        
        if field in critical_fields:
            return 'critical'
        elif field in important_fields:
            return 'important'
        else:
            return 'minor'
    
    def _calculate_quality_score(self, data_sources: Dict[str, Dict[str, Any]], 
                                conflicts: List[Dict[str, Any]]) -> float:
        """Calcule un score de qualité des données."""
        if not data_sources:
            return 0.0
        
        # Score de base selon le nombre de sources
        base_score = min(len(data_sources) / 3, 1.0) * 0.3
        
        # Pénalité pour les conflits
        conflict_penalty = 0
        for conflict in conflicts:
            severity = conflict.get('severity', 'minor')
            if severity == 'critical':
                conflict_penalty += 0.3
            elif severity == 'important':
                conflict_penalty += 0.2
            else:
                conflict_penalty += 0.1
        
        # Score de complétude (champs remplis)
        total_fields = 0
        filled_fields = 0
        
        for source_data in data_sources.values():
            for field, value in source_data.items():
                total_fields += 1
                if value and str(value).strip():
                    filled_fields += 1
        
        completeness_score = (filled_fields / max(total_fields, 1)) * 0.4
        
        # Score final
        final_score = base_score + completeness_score - conflict_penalty
        
        return max(0.0, min(1.0, final_score))
    
    async def run_async(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Version asynchrone."""
        return self.run(input_data) 