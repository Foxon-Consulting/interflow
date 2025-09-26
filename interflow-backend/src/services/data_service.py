"""
Service pour la gestion des données de base
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tempfile
import os
from pathlib import Path

from repositories import (
    BesoinsRepository,
    StocksRepository,
    ReceptionsRepository,
    RappatriementsRepository,
    MatieresPremieresRepository,
    create_json_repository
)
from repositories.storage_strategies import JSONStorageStrategy
from models.besoin import Besoin
from models.stock import Stock
from models.reception import Reception, EtatReception, TypeReception
from models.rappatriement import Rappatriement
from models.matieres import Matiere
from lib.paths import ProjectPaths, get_input_file, get_reference_file


class DataService:
    """
    Service unifié pour la gestion des données de base
    Encapsule les opérations CRUD sur les repositories et le rechargement depuis les fichiers
    """

    def __init__(self):
        """
        Initialise le service avec les repositories
        """
        self.paths = ProjectPaths()

        # Créer les repositories avec la stratégie de stockage JSON
        storage_strategy = JSONStorageStrategy()

        self.besoins_repo = BesoinsRepository(storage_strategy)
        self.stocks_repo = StocksRepository(storage_strategy)
        self.receptions_repo = ReceptionsRepository(storage_strategy)
        self.rappatriements_repo = RappatriementsRepository(storage_strategy)
        self.matieres_repo = MatieresPremieresRepository(storage_strategy)

        # Créer les repositories pour le rechargement (avec create_json_repository)
        self.stock_reload_repo = create_json_repository(StocksRepository)
        self.reception_reload_repo = create_json_repository(ReceptionsRepository)
        self.besoins_reload_repo = create_json_repository(BesoinsRepository)
        self.matieres_reload_repo = create_json_repository(MatieresPremieresRepository)


    def import_besoins(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Importe les besoins depuis un fichier CSV ou XLSX en flushing d'abord le repository

        Args:
            file_path: Chemin vers le fichier temporaire
            filename: Nom du fichier original

        Returns:
            Dict contenant le résumé de l'import
        """
        try:
            # Compter les besoins avant le flush
            besoins_avant = self.besoins_repo.count()

            # Flush le repository pour vider toutes les données existantes
            self.besoins_repo.flush()

            # Importer le fichier
            self.besoins_repo.import_from_file(file_path)

            # Compter les besoins après l'import
            besoins_apres = self.besoins_repo.count()

            return {
                "message": "Import des besoins réussi",
                "filename": filename,
                "besoins_avant_flush": besoins_avant,
                "besoins_importes": besoins_apres,
                "statut": "success"
            }

        except Exception as e:
            return {
                "message": f"Erreur lors de l'import des besoins: {str(e)}",
                "filename": filename,
                "statut": "error"
            }

    def import_receptions(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Importe les réceptions depuis un fichier CSV ou XLSX en flushing d'abord le repository

        Args:
            file_path: Chemin vers le fichier temporaire
            filename: Nom du fichier original

        Returns:
            Dict contenant le résumé de l'import
        """
        try:
            # Compter les réceptions avant le flush
            receptions_avant = self.receptions_repo.count()

            # Flush le repository pour vider toutes les données existantes
            self.receptions_repo.flush()

            # Importer le fichier
            self.receptions_repo.import_from_file(file_path)

            # Compter les réceptions après l'import
            receptions_apres = self.receptions_repo.count()

            return {
                "message": "Import des réceptions réussi",
                "filename": filename,
                "receptions_avant_flush": receptions_avant,
                "receptions_importees": receptions_apres,
                "statut": "success"
            }

        except Exception as e:
            return {
                "message": f"Erreur lors de l'import des réceptions: {str(e)}",
                "filename": filename,
                "statut": "error"
            }

    def import_stocks(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Importe les stocks depuis un fichier CSV ou XLSX en flushing d'abord le repository

        Args:
            file_path: Chemin vers le fichier temporaire
            filename: Nom du fichier original

        Returns:
            Dict contenant le résumé de l'import
        """
        try:
            # Compter les stocks avant le flush
            stocks_avant = self.stocks_repo.count()

            # Flush le repository pour vider toutes les données existantes
            self.stocks_repo.flush()

            # Importer le fichier
            self.stocks_repo.import_from_file(file_path)

            # Compter les stocks après l'import
            stocks_apres = self.stocks_repo.count()

            return {
                "message": "Import des stocks réussi",
                "filename": filename,
                "stocks_avant_flush": stocks_avant,
                "stocks_importes": stocks_apres,
                "statut": "success"
            }

        except Exception as e:
            return {
                "message": f"Erreur lors de l'import des stocks: {str(e)}",
                "filename": filename,
                "statut": "error"
            }

    def import_rappatriements(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Importe les rapatriements depuis un fichier CSV ou XLSX en flushing d'abord le repository

        Args:
            file_path: Chemin vers le fichier temporaire
            filename: Nom du fichier original

        Returns:
            Dict contenant le résumé de l'import
        """
        try:
            # Compter les rapatriements avant le flush
            rapatriements_avant = self.rappatriements_repo.count()

            # Flush le repository pour vider toutes les données existantes
            self.rappatriements_repo.flush()

            # Importer le fichier
            self.rappatriements_repo.import_from_file(file_path)

            # Compter les rapatriements après l'import
            rapatriements_apres = self.rappatriements_repo.count()

            return {
                "message": "Import des rapatriements réussi",
                "filename": filename,
                "rappatriements_avant_flush": rapatriements_avant,
                "rappatriements_importes": rapatriements_apres,
                "statut": "success"
            }

        except Exception as e:
            return {
                "message": f"Erreur lors de l'import des rapatriements: {str(e)}",
                "filename": filename,
                "statut": "error"
            }

    def append_rappatriements(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Ajoute des rapatriements depuis un fichier CSV ou XLSX sans vider le repository existant

        Args:
            file_path: Chemin vers le fichier temporaire
            filename: Nom du fichier original

        Returns:
            Dict contenant le résumé de l'ajout
        """
        try:
            # Compter les rapatriements avant l'ajout
            rapatriements_avant = self.rappatriements_repo.count()

            # Importer le fichier sans flush (ajout seulement)
            rapatriements_ajoutes = self.rappatriements_repo.import_from_file(file_path)

            # Compter les rapatriements après l'ajout
            rapatriements_apres = self.rappatriements_repo.count()
            rapatriements_nouveaux = rapatriements_apres - rapatriements_avant

            return {
                "message": "Ajout des rapatriements réussi",
                "filename": filename,
                "rappatriements_avant_ajout": rapatriements_avant,
                "rappatriements_ajoutes": rapatriements_nouveaux,
                "rappatriements_total": rapatriements_apres,
                "statut": "success"
            }

        except Exception as e:
            return {
                "message": f"Erreur lors de l'ajout des rapatriements: {str(e)}",
                "filename": filename,
                "statut": "error"
            }

    def reload_from_date(self, date: datetime) -> bool:
        """
        Recharge tous les repositories depuis les fichiers CSV/JSON d'une date donnée

        Args:
            date: Date pour laquelle charger les fichiers (format: YYYY-MM-DD)

        Returns:
            bool: True si les 3 fichiers CSV ont été rechargés avec succès, False sinon
        """
        # Construire les chemins des fichiers
        stock_file = get_input_file("csv/stocks.csv", date.strftime("%Y-%m-%d"))
        reception_file = get_input_file("csv/receptions.csv", date.strftime("%Y-%m-%d"))
        besoins_file = get_input_file("csv/besoins.csv", date.strftime("%Y-%m-%d"))
        matieres_file = get_reference_file("matieres.json")

        # Vérifier l'existence des 3 CSV obligatoires
        missing = []
        if not stock_file.exists():
            missing.append(str(stock_file))
        if not reception_file.exists():
            missing.append(str(reception_file))
        if not besoins_file.exists():
            missing.append(str(besoins_file))
        if missing:
            print("❌ Les fichiers CSV suivants sont manquants :")
            for f in missing:
                print(f"   - {f}")
            return False

        # Préparer la liste des fichiers à charger
        files_to_load = self._prepare_files_list(stock_file, reception_file, besoins_file, matieres_file)

        # Vider tous les repositories avant le rechargement
        self._flush_all_repositories()

        # Recharger d'abord les fichiers JSON (matières)
        json_files = [(name, file_path, repo) for name, file_path, repo in files_to_load if name == "matières"]
        self._load_files(json_files)

        # Recharger les fichiers CSV
        csv_files = [(name, file_path, repo) for name, file_path, repo in files_to_load if name != "matières"]
        csv_success_count = self._load_files(csv_files)

        # On considère le rechargement réussi si les 3 CSV ont été rechargés
        return csv_success_count == 3

    def _prepare_files_list(self, stock_file: Path, reception_file: Path,
                           besoins_file: Path, matieres_file: Path) -> List[Tuple[str, Path, object]]:
        """
        Prépare la liste des fichiers à charger avec leurs repositories associés

        Args:
            stock_file: Chemin du fichier stocks.csv
            reception_file: Chemin du fichier receptions.csv
            besoins_file: Chemin du fichier besoins.csv
            matieres_file: Chemin du fichier matieres.json

        Returns:
            List[Tuple[str, Path, object]]: Liste des (nom, fichier, repository) à charger
        """
        files_to_load = []

        if stock_file.exists():
            files_to_load.append(("stocks", stock_file, self.stock_reload_repo))
        else:
            print(f"⚠️  Le fichier {stock_file} n'existe pas")

        if reception_file.exists():
            files_to_load.append(("receptions", reception_file, self.reception_reload_repo))
        else:
            print(f"⚠️  Le fichier {reception_file} n'existe pas")

        if besoins_file.exists():
            files_to_load.append(("besoins", besoins_file, self.besoins_reload_repo))
        else:
            print(f"⚠️  Le fichier {besoins_file} n'existe pas")

        if matieres_file.exists():
            files_to_load.append(("matières", matieres_file, self.matieres_reload_repo))
        else:
            print(f"⚠️  Le fichier {matieres_file} n'existe pas")

        return files_to_load

    def _flush_all_repositories(self) -> None:
        """Vide tous les repositories avant le rechargement"""
        self.stock_reload_repo.flush()
        self.reception_reload_repo.flush()
        self.besoins_reload_repo.flush()
        self.matieres_reload_repo.flush()

    def _load_files(self, files_to_load: List[Tuple[str, Path, object]]) -> int:
        """
        Charge les fichiers dans leurs repositories respectifs

        Args:
            files_to_load: Liste des (nom, fichier, repository) à charger

        Returns:
            int: Nombre de fichiers chargés avec succès
        """
        success_count = 0

        for name, file_path, repo in files_to_load:
            try:
                if name == "matières":
                    repo.import_from_json(file_path)
                else:
                    repo.import_from_file(file_path)
                print(f"✅ {name.capitalize()} rechargé depuis {file_path}")
                success_count += 1
            except Exception as e:
                print(f"❌ Erreur lors du rechargement de {name}: {e}")
                # On pourrait lever une exception ici si on veut arrêter complètement
                # raise RuntimeError(f"Erreur fatale lors du rechargement de {name}: {e}")

        return success_count

    def get_repositories(self) -> Tuple[object, object, object, object]:
        """
        Retourne les repositories pour utilisation externe

        Returns:
            Tuple: (stock_repo, reception_repo, besoins_repo, matieres_repo)
        """
        return self.stock_reload_repo, self.reception_reload_repo, self.besoins_reload_repo, self.matieres_reload_repo
