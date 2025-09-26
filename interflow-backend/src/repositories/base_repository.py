"""
Repository de base avec pattern Strategy pour le stockage
"""
from typing import TypeVar, Generic, List, Optional, Dict, Any
from models.matieres import Matiere
from models.besoin import Besoin
from models.stock import Stock
from models.reception import Reception
import csv
from pathlib import Path
from lib.decoders.decoder import Decoder

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    Repository de base avec pattern Strategy
    """

    def __init__(self, model_class: type, storage, id_field: str = "id"):
        """
        Initialise le repository

        Args:
            model_class: Classe du modèle
            storage: Stratégie de stockage
            id_field: Nom du champ ID
        """
        self.model_class = model_class
        self.storage = storage
        self.id_field = id_field
        self.data: List[T] = []
        self._load_data()

    def _get_file_path(self) -> str:
        """Retourne le chemin du fichier de données"""
        from lib.paths import get_repository_file
        model_name = self.model_class.__name__.lower()
        return str(get_repository_file(f"{model_name}s"))

    def _load_data(self) -> None:
        """Charge les données depuis le stockage"""
        try:
            file_path = self._get_file_path()
            raw_data = self.storage.load(file_path)
            self.data = [self.model_class.from_model_dump(item) for item in raw_data]
        except FileNotFoundError:
            self.data = []
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            self.data = []

    def _save_data(self) -> None:
        """Sauvegarde les données vers le stockage"""
        try:
            file_path = self._get_file_path()
            raw_data = [item.model_dump() for item in self.data]
            self.storage.save(raw_data, file_path)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")

    def get_all(self) -> List[T]:
        """Récupère tous les éléments"""
        return self.data.copy()

    def get_by_id(self, id_value: Any) -> Optional[T]:
        """Récupère un élément par son ID"""
        for item in self.data:
            if getattr(item, self.id_field) == id_value:
                return item
        return None

    def create(self, item: T) -> T:
        """Crée un nouvel élément"""
        # Vérifier si l'ID existe déjà
        item_id = getattr(item, self.id_field)
        if item_id and self.get_by_id(item_id):
            raise ValueError(f"Un élément avec l'ID {item_id} existe déjà")

        self.data.append(item)
        self._save_data()
        return item

    def update(self, id_value: Any, updated_item: T) -> Optional[T]:
        """Met à jour un élément"""
        for i, item in enumerate(self.data):
            if getattr(item, self.id_field) == id_value:
                self.data[i] = updated_item
                self._save_data()
                return updated_item
        return None

    def delete(self, id_value: Any) -> bool:
        """Supprime un élément"""
        for i, item in enumerate(self.data):
            if getattr(item, self.id_field) == id_value:
                del self.data[i]
                self._save_data()
                return True
        return False

    def filter(self, **kwargs) -> List[T]:
        """Filtre les éléments selon les critères"""
        filtered_data = self.data

        for key, value in kwargs.items():
            if value is not None:
                filtered_data = [
                    item for item in filtered_data
                    if hasattr(item, key) and getattr(item, key) == value
                ]

        return filtered_data

    def flush(self) -> None:
        """Vide toutes les données et sauvegarde la liste vide"""
        self.data = []
        self._save_data()  # Sauvegarder la liste vide
        self.storage.flush()
        print(f"✓ Repository {self.model_class.__name__} vidé avec succès")

    def import_from_file(self, file_path: str, decoder_class: Decoder) -> None:
        """
        Importe les données depuis un fichier (CSV ou XLSX)

        Args:
            file_path: Chemin vers le fichier à importer
            decoder_class: Classe du décodeur à utiliser
        """
        try:
            file_extension = Path(file_path).suffix.lower()
            import inspect
            sig = inspect.signature(decoder_class.decode_file)

            # Instancier le décodeur
            decoder = decoder_class()

            # Convertir le chemin en Path
            file_path_obj = Path(file_path)

            # Décoder selon le type de fichier
            if file_extension == '.csv':
                if 'csv_path' in sig.parameters:
                    decoded_items = decoder.decode_file([], csv_path=file_path)
                else:
                    decoded_items = decoder.decode_file(file_path_obj)

            elif file_extension == '.xlsx':
                try:
                    if 'xlsx_path' in sig.parameters:
                        decoded_items = decoder.decode_file([], xlsx_path=file_path)
                    else:
                        decoded_items = decoder.decode_file(file_path_obj)

                except ImportError:
                    raise ImportError("pandas requis pour XLSX. Installez: pip install pandas openpyxl")
                except Exception as e:
                    raise Exception(f"Erreur lecture XLSX: {e}")
            else:
                raise ValueError(f"Type de fichier non supporté: {file_extension}. Utilisez .csv ou .xlsx")

            # Ajouter les éléments décodés
            items_added = 0
            items_ignored = 0

            for item in decoded_items:
                try:
                    item_id = getattr(item, self.id_field)
                    if item_id and self.get_by_id(item_id):
                        items_ignored += 1
                        continue

                    self.data.append(item)
                    items_added += 1

                except Exception as e:
                    print(f"Erreur lors de l'import de l'élément: {e}")
                    continue

            # Sauvegarder si des éléments ont été ajoutés
            if items_added > 0:
                self._save_data()

            print(f"✓ {items_added} éléments importés depuis {file_path}")
            if items_ignored > 0:
                print(f"⚠ {items_ignored} éléments ignorés (déjà existants)")

        except FileNotFoundError:
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        except Exception as e:
            print(f"Erreur lors de l'import: {e}")
            raise e

    def import_from_csv(self, csv_path: str, decoder_class: Decoder) -> None:
        """Importe depuis CSV (compatibilité)"""
        self.import_from_file(csv_path, decoder_class)

    def import_from_xlsx(self, xlsx_path: str, decoder_class: Decoder) -> None:
        """Importe depuis XLSX (compatibilité)"""
        self.import_from_file(xlsx_path, decoder_class)




    def count(self) -> int:
        """Retourne le nombre d'éléments"""
        return len(self.data)

    def exists(self, id_value: Any) -> bool:
        """Vérifie si un élément existe"""
        return self.get_by_id(id_value) is not None
