#!/usr/bin/env python3
"""
Gestionnaire de connexion et opérations PostgreSQL.
"""

import asyncio
import asyncpg
import psycopg2
from typing import Dict, Any, List, Optional, Union
import logging
from contextlib import asynccontextmanager
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestionnaire de base de données PostgreSQL avec support async et sync."""
    
    def __init__(self, connection_params: Optional[Dict[str, Any]] = None):
        """Initialise le gestionnaire de base de données."""
        self.connection_params = connection_params or {
            'host': 'postgres',
            'port': 5432,
            'database': 'agent_company_db',
            'user': 'agent_user',
            'password': 'agent_password'
        }
        
        self.pool = None
        self.sync_connection = None
        self.connected = False
    
    async def connect(self):
        """Établit la connexion async via pool."""
        try:
            self.pool = await asyncpg.create_pool(
                **self.connection_params,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
            self.connected = True
            logger.info("Pool de connexions PostgreSQL créé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du pool PostgreSQL: {e}")
            raise
    
    async def disconnect(self):
        """Ferme la connexion async."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            self.connected = False
            logger.info("Pool de connexions PostgreSQL fermé")
    
    def connect_sync(self):
        """Établit une connexion synchrone."""
        try:
            self.sync_connection = psycopg2.connect(**self.connection_params)
            logger.info("Connexion synchrone PostgreSQL établie")
            return self.sync_connection
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion synchrone PostgreSQL: {e}")
            raise
    
    def disconnect_sync(self):
        """Ferme la connexion synchrone."""
        if self.sync_connection:
            self.sync_connection.close()
            self.sync_connection = None
            logger.info("Connexion synchrone PostgreSQL fermée")
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager pour obtenir une connexion du pool."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """Exécute une requête SELECT et retourne les résultats."""
        async with self.get_connection() as conn:
            if params:
                result = await conn.fetch(query, *params)
            else:
                result = await conn.fetch(query)
            
            return [tuple(row) for row in result]
    
    async def execute_command(self, command: str, params: Optional[tuple] = None) -> str:
        """Exécute une commande INSERT/UPDATE/DELETE et retourne le statut."""
        async with self.get_connection() as conn:
            if params:
                result = await conn.execute(command, *params)
            else:
                result = await conn.execute(command)
            
            return result
    
    async def insert_enterprise(self, data: Dict[str, Any]) -> str:
        """Insère une nouvelle entreprise."""
        query = """
            INSERT INTO entreprises (id, nom, nom_normalise, siren, url, secteur, resume, score_confiance)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """
        
        params = (
            data.get('id'),
            data.get('nom'),
            data.get('nom_normalise'),
            data.get('siren'),
            data.get('url'),
            data.get('secteur'),
            data.get('resume'),
            data.get('score_confiance', 0.5)
        )
        
        return await self.execute_command(query, params)
    
    async def get_enterprise_by_siren(self, siren: str) -> Optional[Dict[str, Any]]:
        """Récupère une entreprise par son SIREN."""
        query = """
            SELECT id, nom, nom_normalise, siren, url, secteur, resume, score_confiance, date_maj
            FROM entreprises 
            WHERE siren = $1
        """
        
        result = await self.execute_query(query, (siren,))
        
        if result:
            row = result[0]
            return {
                'id': row[0],
                'nom': row[1],
                'nom_normalise': row[2],
                'siren': row[3],
                'url': row[4],
                'secteur': row[5],
                'resume': row[6],
                'score_confiance': row[7],
                'date_maj': row[8]
            }
        
        return None
    
    async def get_enterprise_by_id(self, enterprise_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une entreprise par son ID."""
        query = """
            SELECT id, nom, nom_normalise, siren, url, secteur, resume, score_confiance, date_maj
            FROM entreprises 
            WHERE id = $1
        """
        
        result = await self.execute_query(query, (enterprise_id,))
        
        if result:
            row = result[0]
            return {
                'id': row[0],
                'nom': row[1],
                'nom_normalise': row[2],
                'siren': row[3],
                'url': row[4],
                'secteur': row[5],
                'resume': row[6],
                'score_confiance': row[7],
                'date_maj': row[8]
            }
        
        return None
    
    async def update_enterprise(self, enterprise_id: str, data: Dict[str, Any]) -> str:
        """Met à jour une entreprise."""
        set_clauses = []
        params = []
        param_index = 1
        
        for field, value in data.items():
            if field != 'id':  # On ne met pas à jour l'ID
                set_clauses.append(f"{field} = ${param_index}")
                params.append(value)
                param_index += 1
        
        if not set_clauses:
            return "No fields to update"
        
        query = f"""
            UPDATE entreprises 
            SET {', '.join(set_clauses)}, date_maj = NOW()
            WHERE id = ${param_index}
        """
        params.append(enterprise_id)
        
        return await self.execute_command(query, tuple(params))
    
    async def insert_exploration_log(self, log_data: Dict[str, Any]) -> str:
        """Insère un log d'exploration."""
        query = """
            INSERT INTO exploration_logs (id, session_id, entreprise_id, agent, input, output, duree_execution, statut)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """
        
        params = (
            log_data.get('id'),
            log_data.get('session_id'),
            log_data.get('entreprise_id'),
            log_data.get('agent'),
            json.dumps(log_data.get('input', {})),
            json.dumps(log_data.get('output', {})),
            log_data.get('duree_execution'),
            log_data.get('statut', 'success')
        )
        
        return await self.execute_command(query, params)
    
    async def get_exploration_logs(self, session_id: str) -> List[Dict[str, Any]]:
        """Récupère les logs d'exploration pour une session."""
        query = """
            SELECT id, session_id, entreprise_id, agent, input, output, duree_execution, statut, date_executed
            FROM exploration_logs 
            WHERE session_id = $1
            ORDER BY date_executed
        """
        
        result = await self.execute_query(query, (session_id,))
        
        logs = []
        for row in result:
            logs.append({
                'id': row[0],
                'session_id': row[1],
                'entreprise_id': row[2],
                'agent': row[3],
                'input': json.loads(row[4]) if row[4] else {},
                'output': json.loads(row[5]) if row[5] else {},
                'duree_execution': row[6],
                'statut': row[7],
                'date_executed': row[8]
            })
        
        return logs
    
    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """Crée une nouvelle session d'exploration."""
        query = """
            INSERT INTO sessions_exploration (id, entreprise_initiale, parametres, statut)
            VALUES ($1, $2, $3, $4)
        """
        
        params = (
            session_data.get('id'),
            session_data.get('entreprise_initiale'),
            json.dumps(session_data.get('parametres', {})),
            session_data.get('statut', 'en_cours')
        )
        
        return await self.execute_command(query, params)
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> str:
        """Met à jour une session d'exploration."""
        set_clauses = []
        params = []
        param_index = 1
        
        for field, value in updates.items():
            if field == 'parametres':
                set_clauses.append(f"{field} = ${param_index}")
                params.append(json.dumps(value))
            else:
                set_clauses.append(f"{field} = ${param_index}")
                params.append(value)
            param_index += 1
        
        if not set_clauses:
            return "No fields to update"
        
        query = f"""
            UPDATE sessions_exploration 
            SET {', '.join(set_clauses)}
            WHERE id = ${param_index}
        """
        params.append(session_id)
        
        return await self.execute_command(query, tuple(params))
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une session d'exploration."""
        query = """
            SELECT id, entreprise_initiale, parametres, statut, nb_entreprises_trouvees, 
                   date_debut, date_fin, resume_final
            FROM sessions_exploration 
            WHERE id = $1
        """
        
        result = await self.execute_query(query, (session_id,))
        
        if result:
            row = result[0]
            return {
                'id': row[0],
                'entreprise_initiale': row[1],
                'parametres': json.loads(row[2]) if row[2] else {},
                'statut': row[3],
                'nb_entreprises_trouvees': row[4],
                'date_debut': row[5],
                'date_fin': row[6],
                'resume_final': row[7]
            }
        
        return None
    
    def execute_query_sync(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """Exécute une requête synchrone."""
        if not self.sync_connection:
            self.connect_sync()
        
        cursor = self.sync_connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.sync_connection.commit()
                return []
                
        except Exception as e:
            self.sync_connection.rollback()
            raise e
        finally:
            cursor.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé de la base de données."""
        try:
            # Test de connexion
            start_time = datetime.now()
            result = await self.execute_query("SELECT version(), NOW()")
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            
            if result:
                version_info = result[0][0]
                current_time = result[0][1]
                
                return {
                    'status': 'healthy',
                    'version': version_info,
                    'current_time': current_time,
                    'response_time_seconds': response_time,
                    'pool_size': len(self.pool._holders) if self.pool else 0,
                    'connected': self.connected
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'No response from database'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connected': self.connected
            }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Récupère des statistiques de la base de données."""
        try:
            # Nombre d'entreprises
            enterprises_count = await self.execute_query("SELECT COUNT(*) FROM entreprises")
            
            # Nombre de sessions
            sessions_count = await self.execute_query("SELECT COUNT(*) FROM sessions_exploration")
            
            # Nombre de logs
            logs_count = await self.execute_query("SELECT COUNT(*) FROM exploration_logs")
            
            # Dernière activité
            last_activity = await self.execute_query(
                "SELECT MAX(date_executed) FROM exploration_logs"
            )
            
            return {
                'enterprises_count': enterprises_count[0][0] if enterprises_count else 0,
                'sessions_count': sessions_count[0][0] if sessions_count else 0,
                'logs_count': logs_count[0][0] if logs_count else 0,
                'last_activity': last_activity[0][0] if last_activity and last_activity[0][0] else None,
                'status': 'operational'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            } 