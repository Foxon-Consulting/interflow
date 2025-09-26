"""
Décodeur pour les réceptions depuis XLSX
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


class XLSXReceptionsDecoder(Decoder[Reception]):
    """
    Décodeur pour les réceptions depuis XLSX
    """

    def __init__(self):
        """
        Initialise le décodeur XLSX
        """
        self.supported_extensions = ['.xlsx', '.xls']

        # Mapping flexible des colonnes - plusieurs noms possibles pour chaque champ
        self.column_mapping = {
            'numero_reception': ['Numéro Réception', 'Numero Réception', 'Réception', 'Ordre', 'N° Réception', 'N° Réception'],
            'article': ['Article', 'Code Article', 'Référence', 'Code Produit', 'Référence Article'],
            'fournisseur': ['Fournisseur', 'Fournisseur', 'Description fournisseur', 'Nom fournisseur'],
            'montant': ['Montant', 'Prix', 'Coût', 'Valeur', 'Prix unitaire', 'Quantité d\'ordre'],
            'statut': ['Statut', 'Statut Réception', 'Statut d\'ordre', 'État', 'Status'],
            'date_reception': ['Date Réception', 'Date de réception', 'Date création', 'Date ordre', 'Date de réception'],
            'date_livraison_souhaitee': ['Date Livraison Souhaitée', 'Date livraison', 'Date de livraison', 'Échéance'],
            'commentaire': ['Commentaire', 'Notes', 'Description', 'Remarques', 'Description Externe'],
            'devise': ['Devise', 'Monnaie', 'Currency', 'Unité monétaire', 'UDM'],
            'type_reception': ['Type Réception', 'Type d\'ordre', 'Catégorie', 'Type']
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
        Décode une ligne XLSX en objet Reception

        Args:
            row: Dictionnaire représentant une ligne XLSX

        Returns:
            Reception: L'objet Reception créé
        """
        # Utiliser le mapping flexible pour trouver les valeurs
        numero_reception = self._find_column_value(row, 'numero_reception')
        fournisseur = self._find_column_value(row, 'fournisseur')

        # Parser les dates (gestion des formats pandas)
        date_reception = None

        # Gestion de la date de réception
        date_reception_raw = self._find_column_value(row, 'date_reception')
        if date_reception_raw:
            try:
                if isinstance(date_reception_raw, str):
                    # Essayer plusieurs formats de date
                    for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d']:
                        try:
                            date_reception = datetime.strptime(date_reception_raw, fmt)
                            break
                        except ValueError:
                            continue
                    if not date_reception:
                        date_reception = pd.to_datetime(date_reception_raw).to_pydatetime()
                elif isinstance(date_reception_raw, pd.Timestamp):
                    date_reception = date_reception_raw.to_pydatetime()
                else:
                    date_reception = pd.to_datetime(date_reception_raw).to_pydatetime()
            except (ValueError, TypeError):
                logger.warning(f"Impossible de parser la date de réception: {date_reception_raw}")
                pass

        # Créer une matière à partir des données disponibles
        commentaire = clean_string_value(self._find_column_value(row, 'commentaire'))
        article = clean_string_value(self._find_column_value(row, 'article'))
        matiere = Matiere(
            code_mp=article,  # L'article sera toujours trouvé
            nom=commentaire or "Matière sans description"
        )

        # Créer la réception (la normalisation se fait automatiquement dans le modèle Pydantic)
        try:
            reception = Reception(
                matiere=matiere,
                quantite=self._find_column_value(row, 'montant') or '0',  # Normalisation automatique dans Pydantic
                date_creation=date_reception or datetime.now().replace(tzinfo=None),
                # Champs optionnels
                ordre=numero_reception,
                fournisseur=fournisseur,
                article=article,  # L'article sera toujours trouvé
                libelle_article=commentaire or "Article sans description",
                quantite_ordre=self._find_column_value(row, 'montant') or '0',  # Normalisation automatique dans Pydantic
                udm=clean_string_value(self._find_column_value(row, 'devise')) or 'EUR',
                type_ordre=clean_string_value(self._find_column_value(row, 'type_reception')) or 'MATIERE_PREMIERE',
                statut_ordre=clean_string_value(self._find_column_value(row, 'statut')) or 'EN_ATTENTE',
                description_externe=commentaire
            )

            return reception
        except Exception as e:
            logger.error(f"Erreur lors du décodage de la ligne: {e}")
            raise

    def decode_file(self, file_path: Path) -> List[Reception]:
        """
        Décode un fichier XLSX en liste de réceptions

        Args:
            file_path: Chemin vers le fichier XLSX

        Returns:
            List[Reception]: Liste des réceptions créées
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")

            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"Format de fichier non supporté. Formats supportés: {self.supported_extensions}")

            # Lire le fichier Excel avec pandas
            logger.info(f"Lecture du fichier XLSX: {file_path}")
            df = pd.read_excel(file_path)
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
