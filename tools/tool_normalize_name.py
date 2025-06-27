#!/usr/bin/env python3
"""
Outil de normalisation des noms d'entreprises.
"""

import re
import time
from typing import Dict, Any, List


class ToolNormalizeName:
    """Outil pour normaliser les noms d'entreprises."""
    
    def __init__(self):
        self.name = "normalize_name"
        
        # Mots à supprimer ou normaliser
        self.stopwords = {
            'SA', 'SARL', 'SAS', 'SASU', 'SNC', 'SCS', 'GIE',
            'Inc', 'Inc.', 'Corporation', 'Corp', 'Corp.', 
            'LLC', 'Ltd', 'Ltd.', 'Limited', 'SE', 'SCA'
        }
        
        # Remplacements communs
        self.replacements = {
            '&': 'ET',
            'Cie': 'COMPAGNIE',
            'Ets': 'ETABLISSEMENTS',
            'St': 'SAINT',
            'Ste': 'SAINTE'
        }
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalise un nom d'entreprise.
        
        Args:
            input_data: Dict avec 'raw_name'
            
        Returns:
            Dict avec normalized, variants, confidence
        """
        start_time = time.time()
        
        try:
            raw_name = input_data.get('raw_name', '')
            
            if not raw_name:
                return {
                    'normalized': '',
                    'variants': [],
                    'confidence': 0.0,
                    'execution_time': time.time() - start_time,
                    'error': 'Nom vide'
                }
            
            # Normalisation de base
            normalized = self._normalize_basic(raw_name)
            
            # Génération de variantes
            variants = self._generate_variants(normalized, raw_name)
            
            # Score de confiance basé sur la complexité
            confidence = self._calculate_confidence(raw_name, normalized)
            
            return {
                'normalized': normalized,
                'variants': variants,
                'confidence': confidence,
                'execution_time': time.time() - start_time,
                'original': raw_name
            }
            
        except Exception as e:
            return {
                'normalized': input_data.get('raw_name', ''),
                'variants': [],
                'confidence': 0.0,
                'execution_time': time.time() - start_time,
                'error': str(e)
            }
    
    def _normalize_basic(self, name: str) -> str:
        """Normalisation de base du nom."""
        # Conversion en majuscules
        normalized = name.upper().strip()
        
        # Suppression des caractères spéciaux
        normalized = re.sub(r'[^\w\s&-]', ' ', normalized)
        
        # Remplacements communs
        for old, new in self.replacements.items():
            normalized = normalized.replace(old.upper(), new)
        
        # Suppression des formes juridiques en fin
        words = normalized.split()
        if words and words[-1] in self.stopwords:
            words = words[:-1]
        
        # Nettoyage des espaces multiples
        normalized = ' '.join(words)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _generate_variants(self, normalized: str, original: str) -> List[str]:
        """Génère des variantes du nom normalisé."""
        variants = [normalized]
        
        # Variante avec l'original
        if original.upper() != normalized:
            variants.append(original.upper())
        
        # Variante sans accents (simulation)
        no_accent = normalized.replace('É', 'E').replace('È', 'E').replace('À', 'A')
        if no_accent != normalized:
            variants.append(no_accent)
        
        # Variante avec abréviations
        abbreviated = normalized
        for word in ['SOCIÉTÉ', 'ETABLISSEMENTS', 'COMPAGNIE']:
            if word in abbreviated:
                abbreviated = abbreviated.replace(word, word[:3])
        
        if abbreviated != normalized:
            variants.append(abbreviated)
        
        # Variante avec &
        if 'ET' in normalized:
            with_ampersand = normalized.replace(' ET ', ' & ')
            variants.append(with_ampersand)
        
        return list(set(variants))  # Suppression des doublons
    
    def _calculate_confidence(self, original: str, normalized: str) -> float:
        """Calcule un score de confiance pour la normalisation."""
        # Score de base
        confidence = 0.7
        
        # Bonus si le nom contient des mots-clés d'entreprise
        business_keywords = ['SOCIÉTÉ', 'ENTREPRISE', 'GROUPE', 'HOLDING', 'COMPANY']
        if any(keyword in normalized for keyword in business_keywords):
            confidence += 0.1
        
        # Bonus si forme juridique détectée
        if any(form in original.upper() for form in self.stopwords):
            confidence += 0.1
        
        # Malus si nom très court
        if len(normalized) < 5:
            confidence -= 0.2
        
        # Malus si beaucoup de caractères supprimés
        removed_ratio = 1 - (len(normalized) / max(len(original), 1))
        if removed_ratio > 0.3:
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    async def run_async(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Version asynchrone (délègue au synchrone)."""
        return self.run(input_data) 