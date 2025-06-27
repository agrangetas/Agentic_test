"""
Gestionnaire de cache Redis avec politiques avancées.
"""

import asyncio
import json
import gzip
import pickle
from typing import Any, Dict, List, Optional, Union
import aioredis
from loguru import logger
import yaml
import os
from datetime import datetime, timedelta


class CacheManager:
    """Gestionnaire de cache Redis avec politiques configurables."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/1", config_path: str = "config/cache_policy.yaml"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.config = self._load_config(config_path)
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Charge la configuration du cache."""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load cache config: {e}")
            
        # Configuration par défaut
        return {
            'cache_policy': {
                'enterprise_data': {'ttl': '7d', 'compress': True},
                'agent_results': {'ttl': '12h', 'compress': True},
                'validation_results': {'ttl': '6h', 'compress': False}
            },
            'redis_config': {
                'compression_threshold': 1024,
                'compression_algorithm': 'gzip'
            },
            'key_prefixes': {
                'enterprise': 'ent:',
                'agent_result': 'agent:',
                'session': 'sess:',
                'validation': 'valid:'
            }
        }
    
    async def connect(self):
        """Établit la connexion Redis."""
        try:
            self.redis = aioredis.from_url(self.redis_url, decode_responses=False)
            await self.redis.ping()
            logger.info(f"Connected to Redis: {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Ferme la connexion Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    def _get_ttl_seconds(self, ttl_str: str) -> int:
        """Convertit une chaîne TTL en secondes."""
        if ttl_str.endswith('s'):
            return int(ttl_str[:-1])
        elif ttl_str.endswith('m'):
            return int(ttl_str[:-1]) * 60
        elif ttl_str.endswith('h'):
            return int(ttl_str[:-1]) * 3600
        elif ttl_str.endswith('d'):
            return int(ttl_str[:-1]) * 86400
        else:
            return int(ttl_str)
    
    def _should_compress(self, data: bytes, policy: Dict[str, Any]) -> bool:
        """Détermine si les données doivent être compressées."""
        if not policy.get('compress', False):
            return False
        
        threshold = self.config['redis_config'].get('compression_threshold', 1024)
        return len(data) > threshold
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compresse les données."""
        algorithm = self.config['redis_config'].get('compression_algorithm', 'gzip')
        if algorithm == 'gzip':
            return gzip.compress(data)
        return data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Décompresse les données."""
        try:
            return gzip.decompress(data)
        except:
            # Données non compressées
            return data
    
    def _serialize_data(self, data: Any) -> bytes:
        """Sérialise les données."""
        try:
            # Essaie JSON d'abord (plus lisible)
            return json.dumps(data, default=str).encode('utf-8')
        except:
            # Fallback vers pickle
            return pickle.dumps(data)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Désérialise les données."""
        try:
            # Essaie JSON d'abord
            return json.loads(data.decode('utf-8'))
        except:
            # Fallback vers pickle
            return pickle.loads(data)
    
    def _build_key(self, category: str, key: str) -> str:
        """Construit une clé de cache avec préfixe."""
        prefix = self.config['key_prefixes'].get(category, '')
        return f"{prefix}{key}"
    
    async def get(self, category: str, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        if not self.redis:
            return None
            
        cache_key = self._build_key(category, key)
        
        try:
            data = await self.redis.get(cache_key)
            if data is None:
                self.stats['misses'] += 1
                return None
                
            # Décompression si nécessaire
            decompressed_data = self._decompress_data(data)
            
            # Désérialisation
            result = self._deserialize_data(decompressed_data)
            
            self.stats['hits'] += 1
            logger.debug(f"Cache hit for key: {cache_key}")
            return result
            
        except Exception as e:
            logger.error(f"Cache get error for key {cache_key}: {e}")
            self.stats['misses'] += 1
            return None
    
    async def set(self, category: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Stocke une valeur dans le cache."""
        if not self.redis:
            return False
            
        cache_key = self._build_key(category, key)
        policy = self.config['cache_policy'].get(category, {})
        
        try:
            # Sérialisation
            serialized_data = self._serialize_data(value)
            
            # Compression si nécessaire
            if self._should_compress(serialized_data, policy):
                final_data = self._compress_data(serialized_data)
            else:
                final_data = serialized_data
            
            # TTL
            if ttl is None:
                ttl_str = policy.get('ttl', '1h')
                ttl = self._get_ttl_seconds(ttl_str)
            
            # Stockage
            await self.redis.setex(cache_key, ttl, final_data)
            
            self.stats['sets'] += 1
            logger.debug(f"Cache set for key: {cache_key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {cache_key}: {e}")
            return False
    
    async def delete(self, category: str, key: str) -> bool:
        """Supprime une clé du cache."""
        if not self.redis:
            return False
            
        cache_key = self._build_key(category, key)
        
        try:
            result = await self.redis.delete(cache_key)
            self.stats['deletes'] += 1
            logger.debug(f"Cache delete for key: {cache_key}")
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {cache_key}: {e}")
            return False
    
    async def invalidate_pattern(self, category: str, pattern: str) -> int:
        """Invalide toutes les clés correspondant à un pattern."""
        if not self.redis:
            return 0
            
        cache_pattern = self._build_key(category, pattern)
        
        try:
            keys = await self.redis.keys(cache_pattern)
            if keys:
                result = await self.redis.delete(*keys)
                logger.info(f"Invalidated {result} keys matching pattern: {cache_pattern}")
                return result
            return 0
        except Exception as e:
            logger.error(f"Cache invalidation error for pattern {cache_pattern}: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache."""
        total = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total if total > 0 else 0
        
        redis_info = {}
        if self.redis:
            try:
                redis_info = await self.redis.info('memory')
            except:
                pass
        
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': hit_rate,
            'sets': self.stats['sets'],
            'deletes': self.stats['deletes'],
            'redis_memory': redis_info.get('used_memory_human', 'N/A')
        }
    
    async def clear_expired(self) -> int:
        """Nettoie les clés expirées (Redis le fait automatiquement, mais utile pour forcer)."""
        if not self.redis:
            return 0
        
        try:
            # Force l'expiration des clés
            expired_count = 0
            for category in self.config['key_prefixes']:
                pattern = self._build_key(category, '*')
                keys = await self.redis.keys(pattern)
                
                for key in keys:
                    ttl = await self.redis.ttl(key)
                    if ttl == -2:  # Clé expirée mais pas encore supprimée
                        await self.redis.delete(key)
                        expired_count += 1
            
            logger.info(f"Cleared {expired_count} expired keys")
            return expired_count
            
        except Exception as e:
            logger.error(f"Error clearing expired keys: {e}")
            return 0


# Factory function
def create_cache_manager(redis_url: str = "redis://localhost:6379/1", config_path: str = "config/cache_policy.yaml") -> CacheManager:
    """Factory pour créer un gestionnaire de cache."""
    return CacheManager(redis_url, config_path) 