"""
Interface et implémentations pour les décodeurs de fichiers
"""
from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from typing import TypeVar, Generic

T = TypeVar('T')

class Decoder(ABC, Generic[T]):
    """
    Interface pour les décodeurs de fichiers
    """

    @abstractmethod
    def decode_row(self, row: dict) -> T:
        """
        Décode une ligne en objet T

        Args:
            row: Dictionnaire représentant une ligne de données

        Returns:
            T: L'objet T créé
        """
        pass

    @abstractmethod
    def decode_file(self, file_path: Path) -> List[T]:
        """
        Décode un fichier en liste d'éléments

        Args:
            file_path: Chemin vers le fichier à décoder

        Returns:
            List[T]: Liste des éléments créés
        """
        pass
