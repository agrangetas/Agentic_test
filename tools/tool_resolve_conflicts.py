#!/usr/bin/env python3
"""
Outil de résolution de conflits entre sources de données.
"""

import time
from typing import Dict, Any, List


class ToolResolveConflicts:
    """Outil pour résoudre les conflits entre sources de données."""
    
    def __init__(self):
        self.name = "resolve_conflicts"
        
        # Priorités des sources (plus élevé = plus fiable)
        self.source_priorities = {
            'inpi': 0.9,
            'official': 0.8,
            'api': 0.7,
            'web': 0.6,
            'manual': 0.5,
            'unknown': 0.3
        }
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Résout les conflits entre sources de données.
        
        Args:
            input_data: Dict avec 'conflicting_data'
            
        Returns:
            Dict avec resolved_data, resolutions, confidence
        """
        start_time = time.time()
        
        try:
            conflicting_data = input_data.get('conflicting_data', [])
            
            if not conflicting_data:
                return {
                    'resolved_data': {},
                    'resolutions': [],
                    'confidence': 0.0,
                    'execution_time': time.time() - start_time,
                    'error': 'Aucun conflit à résoudre'
                }
            
            # Résolution des conflits
            resolved_data = {}
            resolutions = []
            
            for conflict in conflicting_data:
                resolution = self._resolve_single_conflict(conflict)
                if resolution:
                    field = conflict.get('field', 'unknown')
                    resolved_data[field] = resolution['chosen_value']
                    resolutions.append(resolution)
            
            # Score de confiance global
            confidence = self._calculate_resolution_confidence(resolutions)
            
            return {
                'resolved_data': resolved_data,
                'resolutions': resolutions,
                'confidence': confidence,
                'execution_time': time.time() - start_time,
                'conflicts_resolved': len(resolutions)
            }
            
        except Exception as e:
            return {
                'resolved_data': {},
                'resolutions': [],
                'confidence': 0.0,
                'execution_time': time.time() - start_time,
                'error': str(e)
            }
    
    def _resolve_single_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Résout un conflit unique."""
        field = conflict.get('field', '')
        values = conflict.get('values', [])
        
        if not values:
            return None
        
        # Stratégies de résolution selon le type de champ
        if field == 'siren':
            return self._resolve_by_source_priority(conflict)
        elif field == 'url':
            return self._resolve_url_conflict(conflict)
        elif field == 'name':
            return self._resolve_name_conflict(conflict)
        else:
            return self._resolve_by_confidence(conflict)
    
    def _resolve_by_source_priority(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Résolution basée sur la priorité des sources."""
        values = conflict.get('values', [])
        field = conflict.get('field', '')
        
        best_value = None
        best_priority = -1
        best_source = None
        
        for value_info in values:
            source = value_info.get('source', 'unknown')
            priority = self.source_priorities.get(source, 0.3)
            
            if priority > best_priority:
                best_priority = priority
                best_value = value_info.get('value')
                best_source = source
        
        return {
            'field': field,
            'chosen_value': best_value,
            'chosen_source': best_source,
            'reason': f'Source prioritaire ({best_source})',
            'confidence': best_priority,
            'method': 'source_priority'
        }
    
    def _resolve_by_confidence(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Résolution basée sur la confiance."""
        values = conflict.get('values', [])
        field = conflict.get('field', '')
        
        best_value = None
        best_confidence = -1
        best_source = None
        
        for value_info in values:
            confidence = value_info.get('confidence', 0.0)
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_value = value_info.get('value')
                best_source = value_info.get('source')
        
        return {
            'field': field,
            'chosen_value': best_value,
            'chosen_source': best_source,
            'reason': f'Confiance la plus élevée ({best_confidence:.2f})',
            'confidence': best_confidence,
            'method': 'confidence'
        }
    
    def _resolve_url_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Résolution spécifique pour les URLs."""
        values = conflict.get('values', [])
        field = conflict.get('field', '')
        
        # Préférer les URLs HTTPS
        https_values = [v for v in values if str(v.get('value', '')).startswith('https://')]
        if https_values:
            chosen = https_values[0]
            return {
                'field': field,
                'chosen_value': chosen.get('value'),
                'chosen_source': chosen.get('source'),
                'reason': 'URL HTTPS préférée',
                'confidence': 0.8,
                'method': 'url_preference'
            }
        
        # Sinon, résolution par priorité de source
        return self._resolve_by_source_priority(conflict)
    
    def _resolve_name_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Résolution spécifique pour les noms d'entreprises."""
        values = conflict.get('values', [])
        field = conflict.get('field', '')
        
        # Préférer les noms avec forme juridique
        legal_forms = ['SA', 'SARL', 'SAS', 'Inc', 'Corp', 'LLC', 'Ltd']
        
        for value_info in values:
            name = str(value_info.get('value', '')).upper()
            if any(form in name for form in legal_forms):
                return {
                    'field': field,
                    'chosen_value': value_info.get('value'),
                    'chosen_source': value_info.get('source'),
                    'reason': 'Nom avec forme juridique',
                    'confidence': 0.7,
                    'method': 'name_preference'
                }
        
        # Sinon, résolution par priorité de source
        return self._resolve_by_source_priority(conflict)
    
    def _calculate_resolution_confidence(self, resolutions: List[Dict[str, Any]]) -> float:
        """Calcule la confiance globale des résolutions."""
        if not resolutions:
            return 0.0
        
        # Moyenne pondérée des confidences
        total_confidence = 0
        total_weight = 0
        
        for resolution in resolutions:
            confidence = resolution.get('confidence', 0.0)
            method = resolution.get('method', 'unknown')
            
            # Poids selon la méthode
            weight = 1.0
            if method == 'source_priority':
                weight = 1.2
            elif method == 'confidence':
                weight = 1.0
            elif method in ['url_preference', 'name_preference']:
                weight = 0.8
            
            total_confidence += confidence * weight
            total_weight += weight
        
        return total_confidence / total_weight if total_weight > 0 else 0.0
    
    async def run_async(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Version asynchrone."""
        return self.run(input_data) 