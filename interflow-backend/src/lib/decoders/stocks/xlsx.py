"""
Décodeur pour les stocks depuis XLSX
"""
from typing import List, Union
from pathlib import Path
import pandas as pd
import logging
from models.stock import Stock
from models.matieres import Matiere
from lib.decoders.decoder import Decoder
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


class XLSXStocksDecoder(Decoder[Stock]):
    """
    Décodeur pour les stocks depuis XLSX
    """

    def __init__(self):
        """
        Initialise le décodeur XLSX
        """
        self.supported_extensions = ['.xlsx', '.xls']

    def decode_row(self, row: dict) -> Stock:
        """
        Décode une ligne XLSX en objet Stock

        Args:
            row: Dictionnaire représentant une ligne XLSX

        Returns:
            Stock: L'objet Stock créé
        """

        # Extraire les champs obligatoires
        article = str(row.get('Article', '')).strip()
        magasin = str(row.get('Magasin', '')).strip()
        emplacement = str(row.get('Emplacement', '')).strip()
        contenant = str(row.get('Contenant', '')).strip()

        # Créer la matière
        matiere = Matiere(
            code_mp=article,
            nom=str(row.get('Libellé Article', 'Matière inconnue'))
        )

        # Parser les dates
        date_creation = parse_date(row.get('Date de création'))
        dluo = parse_date(row.get('DLUO'))

        try:
        # Créer le stock (la normalisation se fait automatiquement dans le modèle Pydantic)
            stock = Stock(
                article=article,
                libelle_article=row.get('Libellé Article'),
                du=row.get('DU'),
                quantite=row.get('Qté Disponible', '0'),  # Normalisation automatique dans Pydantic
                udm=row.get('UDM'),
                statut_lot=row.get('Statut Lot'),
                division=row.get('Division'),
                magasin=magasin,
                emplacement=emplacement,
                contenant=contenant,
                statut_proprete=row.get('Statut Propreté'),
                reutilisable=row.get('Réutilisable'),
                statut_contenant=row.get('Statut Contenant'),
                classification=clean_string_value(row.get('Classification Lot')),
                restriction=clean_string_value(row.get('Restriction')),
                lot_fournisseur=row.get('Lot fournisseur'),
                capacite=row.get('Capacité (Kg/Pièce)'),
                commentaire=clean_string_value(row.get('Commentaire lot')),
                date_creation=date_creation,
                dluo=dluo,
                matiere=matiere
                )

            return stock

        except Exception as e:
            logger.error(f"Erreur lors du décodage de la ligne: {e}")
            raise

    def decode_file(self, file_path: Path) -> List[Stock]:
        """
        Décode un fichier XLSX en liste de stocks

        Args:
            file_path: Chemin vers le fichier XLSX

        Returns:
            List[Stock]: Liste des stocks créés
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")

            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"Format de fichier non supporté. Formats supportés: {self.supported_extensions}")

            # Lire le fichier Excel avec pandas
            logger.info(f"Lecture du fichier XLSX: {file_path}")
            df = pd.read_excel(file_path)
            logger.info(f"Fichier lu: {df.shape[0]} lignes, {df.shape[1]} colonnes")

            # Convertir le DataFrame en liste de dictionnaires
            data = df.to_dict('records')

            stocks = []
            lignes_ignorees = 0

            for row in data:
                try:
                    stock = self.decode_row(row)
                    stocks.append(stock)
                except ValueError as e:
                    logger.warning(f"Ligne ignorée: {e}")
                    lignes_ignorees += 1
                    continue
                except Exception as e:
                    logger.error(f"Erreur lors du décodage de la ligne: {e}")
                    continue

            if lignes_ignorees > 0:
                logger.info(f"⚠ {lignes_ignorees} lignes ignorées (champs obligatoires vides)")

            logger.info(f"Fichier {file_path} décodé avec succès. {len(stocks)} stocks créés.")
            return stocks

        except Exception as e:
            logger.error(f"Erreur lors du décodage du fichier {file_path}: {str(e)}")
            raise
