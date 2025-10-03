"""
Décodeur pour les réceptions depuis CSV (S3)
"""
from typing import List, Union, Dict, Optional
from pathlib import Path
import pandas as pd
import logging
from models.reception import Reception
from datetime import datetime
from lib.decoders.decoder import Decoder
from models.matieres import Matiere

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


class CSVReceptionsDecoder(Decoder[Reception]):
    """
    Décodeur pour les réceptions depuis CSV (S3)
    """

    def __init__(self):
        """
        Initialise le décodeur CSV
        """
        self.supported_extensions = ['.csv']

        # Mapping flexible des colonnes - plusieurs noms possibles pour chaque champ
        # Basé sur le format du fichier interflow_recption_prevue.csv
        self.column_mapping = {
            'numero_reception': [
                'RO : Receiving Order Number', 
                'Receiving Order Number', 
                'RO', 
                'Numéro Réception', 
                'Numero Réception', 
                'Réception', 
                'Ordre', 
                'N° Réception'
            ],
            'ligne_reception': [
                'ROL : Receiving Order Line Number', 
                'Receiving Order Line Number', 
                'ROL', 
                'Ligne Réception', 
                'Ligne'
            ],
            'article': [
                'ROL : Product Number', 
                'Product Number', 
                'Article', 
                'Code Article', 
                'Référence', 
                'Code Produit', 
                'Référence Article'
            ],
            'description_article': [
                'ROL : Product Description', 
                'Product Description', 
                'Description Article', 
                'Description Produit', 
                'Libellé Article'
            ],
            'fournisseur_numero': [
                'ROL : Supplier Number', 
                'Supplier Number', 
                'Numéro Fournisseur', 
                'Code Fournisseur'
            ],
            'fournisseur_nom': [
                'ROL : Supplier Name', 
                'Supplier Name', 
                'Fournisseur', 
                'Nom Fournisseur', 
                'Description fournisseur'
            ],
            'quantite': [
                'ROL : Quantity Ordered', 
                'Quantity Ordered', 
                'Quantité', 
                'Montant', 
                'Prix', 
                'Coût', 
                'Valeur', 
                'Prix unitaire'
            ],
            'unite_mesure': [
                'ROL : UOM Code Qty Ordered', 
                'UOM Code Qty Ordered', 
                'UOM', 
                'Unité de Mesure', 
                'Devise', 
                'Monnaie', 
                'Currency', 
                'Unité monétaire'
            ],
            'statut': [
                'ROL : Progress Status', 
                'Progress Status', 
                'Statut', 
                'Statut Réception', 
                'Statut d\'ordre', 
                'État', 
                'Status'
            ],
            'entrepot_destination': [
                'ROL : Scheduled Destination Warehouse', 
                'Scheduled Destination Warehouse', 
                'Entrepôt Destination', 
                'Warehouse', 
                'Destination'
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

    def decode_row(self, row: dict) -> Reception:
        """
        Décode une ligne CSV en objet Reception

        Args:
            row: Dictionnaire représentant une ligne CSV

        Returns:
            Reception: L'objet Reception créé
        """
        # Utiliser le mapping flexible pour trouver les valeurs
        numero_reception = self._find_column_value(row, 'numero_reception')
        ligne_reception = self._find_column_value(row, 'ligne_reception')
        fournisseur_numero = self._find_column_value(row, 'fournisseur_numero')
        fournisseur_nom = self._find_column_value(row, 'fournisseur_nom')
        
        # Combiner le numéro et nom du fournisseur si disponibles
        fournisseur = None
        if fournisseur_numero and fournisseur_nom:
            fournisseur = f"{fournisseur_numero} - {fournisseur_nom}"
        elif fournisseur_nom:
            fournisseur = fournisseur_nom
        elif fournisseur_numero:
            fournisseur = fournisseur_numero

        # Créer une matière à partir des données disponibles
        article = clean_string_value(self._find_column_value(row, 'article'))
        description_article = clean_string_value(self._find_column_value(row, 'description_article'))
        
        matiere = Matiere(
            code_mp=article or "ARTICLE_INCONNU",
            nom=description_article or "Matière sans description"
        )

        # Créer la réception (la normalisation se fait automatiquement dans le modèle Pydantic)
        try:
            reception = Reception(
                matiere=matiere,
                quantite=self._find_column_value(row, 'quantite') or '0',
                date_creation=datetime.now().replace(tzinfo=None),  # Pas de date dans le CSV, utiliser maintenant
                # Champs optionnels
                ordre=numero_reception,
                fournisseur=fournisseur,
                article=article,
                libelle_article=description_article or "Article sans description",
                quantite_ordre=self._find_column_value(row, 'quantite') or '0',
                udm=clean_string_value(self._find_column_value(row, 'unite_mesure')) or 'GRM',
                type_ordre='MATIERE_PREMIERE',  # Valeur par défaut
                statut_ordre=clean_string_value(self._find_column_value(row, 'statut')) or 'EN_ATTENTE',
                description_externe=description_article
            )

            return reception
        except Exception as e:
            logger.error(f"Erreur lors du décodage de la ligne: {e}")
            raise

    def decode_file(self, file_path: Path) -> List[Reception]:
        """
        Décode un fichier CSV en liste de réceptions

        Args:
            file_path: Chemin vers le fichier CSV

        Returns:
            List[Reception]: Liste des réceptions créées
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")

            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"Format de fichier non supporté. Formats supportés: {self.supported_extensions}")

            # Lire le fichier CSV avec pandas
            logger.info(f"Lecture du fichier CSV: {file_path}")
            df = pd.read_csv(file_path)
            logger.info(f"Fichier lu: {df.shape[0]} lignes, {df.shape[1]} colonnes")

            # Afficher les colonnes détectées pour debug
            logger.info(f"Colonnes détectées: {list(df.columns)}")

            # Convertir le DataFrame en liste de dictionnaires
            data = df.to_dict('records')

            receptions = []
            lignes_ignorees = 0

            for i, row in enumerate(data):
                try:
                    reception = self.decode_row(row)
                    receptions.append(reception)
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

            logger.info(f"Fichier {file_path} décodé avec succès. {len(receptions)} réceptions créées.")
            return receptions

        except Exception as e:
            logger.error(f"Erreur lors du décodage du fichier {file_path}: {str(e)}")
            raise

