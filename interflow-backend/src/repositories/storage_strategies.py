"""
Stratégies de stockage pour les repositories
"""
import json
import sqlite3
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from pathlib import Path
import logging
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class StorageStrategy(ABC):
    """
    Interface pour les stratégies de stockage
    """

    @abstractmethod
    def save(self, data: List[Dict[str, Any]], file_path: str) -> None:
        """Sauvegarde les données"""
        pass

    @abstractmethod
    def load(self, file_path: str) -> List[Dict[str, Any]]:
        """Charge les données"""
        pass

    @abstractmethod
    def flush(self) -> None:
        """Vide les données"""
        pass


class JSONStorageStrategy(StorageStrategy):
    """
    Stratégie de stockage en JSON
    """

    def save(self, data: List[Dict[str, Any]], file_path: str) -> None:
        """Sauvegarde les données en JSON"""
        try:
            # Créer le répertoire parent si nécessaire
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with open(f"{file_path}.json", 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde JSON: {e}")

    def load(self, file_path: str) -> List[Dict[str, Any]]:
        """Charge les données depuis un fichier JSON"""
        try:
            with open(f"{file_path}.json", 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Erreur lors du chargement JSON: {e}")
            return []

    def flush(self) -> None:
        """Vide les données en supprimant le fichier JSON"""
        # Dans un contexte de flush, on n'a pas accès au file_path
        # donc on ne peut pas supprimer le fichier directement ici
        # Cette méthode sera appelée avec un file_path par BaseRepository
        pass


class CSVStorageStrategy(StorageStrategy):
    """
    Stratégie de stockage en CSV
    """

    def save(self, data: List[Dict[str, Any]], file_path: str) -> None:
        """Sauvegarde les données en CSV"""
        try:
            import csv

            # Créer le répertoire parent si nécessaire
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            if data:
                fieldnames = data[0].keys()
                with open(f"{file_path}.csv", 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde CSV: {e}")

    def load(self, file_path: str) -> List[Dict[str, Any]]:
        """Charge les données depuis un fichier CSV"""
        try:
            import csv

            with open(f"{file_path}.csv", 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return list(reader)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Erreur lors du chargement CSV: {e}")
            return []

    def flush(self) -> None:
        """Vide les données (pas d'action nécessaire pour CSV)"""
        pass


class SQLiteStorageStrategy(StorageStrategy):
    """
    Stratégie de stockage en SQLite pour de meilleures performances avec de gros volumes
    """
    
    def __init__(self):
        """Initialise la stratégie SQLite"""
        self.connection = None
        self.current_file_path = None
    
    def _get_connection(self, file_path: str) -> sqlite3.Connection:
        """
        Obtient une connexion à la base SQLite
        
        Args:
            file_path: Chemin vers le fichier de base de données
            
        Returns:
            sqlite3.Connection: Connexion à la base
        """
        # Si on a déjà une connexion pour ce fichier, la réutiliser
        if self.connection and self.current_file_path == file_path:
            return self.connection
            
        # Créer le répertoire parent si nécessaire
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Fermer l'ancienne connexion si elle existe
        if self.connection:
            self.connection.close()
            
        # Créer une nouvelle connexion
        self.connection = sqlite3.connect(file_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Pour avoir des dictionnaires
        self.current_file_path = file_path
        
        return self.connection
    
    def _create_table(self, file_path: str, table_name: str, data: List[Dict[str, Any]]) -> None:
        """
        Crée la table SQLite basée sur la structure des données
        
        Args:
            file_path: Chemin vers le fichier de base de données
            table_name: Nom de la table
            data: Données pour déterminer la structure
        """
        if not data:
            return
            
        conn = self._get_connection(file_path)
        cursor = conn.cursor()
        
        # Analyser la structure des données pour créer la table
        sample_item = data[0]
        columns = []
        
        for key, value in sample_item.items():
            if isinstance(value, bool):
                col_type = "INTEGER"
            elif isinstance(value, int):
                col_type = "INTEGER"
            elif isinstance(value, float):
                col_type = "REAL"
            elif isinstance(value, str):
                col_type = "TEXT"
            else:
                col_type = "TEXT"  # Fallback pour les autres types
                
            columns.append(f'"{key}" {col_type}')
        
        # Créer la table
        create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n' + ',\n'.join(columns) + '\n)'
        cursor.execute(create_sql)
        
        # Créer un index sur l'ID si il existe
        if 'id' in sample_item:
            cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_id ON "{table_name}" (id)')
        
        conn.commit()
    
    def save(self, data: List[Dict[str, Any]], file_path: str) -> None:
        """Sauvegarde les données en SQLite"""
        try:
            if not data:
                return
                
            # Déterminer le nom de la table à partir du nom du fichier
            table_name = Path(f"{file_path}.db").stem
            
            # Créer la table
            self._create_table(f"{file_path}.db", table_name, data)
            
            conn = self._get_connection(f"{file_path}.db")
            cursor = conn.cursor()
            
            # Vider la table existante
            cursor.execute(f'DELETE FROM "{table_name}"')
            
            # Préparer les colonnes et les valeurs
            columns = list(data[0].keys())
            placeholders = ', '.join(['?' for _ in columns])
            columns_str = ', '.join([f'"{col}"' for col in columns])
            
            insert_sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})'
            
            # Insérer les données par batch pour de meilleures performances
            batch_size = 1000
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                batch_values = []
                
                for item in batch:
                    values = []
                    for col in columns:
                        value = item.get(col)
                        # Convertir les objets complexes en JSON
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value, default=str)
                        elif hasattr(value, 'model_dump'):  # Objets Pydantic
                            value = json.dumps(value.model_dump(), default=str)
                        elif value is None:
                            value = None
                        else:
                            value = str(value)
                        values.append(value)
                    batch_values.append(tuple(values))
                
                cursor.executemany(insert_sql, batch_values)
            
            conn.commit()
            logger.info(f"✅ {len(data)} enregistrements sauvegardés dans SQLite: {file_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde SQLite: {e}")
            raise
    
    def load(self, file_path: str) -> List[Dict[str, Any]]:
        """Charge les données depuis une base SQLite"""
        try:
            if not Path(f"{file_path}.db").exists():
                return []
                
            table_name = Path(f"{file_path}.db").stem
            conn = self._get_connection(f"{file_path}.db")
            cursor = conn.cursor()
            
            # Vérifier que la table existe
            cursor.execute(f'SELECT name FROM sqlite_master WHERE type="table" AND name="{table_name}"')
            if not cursor.fetchone():
                return []
            
            # Charger toutes les données
            cursor.execute(f'SELECT * FROM "{table_name}"')
            rows = cursor.fetchall()
            
            # Convertir les Row en dictionnaires
            data = []
            for row in rows:
                item = dict(row)
                # Essayer de parser les champs JSON
                for key, value in item.items():
                    if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                        try:
                            item[key] = json.loads(value)
                        except json.JSONDecodeError:
                            pass  # Garder la valeur string si ce n'est pas du JSON valide
                data.append(item)
            
            logger.info(f"✅ {len(data)} enregistrements chargés depuis SQLite: {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement SQLite: {e}")
            return []
    
    def flush(self) -> None:
        """Vide les données en supprimant le fichier SQLite"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.current_file_path = None
    
    def __del__(self):
        """Fermer la connexion lors de la destruction de l'objet"""
        if self.connection:
            self.connection.close()


class S3StorageStrategy(StorageStrategy):
    """
    Stratégie de stockage en S3 pour les rappatriements
    """
    
    def __init__(self, bucket_name: str = None, region_name: str = None):
        """
        Initialise la stratégie S3
        
        Args:
            bucket_name: Nom du bucket S3 (optionnel, sera extrait de S3_RAPPATRIMENT_FILE_PATH)
            region_name: Région AWS (obligatoire via env var AWS_REGION)
            
        Raises:
            ValueError: Si les variables d'environnement requises ne sont pas définies
        """
        # Récupérer le chemin S3 complet
        s3_path = os.environ.get('S3_RAPPATRIMENT_FILE_PATH')
        if not s3_path:
            raise ValueError(
                "S3_RAPPATRIMENT_FILE_PATH est obligatoire. "
                "Définissez la variable d'environnement S3_RAPPATRIMENT_FILE_PATH."
            )
        
        # Extraire le bucket et la clé du chemin S3
        if s3_path.startswith('s3://'):
            # Format: s3://bucket/key
            path_without_prefix = s3_path[5:]  # Enlever s3://
            if '/' in path_without_prefix:
                self.bucket_name, self.s3_key = path_without_prefix.split('/', 1)
            else:
                self.bucket_name = path_without_prefix
                self.s3_key = 'rappatriements.json'  # Valeur par défaut
        else:
            # Si ce n'est pas un chemin S3 complet, utiliser S3_BUCKET_NAME
            self.bucket_name = bucket_name or os.environ.get('S3_BUCKET_NAME')
            self.s3_key = s3_path
            if not self.bucket_name:
                raise ValueError(
                    "S3_BUCKET_NAME est obligatoire quand S3_RAPPATRIMENT_FILE_PATH n'est pas un chemin S3 complet. "
                    "Définissez la variable d'environnement S3_BUCKET_NAME ou utilisez un chemin S3 complet."
                )
        
        # Validation de la région
        self.region_name = region_name or os.environ.get('AWS_REGION')
        if not self.region_name:
            raise ValueError(
                "AWS_REGION est obligatoire. "
                "Définissez la variable d'environnement AWS_REGION ou passez region_name en paramètre."
            )
        
        # Initialiser le client S3 (utilise les credentials par défaut d'AWS)
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region_name
            )
            logger.info(f"✅ Client S3 initialisé pour le bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.error("❌ Credentials AWS non trouvés")
            raise
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation S3: {e}")
            raise
    
    def _get_s3_key(self, file_path: str) -> str:
        """
        Retourne la clé S3 extraite lors de l'initialisation
        
        Args:
            file_path: Chemin du fichier local (non utilisé, gardé pour compatibilité)
            
        Returns:
            str: Clé S3
        """
        return self.s3_key
    
    def _ensure_bucket_exists(self) -> None:
        """
        Vérifie que le bucket S3 existe, le crée si nécessaire
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.debug(f"✅ Bucket {self.bucket_name} existe déjà")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket n'existe pas, le créer
                try:
                    if self.region_name == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region_name}
                        )
                    logger.info(f"✅ Bucket {self.bucket_name} créé dans la région {self.region_name}")
                except ClientError as create_error:
                    logger.error(f"❌ Erreur lors de la création du bucket: {create_error}")
                    raise
            else:
                logger.error(f"❌ Erreur lors de la vérification du bucket: {e}")
                raise
    
    def save(self, data: List[Dict[str, Any]], file_path: str) -> None:
        """Sauvegarde les données en S3"""
        try:
            # S'assurer que le bucket existe
            self._ensure_bucket_exists()
            
            # Convertir les données en JSON
            json_data = json.dumps(data, ensure_ascii=False, indent=2, default=str)
            
            # Obtenir la clé S3
            s3_key = self._get_s3_key(file_path)
            
            # Upload vers S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json',
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"✅ {len(data)} enregistrements sauvegardés dans S3: s3://{self.bucket_name}/{s3_key}")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde S3: {e}")
            raise
    
    def load(self, file_path: str) -> List[Dict[str, Any]]:
        """Charge les données depuis S3"""
        try:
            # Obtenir la clé S3
            s3_key = self._get_s3_key(file_path)
            
            # Télécharger depuis S3
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            # Décoder le contenu JSON
            json_data = response['Body'].read().decode('utf-8')
            data = json.loads(json_data)
            
            if not isinstance(data, list):
                data = []
            
            logger.info(f"✅ {len(data)} enregistrements chargés depuis S3: s3://{self.bucket_name}/{s3_key}")
            return data
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                logger.info(f"ℹ️ Fichier S3 non trouvé: s3://{self.bucket_name}/{s3_key}")
                return []
            else:
                logger.error(f"❌ Erreur lors du chargement S3: {e}")
                return []
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement S3: {e}")
            return []
    
    def flush(self) -> None:
        """Vide les données en supprimant le fichier S3"""
        # Cette méthode sera appelée avec un file_path par BaseRepository
        # On ne peut pas supprimer ici car on n'a pas accès au file_path
        pass
    
    def delete_file(self, file_path: str) -> bool:
        """
        Supprime un fichier S3
        
        Args:
            file_path: Chemin du fichier local (utilisé pour générer la clé S3)
            
        Returns:
            bool: True si supprimé avec succès
        """
        try:
            s3_key = self._get_s3_key(file_path)
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"✅ Fichier S3 supprimé: s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de la suppression S3: {e}")
            return False
    
    def list_files(self) -> List[str]:
        """
        Liste tous les fichiers de rappatriements dans S3
        
        Returns:
            List[str]: Liste des clés S3
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='rappatriements/'
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append(obj['Key'])
            
            return files
        except Exception as e:
            logger.error(f"❌ Erreur lors de la liste des fichiers S3: {e}")
            return []

