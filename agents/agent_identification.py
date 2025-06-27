"""
Agent d'identification d'entreprises.

Trouve le SIREN et l'URL officielle des entreprises à partir des données normalisées.
"""

import time
from typing import Dict, Any
from .base import FullFeaturedAgent, AgentResult


class AgentIdentification(FullFeaturedAgent):
    """Agent d'identification SIREN/URL d'entreprises."""
    
    REQUIRED_FIELDS = ['normalized_name']
    FIELD_TYPES = {'normalized_name': str}
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__('identification', config)
    
    def validate_input(self, context: 'TaskContext') -> bool:
        """Valide les données d'entrée."""
        normalization_data = context.collected_data.get('normalization', {})
        return bool(normalization_data.get('normalized_name'))
    
    async def execute(self, context: 'TaskContext') -> AgentResult:
        """Exécute l'identification de l'entreprise."""
        start_time = time.time()
        errors = []
        warnings = []
        
        self.logger.debug("Starting identification execution", extra={
            "session_id": context.session_id,
            "enterprise_name": context.enterprise_name,
            "function": "execute"
        })
        
        try:
            await self.pre_execute(context)
            
            # Récupération des données de normalisation
            self.logger.debug("Retrieving normalization data", extra={
                "session_id": context.session_id,
                "has_normalization_data": 'normalization' in context.collected_data,
                "function": "execute"
            })
            
            normalization_data = context.collected_data.get('normalization', {})
            if not normalization_data:
                raise ValueError("Normalization data required")
            
            # Utilise le SIREN déjà trouvé par la normalisation ou cherche
            existing_siren = normalization_data.get('siren')
            
            self.logger.debug("Checking for existing SIREN", extra={
                "session_id": context.session_id,
                "has_existing_siren": bool(existing_siren),
                "existing_siren": existing_siren,
                "function": "execute"
            })
            
            if existing_siren:
                siren = existing_siren
                confidence = 0.9
                method = 'from_normalization'
                
                self.logger.debug("Using SIREN from normalization", extra={
                    "session_id": context.session_id,
                    "siren": siren,
                    "confidence": confidence,
                    "function": "execute"
                })
            else:
                # Recherche SIREN (FAKE)
                self.logger.debug("Starting SIREN search (fake mode)", extra={
                    "session_id": context.session_id,
                    "company_name": normalization_data['normalized_name'],
                    "function": "_find_siren_fake"
                })
                
                siren_result = await self._find_siren_fake(normalization_data['normalized_name'])
                siren = siren_result['siren']
                confidence = siren_result['confidence']
                method = 'fake_search'
                
                self.logger.debug("SIREN search completed", extra={
                    "session_id": context.session_id,
                    "siren": siren,
                    "confidence": confidence,
                    "source": siren_result.get('source'),
                    "function": "_find_siren_fake"
                })
            
            # Recherche URL officielle (FAKE)
            self.logger.debug("Starting website URL search (fake mode)", extra={
                "session_id": context.session_id,
                "company_name": normalization_data['normalized_name'],
                "siren": siren,
                "function": "_find_website_fake"
            })
            
            url_result = await self._find_website_fake(normalization_data['normalized_name'], siren)
            
            self.logger.debug("Website URL search completed", extra={
                "session_id": context.session_id,
                "url": url_result['url'],
                "confidence": url_result['confidence'],
                "method": url_result['method'],
                "function": "_find_website_fake"
            })
            
            # Données d'identification consolidées
            identification_data = {
                'siren': siren,
                'url': url_result['url'],
                'normalized_name': normalization_data['normalized_name'],
                'original_name': normalization_data['original_name'],
                'confidence_score': min(confidence, url_result['confidence']),
                'identification_method': method,
                'url_method': url_result['method'],
                'verified': True if siren and url_result['url'] else False
            }
            
            execution_time = time.time() - start_time
            
            self.logger.info("Identification execution successful", extra={
                "session_id": context.session_id,
                "execution_time": execution_time,
                "confidence_score": identification_data['confidence_score'],
                "siren": siren,
                "url": url_result['url'],
                "verified": identification_data['verified'],
                "event_type": "identification_success"
            })
            
            result = AgentResult(
                agent_name=self.name,
                success=bool(siren),
                data=identification_data,
                confidence_score=identification_data['confidence_score'],
                execution_time=execution_time,
                errors=errors,
                warnings=warnings,
                metadata={
                    'siren_found': bool(siren),
                    'url_found': bool(url_result['url']),
                    'mode': 'fake_testing'
                }
            )
            
            await self.post_execute(result, context)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            errors.append(str(e))
            
            self.logger.error("Identification execution failed", extra={
                "session_id": context.session_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time": execution_time,
                "event_type": "identification_error"
            })
            
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
    
    async def _find_siren_fake(self, company_name: str) -> Dict[str, Any]:
        """Trouve le SIREN d'une entreprise (VERSION FAKE)."""
        start_time = time.time()
        
        self.logger.debug("Starting fake SIREN search", extra={
            "company_name": company_name,
            "function": "_find_siren_fake"
        })
        
        # Simulation de recherche SIREN
        result = None
        
        if "LVMH" in company_name.upper():
            result = {
                'siren': '775670417',
                'confidence': 0.95,
                'source': 'fake_inpi_db'
            }
        elif "GOOGLE" in company_name.upper():
            result = {
                'siren': '443061841',
                'confidence': 0.90,
                'source': 'fake_inpi_db'
            }
        elif "MICROSOFT" in company_name.upper():
            result = {
                'siren': '327733184',
                'confidence': 0.88,
                'source': 'fake_inpi_db'
            }
        else:
            # SIREN générique pour test
            result = {
                'siren': '123456789',
                'confidence': 0.6,
                'source': 'fake_generated'
            }
        
        execution_time = time.time() - start_time
        
        self.logger.debug("Fake SIREN search completed", extra={
            "company_name": company_name,
            "siren": result['siren'],
            "confidence": result['confidence'],
            "source": result['source'],
            "execution_time": execution_time,
            "function": "_find_siren_fake"
        })
        
        return result
    
    async def _find_website_fake(self, company_name: str, siren: str) -> Dict[str, Any]:
        """Trouve l'URL officielle d'une entreprise (VERSION FAKE)."""
        # Simulation de recherche d'URL
        
        if "LVMH" in company_name.upper():
            return {
                'url': 'https://www.lvmh.fr',
                'confidence': 0.95,
                'method': 'fake_web_search'
            }
        elif "GOOGLE" in company_name.upper():
            return {
                'url': 'https://www.google.fr',
                'confidence': 0.98,
                'method': 'fake_web_search'
            }
        elif "MICROSOFT" in company_name.upper():
            return {
                'url': 'https://www.microsoft.com/fr-fr',
                'confidence': 0.90,
                'method': 'fake_web_search'
            }
        else:
            # URL générique pour test
            clean_name = company_name.lower().replace(' ', '')
            return {
                'url': f'https://www.{clean_name}.com',
                'confidence': 0.5,
                'method': 'fake_generated'
            } 