"""
Agent de normalisation des noms d'entreprises.

Normalise les noms d'entreprises, génère des variantes et trouve des correspondances
dans la base de données via matching flou et extraction d'entités nommées.
"""

import time
import re
from typing import Dict, Any, List
from .base import FullFeaturedAgent, AgentResult


class AgentNormalization(FullFeaturedAgent):
    """Agent de normalisation des noms d'entreprises."""
    
    REQUIRED_FIELDS = ['enterprise_name']
    FIELD_TYPES = {'enterprise_name': str}
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__('normalization', config)
        
    def validate_input(self, context: 'TaskContext') -> bool:
        """Valide les données d'entrée."""
        if not context.enterprise_name or not context.enterprise_name.strip():
            return False
        return True
    
    async def execute(self, context: 'TaskContext') -> AgentResult:
        """Exécute la normalisation du nom d'entreprise."""
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            await self.pre_execute(context)
            
            # Vérification du cache
            cached_result = await self.get_cached_result(context)
            if cached_result:
                self.logger.info("Using cached normalization result")
                return cached_result
            
            # Validation des entrées
            if not self.validate_input(context):
                raise ValueError("Invalid input data")
            
            # 1. Normalisation du nom (FAKE DATA pour tests)
            normalized_result = await self._normalize_name_fake(context.enterprise_name)
            
            # 2. Matching avec base de données (FAKE DATA pour tests)
            match_result = await self._match_enterprise_fake(normalized_result['variants'])
            
            # 3. Extraction d'entités nommées (FAKE DATA pour tests)
            ner_result = await self._extract_entities_fake(context.enterprise_name)
            
            # Consolidation des résultats
            consolidated_data = {
                'original_name': context.enterprise_name,
                'normalized_name': normalized_result['normalized'],
                'variants': normalized_result['variants'],
                'matched_entities': match_result['matches'],
                'best_match': match_result.get('best_match'),
                'siren': match_result.get('best_match', {}).get('siren'),
                'confidence_score': match_result.get('confidence', 0.0),
                'named_entities': ner_result['entities'],
                'normalization_method': 'fake_for_testing'
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
                    'entities_extracted': len(ner_result['entities']),
                    'mode': 'fake_testing'
                }
            )
            
            # Mise en cache
            await self.cache_result(result, context)
            
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
    
    async def _normalize_name_fake(self, raw_name: str) -> Dict[str, Any]:
        """Normalise un nom d'entreprise (VERSION FAKE pour tests)."""
        # Simulation d'un traitement de normalisation
        
        # Nettoyage de base
        normalized = raw_name.strip().upper()
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Suppression des formes juridiques courantes pour le nom de base
        legal_forms = ['SA', 'SAS', 'SARL', 'EURL', 'SNC', 'SCOP', 'CORP', 'LTD', 'INC']
        base_name = normalized
        for form in legal_forms:
            base_name = re.sub(f'\\b{form}\\b', '', base_name).strip()
        
        # Génération de variantes
        variants = [
            raw_name,  # Original
            normalized,  # Normalisé
            base_name,  # Sans forme juridique
            raw_name.lower(),  # Minuscules
            raw_name.title(),  # Title case
        ]
        
        # Variantes avec et sans accents (simulation)
        if 'É' in normalized:
            variants.append(normalized.replace('É', 'E'))
        if 'È' in normalized:
            variants.append(normalized.replace('È', 'E'))
        
        # Suppression des doublons
        variants = list(set(variants))
        
        return {
            'normalized': base_name or normalized,
            'variants': variants,
            'confidence': 0.8,
            'method': 'fake_normalization'
        }
    
    async def _match_enterprise_fake(self, name_variants: List[str]) -> Dict[str, Any]:
        """Trouve des correspondances d'entreprises (VERSION FAKE pour tests)."""
        # Simulation de matching avec base de données
        
        # Données factices pour tests
        fake_matches = []
        best_match = None
        confidence = 0.0
        
        # Simulation de matching basée sur le nom
        primary_name = name_variants[0] if name_variants else ""
        
        if "LVMH" in primary_name.upper():
            fake_matches = [
                {
                    'name': 'LVMH MOET HENNESSY LOUIS VUITTON',
                    'siren': '775670417',
                    'score': 0.95,
                    'source': 'fake_db'
                },
                {
                    'name': 'LOUIS VUITTON',
                    'siren': '421048806',
                    'score': 0.85,
                    'source': 'fake_db'
                }
            ]
            best_match = fake_matches[0]
            confidence = 0.95
            
        elif "GOOGLE" in primary_name.upper():
            fake_matches = [
                {
                    'name': 'GOOGLE FRANCE',
                    'siren': '443061841',
                    'score': 0.90,
                    'source': 'fake_db'
                }
            ]
            best_match = fake_matches[0]
            confidence = 0.90
            
        elif "MICROSOFT" in primary_name.upper():
            fake_matches = [
                {
                    'name': 'MICROSOFT FRANCE',
                    'siren': '327733184',
                    'score': 0.88,
                    'source': 'fake_db'
                }
            ]
            best_match = fake_matches[0]
            confidence = 0.88
            
        else:
            # Simulation de matching partiel
            fake_matches = [
                {
                    'name': f'{primary_name} (SIMULATED)',
                    'siren': '123456789',
                    'score': 0.6,
                    'source': 'fake_db'
                }
            ]
            best_match = fake_matches[0]
            confidence = 0.6
        
        return {
            'matches': fake_matches,
            'best_match': best_match,
            'confidence': confidence,
            'method': 'fake_matching'
        }
    
    async def _extract_entities_fake(self, text: str) -> Dict[str, Any]:
        """Extrait les entités nommées (VERSION FAKE pour tests)."""
        # Simulation d'extraction d'entités
        
        entities = []
        
        # Patterns simples pour simulation
        if "LVMH" in text.upper():
            entities.extend([
                {'text': 'LVMH', 'type': 'ORGANIZATION', 'confidence': 0.9},
                {'text': 'MOET HENNESSY', 'type': 'ORGANIZATION', 'confidence': 0.8},
                {'text': 'LOUIS VUITTON', 'type': 'ORGANIZATION', 'confidence': 0.8}
            ])
            
        if "GOOGLE" in text.upper():
            entities.append({'text': 'Google', 'type': 'ORGANIZATION', 'confidence': 0.95})
            
        if "MICROSOFT" in text.upper():
            entities.append({'text': 'Microsoft', 'type': 'ORGANIZATION', 'confidence': 0.95})
        
        # Extraction générique de mots en majuscules (simulation d'orgs)
        import re
        caps_words = re.findall(r'\b[A-Z]{2,}\b', text)
        for word in caps_words:
            if word not in [e['text'] for e in entities]:
                entities.append({
                    'text': word,
                    'type': 'ORGANIZATION',
                    'confidence': 0.5
                })
        
        return {
            'entities': entities,
            'method': 'fake_ner',
            'total_found': len(entities)
        } 