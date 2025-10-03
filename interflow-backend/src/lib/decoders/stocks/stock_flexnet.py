"""
Décodeur pour les stocks depuis l'onglet stock_flexnet du fichier Excel
"""
from typing import List, Union, Dict, Optional
from pathlib import Path
import pandas as pd
import logging
from models.stock import Stock
from datetime import datetime
from lib.decoders.decoder import Decoder
from models.matieres import Matiere
from lib.utils import parse_date

logger = logging.getLogger(__name__)


def clean_string_value(value) -> str | None:
    """
    Nettoie une valeur pour la convertir en string valide

    Args:
        value: La valeur à nettoyer

    Returns:
        str | None: La valeur nettoyée ou None si NaN/vide
    """
    if pd.isna(value) or value is None:
        return None

    # Convertir en string et nettoyer
    value_str = str(value).strip()

    # Vérifier si c'est un NaN string
    if value_str.lower() in ['nan', 'none', 'null', '']:
        return None

    return value_str


class StockFlexnetDecoder(Decoder[Stock]):
    """
    Décodeur pour les stocks depuis l'onglet stock_flexnet du fichier Excel
    """

    def __init__(self):
        """
        Initialise le décodeur stock_flexnet
        """
        self.supported_extensions = ['.xlsx', '.xls']

        # Mapping des colonnes du format stock_flexnet
        self.column_mapping = {
            'statut_lot': [
                'IN : Inventory Status',
                'Inventory Status',
                'Statut Lot',
                'Statut'
            ],
            'article': [
                'IN : Product Number',
                'Product Number',
                'Article',
                'Code Article',
                'Référence'
            ],
            'libelle_article': [
                'IN : Product Description',
                'Product Description',
                'Libellé Article',
                'Description',
                'Description Article'
            ],
            'lot_fournisseur': [
                'IN : Lot Number',
                'Lot Number',
                'Lot fournisseur',
                'Numéro Lot'
            ],
            'quantite': [
                'IN : Quantity available',
                'Quantity available',
                'Quantité',
                'Qté Disponible',
                'Quantité disponible'
            ],
            'udm': [
                'IN : UOM Code',
                'UOM Code',
                'UDM',
                'Unité de Mesure',
                'Unité'
            ],
            'division': [
                'IN : Facility',
                'Facility',
                'Division',
                'Site'
            ],
            'emplacement': [
                'IN : Warehouse Location Name',
                'Warehouse Location Name',
                'Emplacement',
                'Location',
                'Magasin'
            ],
            'contenant': [
                'INC : Container',
                'Container',
                'Contenant',
                'Container ID'
            ],
            'dluo': [
                'IN : Best Before Date',
                'Best Before Date',
                'DLUO',
                'Date limite',
                'Date expiration'
            ],
            'commentaire': [
                'AL : Lot Comment',
                'Lot Comment',
                'Commentaire',
                'Commentaire lot',
                'Notes'
            ]
        }

    def _find_column_value(self, row: dict, field_name: str) -> Optional[str]:
        """
        Trouve la valeur d'une colonne en utilisant le mapping flexible

        Args:
            row: Dictionnaire représentant une ligne
            field_name: Nom du champ recherché

        Returns:
            Valeur trouvée ou None
        """
        if field_name not in self.column_mapping:
            return row.get(field_name)

        possible_names = self.column_mapping[field_name]

        # Essayer chaque nom possible
        for col_name in possible_names:
            if col_name in row and pd.notna(row[col_name]):
                return str(row[col_name]).strip()

        return None

    def _parse_quantity(self, quantity_value) -> float:
        """
        Parse une valeur de quantité en float
        
        Args:
            quantity_value: Valeur brute de la quantité
            
        Returns:
            float: Quantité parsée ou 0.0 si non disponible
        """
        if quantity_value is None or pd.isna(quantity_value):
            return 0.0
            
        try:
            # Essayer de convertir en float
            if isinstance(quantity_value, str):
                # Nettoyer la string
                cleaned = quantity_value.strip().replace(',', '.')
                if cleaned.lower() in ['nan', 'none', 'null', '', 'n/a']:
                    return 0.0
                return float(cleaned)
            else:
                return float(quantity_value)
        except (ValueError, TypeError):
            logger.warning(f"Impossible de parser la quantité '{quantity_value}', utilisation de 0.0")
            return 0.0

    def _convert_quantity_to_kg(self, quantite: float, unite_mesure: str) -> float:
        """
        Convertit automatiquement toute quantité en kilos
        
        Args:
            quantite: La quantité à convertir
            unite_mesure: L'unité de mesure (GRM pour grammes, KGM pour kilos)
            
        Returns:
            float: La quantité en kilos
        """
        if quantite is None or pd.isna(quantite):
            return 0.0
        
        # Convertir automatiquement en kilos selon l'unité de mesure
        if unite_mesure and unite_mesure.upper() == 'GRM':
            # Grammes -> Kilos
            return quantite / 1000.0
        else:
            # KGM ou autre -> considérer déjà en kilos
            return quantite

    def decode_row(self, row: dict) -> Stock:
        """
        Décode une ligne stock_flexnet en objet Stock

        Args:
            row: Dictionnaire représentant une ligne stock_flexnet

        Returns:
            Stock: L'objet Stock créé
        """
        # Utiliser le mapping flexible pour trouver les valeurs
        article = self._find_column_value(row, 'article')
        libelle_article = self._find_column_value(row, 'libelle_article')
        statut_lot = self._find_column_value(row, 'statut_lot')
        division = self._find_column_value(row, 'division')
        emplacement = self._find_column_value(row, 'emplacement')
        contenant = self._find_column_value(row, 'contenant')

        # Vérifier les champs obligatoires
        if not article:
            raise ValueError("Article manquant")
        if not emplacement:
            raise ValueError("Emplacement manquant")
        if not contenant:
            raise ValueError("Contenant manquant")

        # Créer la matière
        matiere = Matiere(
            code_mp=article,
            nom=libelle_article or "Matière sans description"
        )

        # Parser les dates
        dluo = None
        dluo_raw = self._find_column_value(row, 'dluo')
        if dluo_raw:
            # Essayer plusieurs formats de date pour stock_flexnet
            for fmt in ['%d-%m-%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                try:
                    dluo = datetime.strptime(dluo_raw, fmt)
                    break
                except ValueError:
                    continue
            if not dluo:
                # Fallback avec parse_date
                dluo = parse_date(dluo_raw)

        # Récupérer l'unité de mesure et la quantité
        unite_mesure = clean_string_value(self._find_column_value(row, 'udm')) or 'KGM'
        quantite_raw = self._parse_quantity(self._find_column_value(row, 'quantite'))
        
        # Convertir automatiquement la quantité en kilos
        quantite_kg = self._convert_quantity_to_kg(quantite_raw, unite_mesure)

        try:
            # Créer le stock (la normalisation se fait automatiquement dans le modèle Pydantic)
            stock = Stock(
                article=article,
                libelle_article=libelle_article or "N/A",
                du=None,  # Pas de champ DU dans stock_flexnet
                quantite=quantite_kg,
                udm='KGM',  # Toujours en kilos après conversion
                statut_lot=statut_lot or 'N/A',
                division=division or 'N/A',
                magasin=division or 'N/A',  # Utiliser division comme magasin
                emplacement=emplacement,
                contenant=contenant,
                statut_proprete='N/A',  # Pas de champ dans stock_flexnet
                reutilisable='N/A',  # Pas de champ dans stock_flexnet
                statut_contenant='N/A',  # Pas de champ dans stock_flexnet
                classification=None,
                restriction=None,
                lot_fournisseur=self._find_column_value(row, 'lot_fournisseur') or 'N/A',
                capacite=None,
                commentaire=clean_string_value(self._find_column_value(row, 'commentaire')) or 'N/A',
                date_creation=datetime.now().replace(tzinfo=None),
                dluo=dluo,
                matiere=matiere
            )

            return stock
        except Exception as e:
            logger.error(f"Erreur lors du décodage de la ligne: {e}")
            raise

    def decode_file(self, file_path: Path) -> List[Stock]:
        """
        Décode un fichier Excel (onglet stock_flexnet) en liste de stocks

        Args:
            file_path: Chemin vers le fichier Excel

        Returns:
            List[Stock]: Liste des stocks créés
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")

            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"Format de fichier non supporté. Formats supportés: {self.supported_extensions}")

            # Lire l'onglet stock_flexnet du fichier Excel
            logger.info(f"Lecture de l'onglet stock_flexnet: {file_path}")
            df = pd.read_excel(file_path, sheet_name='stock_flexnet', header=1)
            logger.info(f"Onglet lu: {df.shape[0]} lignes, {df.shape[1]} colonnes")

            # Afficher les colonnes détectées pour debug
            logger.info(f"Colonnes détectées: {list(df.columns)}")

            # Convertir le DataFrame en liste de dictionnaires
            data = df.to_dict('records')

            stocks = []
            lignes_ignorees = 0

            for i, row in enumerate(data):
                try:
                    stock = self.decode_row(row)
                    stocks.append(stock)
                except ValueError as e:
                    # Ignorer silencieusement les lignes avec des champs vides
                    lignes_ignorees += 1
                    logger.debug(f"Ligne {i+1} ignorée: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Erreur lors du décodage de la ligne {i+1}: {e}")
                    continue

            if lignes_ignorees > 0:
                logger.info(f"⚠ {lignes_ignorees} lignes ignorées (champs obligatoires vides)")

            logger.info(f"Fichier {file_path} décodé avec succès. {len(stocks)} stocks créés.")
            return stocks

        except Exception as e:
            logger.error(f"Erreur lors du décodage du fichier {file_path}: {str(e)}")
            raise
