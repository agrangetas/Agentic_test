#!/usr/bin/env python3
"""
Outil d'extraction d'entités nommées (NER).
"""

import time
import re
from typing import Dict, Any, List


class ToolNERExtraction:
    """Outil pour extraire les entités nommées d'un texte."""
    
    def __init__(self):
        self.name = "ner_extraction"
        
        # Patterns pour détecter les entités
        self.company_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc\.?|Corporation|Corp\.?|LLC|Ltd\.?|SA|SARL|SAS)\b',
            r'\b([A-Z]+(?:\s+[A-Z]+)*)\s+(?:Inc\.?|Corporation|Corp\.?|LLC|Ltd\.?|SA|SARL|SAS)\b',
            r'\b(Apple|Microsoft|Google|Amazon|Tesla|LVMH|Meta)\b'
        ]
        
        self.person_patterns = [
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b',  # Prénom Nom
            r'\b(Tim Cook|Bill Gates|Elon Musk|Bernard Arnault|Mark Zuckerberg)\b'  # Noms connus
        ]
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les entités nommées d'un texte.
        
        Args:
            input_data: Dict avec 'text'
            
        Returns:
            Dict avec entities, confidence
        """
        start_time = time.time()
        
        try:
            text = input_data.get('text', '')
            
            if not text:
                return {
                    'entities': [],
                    'confidence': 0.0,
                    'execution_time': time.time() - start_time,
                    'error': 'Texte vide'
                }
            
            # Extraction des entités
            entities = []
            entities.extend(self._extract_companies(text))
            entities.extend(self._extract_persons(text))
            entities.extend(self._extract_locations(text))
            
            # Score de confiance
            confidence = self._calculate_confidence(entities, text)
            
            return {
                'entities': entities,
                'confidence': confidence,
                'execution_time': time.time() - start_time,
                'text_length': len(text)
            }
            
        except Exception as e:
            return {
                'entities': [],
                'confidence': 0.0,
                'execution_time': time.time() - start_time,
                'error': str(e)
            }
    
    def _extract_companies(self, text: str) -> List[Dict[str, Any]]:
        """Extrait les noms d'entreprises."""
        companies = []
        
        for pattern in self.company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                company_name = match.group(1) if match.groups() else match.group(0)
                companies.append({
                    'text': company_name,
                    'type': 'COMPANY',
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.8
                })
        
        return companies
    
    def _extract_persons(self, text: str) -> List[Dict[str, Any]]:
        """Extrait les noms de personnes."""
        persons = []
        
        for pattern in self.person_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                person_name = match.group(1) if match.groups() else match.group(0)
                persons.append({
                    'text': person_name,
                    'type': 'PERSON',
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.7
                })
        
        return persons
    
    def _extract_locations(self, text: str) -> List[Dict[str, Any]]:
        """Extrait les lieux."""
        locations = []
        
        # Patterns simples pour les lieux
        location_patterns = [
            r'\b(Paris|Londres|New York|San Francisco|Cupertino|Seattle|Redmond)\b'
        ]
        
        for pattern in location_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                location_name = match.group(0)
                locations.append({
                    'text': location_name,
                    'type': 'LOCATION',
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.6
                })
        
        return locations
    
    def _calculate_confidence(self, entities: List[Dict[str, Any]], text: str) -> float:
        """Calcule un score de confiance global."""
        if not entities:
            return 0.0
        
        # Score basé sur le nombre d'entités trouvées
        entity_density = len(entities) / max(len(text.split()), 1)
        base_score = min(entity_density * 5, 0.8)  # Max 0.8 pour la densité
        
        # Score moyen des confidences individuelles
        avg_confidence = sum(e.get('confidence', 0) for e in entities) / len(entities)
        
        # Score final
        final_score = (base_score + avg_confidence) / 2
        
        return min(final_score, 1.0)
    
    async def run_async(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Version asynchrone."""
        return self.run(input_data) 