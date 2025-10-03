"""
Service pour la gestion des données de base
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tempfile
import os
from pathlib import Path
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from repositories import (
    BesoinsRepository,
    StocksRepository,
    ReceptionsRepository,
    RappatriementsRepository,
    MatieresPremieresRepository,
    JSONStorageStrategy,
    SQLiteStorageStrategy,
    S3StorageStrategy
)

from lib.paths import ProjectPaths, get_input_file, get_reference_file
from dotenv import load_dotenv

load_dotenv()


class DataService:
    """
    Service unifié pour la gestion des données de base
    Encapsule les opérations CRUD sur les repositories et le rechargement depuis les fichiers
    Singleton pour garantir la cohérence des données
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """
        Implémentation du pattern Singleton
        Garantit qu'une seule instance de DataService existe
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialise le service avec les repositories
        Ne s'exécute qu'une seule fois grâce au pattern Singleton
        """
        # Éviter la réinitialisation multiple
        if self._initialized:
            return
            
        self.paths = ProjectPaths()

        # Créer les repositories avec la stratégie appropriée
        storage_strategy_name = os.environ.get("STORAGE_STRATEGY", "sqlite")
        
        if storage_strategy_name == "sqlite":
            storage_strategy = SQLiteStorageStrategy()
        else:
            storage_strategy = JSONStorageStrategy()
        
        # Stratégie spéciale pour les rappatriements (S3)
        rappatriements_storage_strategy = S3StorageStrategy()
        
        self.besoins_repo = BesoinsRepository(storage_strategy)
        self.stocks_repo = StocksRepository(storage_strategy)
        self.receptions_repo = ReceptionsRepository(storage_strategy)
        self.rappatriements_repo = RappatriementsRepository(rappatriements_storage_strategy)
        self.matieres_repo = MatieresPremieresRepository(storage_strategy)
        
        # Marquer comme initialisé
        self._initialized = True


    def _download_file_from_s3(self, s3_path: str) -> str:
        """
        Télécharge un fichier depuis un bucket S3
        
        Args:
            s3_path: Chemin vers le fichier dans le bucket S3 (format: s3://bucket/path/to/file.xlsx)
            
        Returns:
            str: Chemin local vers le fichier téléchargé
            
        Raises:
            ValueError: Si le chemin S3 n'est pas valide
            NoCredentialsError: Si les credentials AWS ne sont pas configurés
            ClientError: Si une erreur survient lors du téléchargement
        """
        # Valider le format du chemin S3
        if not s3_path.startswith('s3://'):
            raise ValueError(f"Le chemin S3 doit commencer par 's3://', reçu: {s3_path}")
        
        # Parser le chemin S3
        try:
            # Enlever le préfixe s3://
            path_without_prefix = s3_path[5:]
            # Séparer le bucket et la clé
            bucket_name, object_key = path_without_prefix.split('/', 1)
        except ValueError:
            raise ValueError(f"Format de chemin S3 invalide: {s3_path}")
        
        # Créer un fichier temporaire
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(object_key).suffix)
        temp_file_path = temp_file.name
        temp_file.close()
        
        try:
            # Créer le client S3
            s3_client = boto3.client('s3')
            
            # Télécharger le fichier
            s3_client.download_file(bucket_name, object_key, temp_file_path)
            
            return temp_file_path
            
        except NoCredentialsError:
            # Nettoyer le fichier temporaire en cas d'erreur
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise NoCredentialsError("Les credentials AWS ne sont pas configurés. "
                                   "Veuillez configurer AWS_ACCESS_KEY_ID et AWS_SECRET_ACCESS_KEY "
                                   "ou utiliser un profil AWS.")
        except ClientError as e:
            # Nettoyer le fichier temporaire en cas d'erreur
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise ClientError(
                    error_response={'Error': {'Code': 'NoSuchBucket', 
                                            'Message': f"Le bucket '{bucket_name}' n'existe pas"}},
                    operation_name='download_file'
                )
            elif error_code == 'NoSuchKey':
                raise ClientError(
                    error_response={'Error': {'Code': 'NoSuchKey', 
                                            'Message': f"Le fichier '{object_key}' n'existe pas dans le bucket '{bucket_name}'"}},
                    operation_name='download_file'
                )
            else:
                raise ClientError(
                    error_response={'Error': {'Code': error_code, 
                                            'Message': f"Erreur lors du téléchargement: {e.response['Error']['Message']}"}},
                    operation_name='download_file'
                )
        except Exception as e:
            # Nettoyer le fichier temporaire en cas d'erreur
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise RuntimeError(f"Erreur inattendue lors du téléchargement: {str(e)}")

    def import_besoins(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Importe les besoins depuis un fichier XLSX (flush d'abord le repository)

        Args:
            file_path: Chemin vers le fichier
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
            self.besoins_repo.import_from_file(file_path, "")

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
        
    def import_besoins_from_s3(self) -> Dict[str, Any]:
        """
        Importe les besoins depuis un fichier XLSX d'un bucket S3 (flush d'abord le repository)
        
        Returns:
            Dict contenant le résumé de l'import
        """
        s3_path = None
        try:
            # Compter les besoins avant le flush
            besoins_avant = self.besoins_repo.count()
            
            # Flush le repository pour vider toutes les données existantes
            self.besoins_repo.flush()
            
            # Récupérer le chemin S3 depuis les variables d'environnement
            s3_path = os.environ.get("S3_BESOINS_FILE_PATH")
            if not s3_path:
                raise ValueError("Variable d'environnement S3_BESOINS_FILE_PATH non définie")

            # Télécharger le fichier depuis le bucket S3 (responsabilité infrastructure)
            file_path = self._download_file_from_s3(s3_path)

            # Déléguer l'import au repository (responsabilité métier)
            self.besoins_repo.import_from_file(file_path)

            # Compter les besoins après l'import
            besoins_apres = self.besoins_repo.count()
            
            return {
                "message": "Import des besoins réussi",
                "filename": s3_path,
                "besoins_avant_flush": besoins_avant,
                "besoins_importes": besoins_apres,
                "statut": "success"
            }
        except Exception as e:
            return {
                "message": f"Erreur lors de l'import des besoins: {str(e)}",
                "filename": s3_path if s3_path else "N/A",
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

    def import_receptions_from_s3(self) -> Dict[str, Any]:
        """
        Importe les réceptions depuis un fichier CSV d'un bucket S3 (flush d'abord le repository)
        """
        s3_path = None
        try:
            # Compter les réceptions avant le flush
            receptions_avant = self.receptions_repo.count()
            
            # Flush le repository pour vider toutes les données existantes
            self.receptions_repo.flush()
            
            # Récupérer le chemin S3 depuis les variables d'environnement
            s3_path = os.environ.get("S3_RECEPTIONS_FILE_PATH")
            if not s3_path:
                raise ValueError("Variable d'environnement S3_RECEPTIONS_FILE_PATH non définie")

            # Télécharger le fichier depuis le bucket S3 (responsabilité infrastructure)
            file_path = self._download_file_from_s3(s3_path)

            # Déléguer l'import au repository (responsabilité métier)
            self.receptions_repo.import_from_file(file_path)

            # Compter les réceptions après l'import
            receptions_apres = self.receptions_repo.count()

            return {
                "message": "Import des réceptions réussi",
                "filename": s3_path,
                "receptions_avant_flush": receptions_avant,
                "receptions_importees": receptions_apres,
                "statut": "success"
            }
        except Exception as e:
            return {
                "message": f"Erreur lors de l'import des réceptions: {str(e)}",
                "filename": s3_path if s3_path else "N/A",
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
        
    def import_stocks_from_s3(self) -> Dict[str, Any]:
        """
        Importe les stocks depuis un fichier XLSX d'un bucket S3 (flush d'abord le repository)
        """
        s3_path = None
        try:
            # Compter les stocks avant le flush
            stocks_avant = self.stocks_repo.count()
            
            # Flush le repository pour vider toutes les données existantes
            self.stocks_repo.flush()
            
            # Récupérer le chemin S3 depuis les variables d'environnement
            s3_path = os.environ.get("S3_STOCKS_FILE_PATH")
            if not s3_path:
                raise ValueError("Variable d'environnement S3_STOCKS_FILE_PATH non définie")

            # Télécharger le fichier depuis le bucket S3 (responsabilité infrastructure)
            file_path = self._download_file_from_s3(s3_path)

            # Déléguer l'import au repository (responsabilité métier)
            self.stocks_repo.import_from_s3(file_path)

            # Compter les stocks après l'import
            stocks_apres = self.stocks_repo.count()

            return {
                "message": "Import des stocks réussi",
                "filename": s3_path,
                "stocks_avant_flush": stocks_avant,
                "stocks_importes": stocks_apres,
                "statut": "success"
            }

        except Exception as e:
            return {
                "message": f"Erreur lors de l'import des stocks: {str(e)}",
                "filename": s3_path if s3_path else "N/A",
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

    def get_stocks(self, matiere_code: str = None, stock_type: str = None):
        """
        Récupère les stocks avec filtres optionnels
        
        Args:
            matiere_code: Code de la matière pour filtrer
            stock_type: Type de stock ('interne' ou 'externe')
            
        Returns:
            Liste des stocks
        """
        if matiere_code:
            return self.stocks_repo.get_stocks_by_matiere(matiere_code)
        elif stock_type:
            if stock_type.lower() == "interne":
                return self.stocks_repo.get_internal_stocks()
            elif stock_type.lower() == "externe":
                return self.stocks_repo.get_external_stocks()
            else:
                raise ValueError("Type de stock invalide. Utilisez 'interne' ou 'externe'")
        else:
            return self.stocks_repo.get_all()
    
    def get_stock_by_id(self, stock_id: str):
        """Récupère un stock par son ID"""
        return self.stocks_repo.get_by_id(stock_id)
    
    def create_stock(self, stock_data: dict):
        """Crée un nouveau stock"""
        from models.stock import Stock
        stock = Stock(**stock_data)
        return self.stocks_repo.create(stock)
    
    def update_stock(self, stock_id: str, stock_data: dict):
        """Met à jour un stock existant"""
        from models.stock import Stock
        stock = Stock(**stock_data)
        return self.stocks_repo.update(stock_id, stock)
    
    def delete_stock(self, stock_id: str):
        """Supprime un stock"""
        return self.stocks_repo.delete(stock_id)
    
    def get_stocks_count(self):
        """Retourne le nombre de stocks"""
        return self.stocks_repo.count()
