"""
Repository pour les matières premières
"""
from typing import List, Optional
from repositories.base_repository import BaseRepository
from repositories.storage_strategies import StorageStrategy
from models.matieres import Matiere
from lib.paths import get_reference_file
import json


class MatieresPremieresRepository(BaseRepository[Matiere]):
    """
    Repository pour les matières premières avec méthodes métier spécifiques
    """

    def __init__(self, storage: StorageStrategy):
        super().__init__(Matiere, storage, id_field="code_mp")

    def get_matieres_list(self) -> List[Matiere]:
        """
        Récupère toutes les matières premières

        Returns:
            List[Matiere]: Une liste de matières premières
        """
        return self.get_all()

    def get_matiere_by_code(self, code_mp: str) -> Optional[Matiere]:
        """
        Récupère une matière première par son code

        Args:
            code_mp: Le code de la matière première

        Returns:
            Optional[Matiere]: La matière première ou None si non trouvée
        """
        return self.get_by_id(code_mp)

    def get_matiere_by_name(self, nom: str) -> Optional[Matiere]:
        """
        Récupère une matière première par son nom

        Args:
            nom: Le nom de la matière première

        Returns:
            Optional[Matiere]: La matière première ou None si non trouvée
        """
        matieres = self.get_all()
        for matiere in matieres:
            if matiere.nom == nom:
                return matiere
        return None

    def from_name(self, name: str) -> Matiere:
        """
        Recherche une matière par nom dans le fichier de référence

        Args:
            name: Le nom de la matière

        Returns:
            Matiere: La matière trouvée ou une matière par défaut
        """
        try:
            matieres_file = get_reference_file("matieres.json")
            with open(matieres_file, "r", encoding="utf-8") as file:
                matieres = json.load(file)
            for matiere in matieres:
                if matiere["nom"] == name:
                    return Matiere(**matiere)
            return Matiere(code_mp="TOBEDEFINED", nom=name)
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Erreur lors de la recherche de matière par nom: {e}")
            return Matiere(code_mp="TOBEDEFINED", nom=name)

    def from_code_mp(self, code_mp: str) -> Matiere:
        """
        Recherche une matière par code dans le fichier de référence

        Args:
            code_mp: Le code de la matière

        Returns:
            Matiere: La matière trouvée ou une matière par défaut
        """
        try:
            matieres_file = get_reference_file("matieres.json")
            with open(matieres_file, "r", encoding="utf-8") as file:
                matieres = json.load(file)
            for matiere in matieres:
                if matiere["code_mp"] == code_mp:
                    return Matiere(**matiere)
            return Matiere(code_mp=code_mp, nom="TOBEDEFINED")
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Erreur lors de la recherche de matière par code: {e}")
            return Matiere(code_mp=code_mp, nom="TOBEDEFINED")

    def import_from_json(self, json_path: str = "data/matieres.json") -> None:
        """
        Importe les matières depuis un fichier JSON

        Args:
            json_path: Chemin vers le fichier JSON
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Créer les objets Matiere depuis les données JSON
            for item in data:
                matiere = Matiere(**item)
                self.create(matiere)
        except FileNotFoundError:
            print(f"Fichier {json_path} non trouvé")
        except json.JSONDecodeError:
            print(f"Erreur lors du décodage JSON du fichier {json_path}")

    def search_by_nom(self, nom: str) -> List[Matiere]:
        """
        Recherche des matières par nom (recherche partielle)

        Args:
            nom: Nom ou partie du nom à rechercher

        Returns:
            List[Matiere]: Liste des matières correspondantes
        """
        matieres = self.get_all()
        return [matiere for matiere in matieres if nom.lower() in matiere.nom.lower()]

    def get_matieres_seveso(self) -> List[Matiere]:
        """
        Récupère toutes les matières SEVESO

        Returns:
            List[Matiere]: Liste des matières SEVESO
        """
        matieres = self.get_all()
        return [matiere for matiere in matieres if matiere.seveso]

    def get_matieres_by_type(self, type_matiere: str) -> List[Matiere]:
        """
        Récupère les matières par type

        Args:
            type_matiere: Type de matière à rechercher

        Returns:
            List[Matiere]: Liste des matières du type spécifié
        """
        matieres = self.get_all()
        return [matiere for matiere in matieres if matiere.type_matiere and matiere.type_matiere.value == type_matiere]

    def get_by_code_mp(self, code_mp: str) -> Optional[Matiere]:
        """
        Alias pour get_matiere_by_code pour la compatibilité

        Args:
            code_mp: Code de la matière première

        Returns:
            Optional[Matiere]: La matière première ou None si non trouvée
        """
        return self.get_matiere_by_code(code_mp)
