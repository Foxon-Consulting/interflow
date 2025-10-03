"""
Stratégies de stockage pour les repositories
"""
import json
import sqlite3
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from pathlib import Path
import logging

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

