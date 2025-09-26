"""
Décodeur pour les stocks depuis CSV
"""
from typing import List
from pathlib import Path
from models.stock import Stock
from models.matieres import Matiere
from lib.decoders.decoder import Decoder
from lib.utils import parse_date
import logging

logger = logging.getLogger(__name__)

class CSVStocksDecoder(Decoder[Stock]):
    """
    Décodeur pour les stocks depuis CSV
    """

    def __init__(self):
        """
        Initialise le décodeur CSV
        """
        self.supported_extensions = ['.csv']

    def decode_row(self, row: dict) -> Stock:
        """
        Décode une ligne CSV en objet Stock

        Args:
            row: Dictionnaire représentant une ligne CSV

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

        # Créer le stock (la normalisation se fait automatiquement dans le modèle Pydantic)
        try:
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
                classification=row.get('Classification Lot'),
                restriction=row.get('Restriction'),
                lot_fournisseur=row.get('Lot fournisseur'),
                capacite=row.get('Capacité (Kg/Pièce)'),
                commentaire=row.get('Commentaire lot'),
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
        Décode un fichier CSV en liste de stocks

        Args:
            file_path: Chemin vers le fichier CSV

        Returns:
            List[Stock]: Liste des stocks créés
        """
        import csv

        try:
            if not file_path.exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")

            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"Format de fichier non supporté. Formats supportés: {self.supported_extensions}")

            stocks = []
            lignes_ignorees = 0

            with open(file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
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
