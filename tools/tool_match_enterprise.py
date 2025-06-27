#!/usr/bin/env python3
"""
Outil de matching d'entreprises.
"""

import time
import random
from typing import Dict, Any, List


class ToolMatchEnterprise:
    """Outil pour matcher des entreprises dans une base de données."""
    
    def __init__(self):
        self.name = "match_enterprise"
        
        # Base de données fictive pour les tests
        self.fake_database = [
            {'siren': '552120222', 'name': 'APPLE INC', 'url': 'https://www.apple.com'},
            {'siren': '123456789', 'name': 'MICROSOFT CORPORATION', 'url': 'https://www.microsoft.com'},
            {'siren': '987654321', 'name': 'GOOGLE LLC', 'url': 'https://www.google.com'},
            {'siren': '456789123', 'name': 'TESLA INC', 'url': 'https://www.tesla.com'},
            {'siren': '789123456', 'name': 'AMAZON COM INC', 'url': 'https://www.amazon.com'}
        ]
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recherche des correspondances d'entreprises.
        
        Args:
            input_data: Dict avec 'name_variants'
            
        Returns:
            Dict avec matches, best_match, confidence
        """
        start_time = time.time()
        
        try:
            name_variants = input_data.get('name_variants', [])
            
            if not name_variants:
                return {
                    'matches': [],
                    'best_match': {},
                    'confidence': 0.0,
                    'execution_time': time.time() - start_time,
                    'error': 'Aucune variante fournie'
                }
            
            # Recherche des correspondances
            matches = self._find_matches(name_variants)
            
            # Meilleure correspondance
            best_match = self._get_best_match(matches) if matches else {}
            
            # Score de confiance
            confidence = self._calculate_confidence(matches, name_variants)
            
            return {
                'matches': matches,
                'best_match': best_match,
                'confidence': confidence,
                'execution_time': time.time() - start_time,
                'searched_variants': name_variants
            }
            
        except Exception as e:
            return {
                'matches': [],
                'best_match': {},
                'confidence': 0.0,
                'execution_time': time.time() - start_time,
                'error': str(e)
            }
    
    def _find_matches(self, name_variants: List[str]) -> List[Dict[str, Any]]:
        """Trouve les correspondances dans la base de données."""
        matches = []
        
        for variant in name_variants:
            variant_upper = variant.upper()
            
            for entry in self.fake_database:
                db_name = entry['name'].upper()
                
                # Matching exact
                if variant_upper == db_name:
                    match = entry.copy()
                    match['match_type'] = 'exact'
                    match['similarity'] = 1.0
                    matches.append(match)
                    continue
                
                # Matching partiel
                if variant_upper in db_name or db_name in variant_upper:
                    match = entry.copy()
                    match['match_type'] = 'partial'
                    match['similarity'] = self._calculate_similarity(variant_upper, db_name)
                    matches.append(match)
                    continue
                
                # Matching par mots-clés
                variant_words = set(variant_upper.split())
                db_words = set(db_name.split())
                common_words = variant_words.intersection(db_words)
                
                if len(common_words) >= 1 and len(common_words) / max(len(variant_words), 1) > 0.5:
                    match = entry.copy()
                    match['match_type'] = 'keyword'
                    match['similarity'] = len(common_words) / len(variant_words.union(db_words))
                    matches.append(match)
        
        # Suppression des doublons
        seen_sirens = set()
        unique_matches = []
        for match in matches:
            if match['siren'] not in seen_sirens:
                seen_sirens.add(match['siren'])
                unique_matches.append(match)
        
        # Tri par similarité
        unique_matches.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        return unique_matches
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calcule la similarité entre deux chaînes."""
        # Similarité simple basée sur les caractères communs
        set1 = set(str1.replace(' ', ''))
        set2 = set(str2.replace(' ', ''))
        
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _get_best_match(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Retourne la meilleure correspondance."""
        if not matches:
            return {}
        
        # La première après tri par similarité
        best = matches[0].copy()
        
        # Ajout d'informations sur la qualité du match
        if best.get('similarity', 0) >= 0.9:
            best['quality'] = 'excellent'
        elif best.get('similarity', 0) >= 0.7:
            best['quality'] = 'good'
        elif best.get('similarity', 0) >= 0.5:
            best['quality'] = 'fair'
        else:
            best['quality'] = 'poor'
        
        return best
    
    def _calculate_confidence(self, matches: List[Dict[str, Any]], variants: List[str]) -> float:
        """Calcule un score de confiance global."""
        if not matches:
            return 0.0
        
        # Score basé sur le nombre de correspondances
        base_score = min(len(matches) / max(len(variants), 1), 1.0)
        
        # Bonus pour la qualité de la meilleure correspondance
        best_similarity = matches[0].get('similarity', 0) if matches else 0
        quality_bonus = best_similarity * 0.3
        
        # Bonus pour correspondance exacte
        exact_bonus = 0.2 if any(m.get('match_type') == 'exact' for m in matches) else 0
        
        confidence = base_score * 0.5 + quality_bonus + exact_bonus
        
        return min(confidence, 1.0)
    
    async def run_async(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Version asynchrone."""
        return self.run(input_data) 