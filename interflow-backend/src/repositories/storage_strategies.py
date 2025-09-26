"""
Stratégies de stockage pour les repositories
"""
import json
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from pathlib import Path


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

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde JSON: {e}")

    def load(self, file_path: str) -> List[Dict[str, Any]]:
        """Charge les données depuis un fichier JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
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
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde CSV: {e}")

    def load(self, file_path: str) -> List[Dict[str, Any]]:
        """Charge les données depuis un fichier CSV"""
        try:
            import csv

            with open(file_path, 'r', encoding='utf-8') as file:
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


# Fonction utilitaire pour créer des repositories avec stockage JSON
def create_json_repository(repository_class):
    """
    Crée une instance de repository avec stockage JSON

    Args:
        repository_class: Classe du repository à instancier

    Returns:
        Instance du repository avec stockage JSON
    """
    storage = JSONStorageStrategy()
    return repository_class(storage)
