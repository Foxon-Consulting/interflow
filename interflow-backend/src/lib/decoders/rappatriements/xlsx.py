"""
Décodeur pour les rapatriements depuis XLSX
"""
from typing import List, Union, Dict, Optional
from pathlib import Path
import pandas as pd
import logging
from models.rappatriement import Rappatriement, ProduitRappatriement, TypeEmballage
from datetime import datetime
from lib.decoders.decoder import Decoder

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


class XLSXRappatriementsDecoder(Decoder[Rappatriement]):
    """
    Décodeur pour les rapatriements depuis XLSX
    """

    def __init__(self):
        """
        Initialise le décodeur XLSX
        """
        self.supported_extensions = ['.xlsx', '.xls']

        # Mapping flexible des colonnes - plusieurs noms possibles pour chaque champ
        self.column_mapping = {
            'prelevement': ['Pour PRLVM', 'PRLVM', 'Pour', 'Code PRLVM', 'Pour Prlvm', 'Unnamed: 0'],
            'code_prdt': ['Code Prdt', 'Code Produit', 'Code', 'Référence'],
            'designation_prdt': ['Designation Prdt', 'Désignation Prdt', 'Désignation', 'Description', 'Nom Produit'],
            'lot': ['Lot', 'Numéro Lot', 'Lot N°'],
            'poids_net': ['Poids Net', 'Poids', 'Poids (kg)', 'Masse', 'Poids net (/lot)'],
            'type_emballage': ['Type Emballage', 'Type', 'Emballage', 'Packaging', 'Type emballage'],
            'stock_solde': ['Stock Solde', 'Solde', 'Stock', 'Disponible', 'Stock soldé'],
            'nb_contenants': ['Nb Contenants', 'Nombre Contenants', 'Contenants', 'Nb Cont', 'Nb contenants'],
            'nb_palettes': ['Nb Palettes', 'Nombre Palettes', 'Palettes', 'Nb Pal', 'Nb palettes'],
            'dimension_palettes': ['Dimension Palettes', 'Dimensions', 'Taille Palettes', 'Dimension palettes'],
            'code_onu': ['Code ONU', 'ONU', 'Code UN'],
            'grp_emballage': ['Grp Emballage', 'Groupe Emballage', 'Groupe', 'Grp emballage'],
            'po': ['PO', 'Purchase Order', 'Commande', 'PO(à renseigner par les divisions 0101 et 0102ND)']
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

        # Debug pour voir les colonnes disponibles
        logger.debug(f"Recherche de {field_name} dans les colonnes: {list(row.keys())}")
        logger.debug(f"Noms possibles pour {field_name}: {possible_names}")

        # Essayer chaque nom possible
        for col_name in possible_names:
            if col_name in row and pd.notna(row[col_name]):
                value = str(row[col_name]).strip()
                if value and value.lower() not in ['nan', 'none', 'null', '#error!']:
                    logger.debug(f"Colonne '{col_name}' trouvée avec valeur: '{value}'")
                    return value
                else:
                    logger.debug(f"Colonne '{col_name}' trouvée mais valeur ignorée: '{value}'")

        logger.debug(f"Aucune valeur trouvée pour {field_name}")
        return None

    def decode_row(self, row: dict) -> Rappatriement:
        """
        Décode une ligne XLSX en objet Rappatriement

        Args:
            row: Dictionnaire représentant une ligne XLSX

        Returns:
            Rappatriement: L'objet Rappatriement créé
        """
        # Créer un rapatriement avec un produit (la normalisation se fait automatiquement dans le modèle Pydantic)
        try:
            # Créer le produit
            produit = ProduitRappatriement(
                prelevement=self._find_column_value(row, 'prelevement') or False,
                code_prdt=self._find_column_value(row, 'code_prdt') or "PROD_UNKNOWN",
                designation_prdt=self._find_column_value(row, 'designation_prdt') or "Produit sans description",
                lot=self._find_column_value(row, 'lot') or "",
                poids_net=self._find_column_value(row, 'poids_net') or '0',  # Normalisation automatique dans Pydantic
                type_emballage=self._find_column_value(row, 'type_emballage') or 'AUTRE',  # Normalisation automatique dans Pydantic
                stock_solde=self._find_column_value(row, 'stock_solde') or False,  # Normalisation automatique dans Pydantic
                nb_contenants=self._find_column_value(row, 'nb_contenants') or '0',  # Normalisation automatique dans Pydantic
                nb_palettes=self._find_column_value(row, 'nb_palettes') or '0',  # Normalisation automatique dans Pydantic
                dimension_palettes=self._find_column_value(row, 'dimension_palettes') or "",
                code_onu=self._find_column_value(row, 'code_onu') or "",
                grp_emballage=self._find_column_value(row, 'grp_emballage') or "",
                po=clean_string_value(self._find_column_value(row, 'po'))  # Champ optionnel
            )

            # Créer le rapatriement avec des valeurs par défaut
            rappatriement = Rappatriement(
                numero_transfert="RAP_UNKNOWN",
                date_derniere_maj=datetime.now().replace(tzinfo=None),
                responsable_diffusion="Service Entrepôts & Distribution",
                date_demande=None,
                date_reception_souhaitee=None,
                contacts="",
                adresse_destinataire="",
                adresse_enlevement="",
                remarques=""
            )

            rappatriement.ajouter_produit(produit)
            return rappatriement

        except Exception as e:
            logger.error(f"Erreur lors du décodage de la ligne: {e}")
            raise

    def decode_file(self, file_path: Path) -> List[Rappatriement]:
        """
        Décode un fichier XLSX de rapatriement

        Args:
            file_path: Le chemin vers le fichier XLSX

        Returns:
            List[Rappatriement]: Liste des rapatriements décodés
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")

            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"Format de fichier non supporté. Formats supportés: {self.supported_extensions}")

            # Lire le fichier Excel avec pandas
            logger.info(f"Lecture du fichier XLSX: {file_path}")

            # Essayer de lire avec header=None pour voir toutes les lignes
            df_raw = pd.read_excel(file_path, header=None)
            logger.info(f"Fichier lu (raw): {df_raw.shape[0]} lignes, {df_raw.shape[1]} colonnes")

            # Chercher l'en-tête (lignes contenant "Code Prdt")
            header_row = None
            for i, row in df_raw.iterrows():
                row_values = [str(val).strip() for val in row.values if pd.notna(val)]
                if any('Code Prdt' in val for val in row_values):
                    header_row = i
                    logger.info(f"En-tête trouvé à la ligne {i+1}: {row_values}")
                    break

            if header_row is None:
                raise ValueError("En-tête CSV non trouvé dans le fichier XLSX")

            logger.info(f"En-tête trouvé à la ligne {header_row + 1}")

            # Lire le fichier avec l'en-tête correct
            df = pd.read_excel(file_path, header=header_row)
            logger.info(f"Fichier lu avec en-tête: {df.shape[0]} lignes, {df.shape[1]} colonnes")

            # Afficher les colonnes détectées pour debug
            logger.info(f"Colonnes détectées: {list(df.columns)}")

            # Extraire les métadonnées du rapatriement depuis le fichier XLSX
            numero_transfert = "RAP_UNKNOWN"
            date_demande = None
            date_reception_souhaitee = None
            adresse_destinataire = ""
            adresse_enlevement = ""
            remarques = ""

            # Lire les métadonnées depuis les premières lignes
            for i, row in df_raw.iterrows():
                row_values = [str(val).strip() for val in row.values if pd.notna(val)]
                row_text = " ".join(row_values).lower()

                # Numéro de transfert
                if "numéro de transfert" in row_text:
                    for val in row_values:
                        if "n°" in val or "lsr" in val.lower():
                            # Nettoyer le numéro de transfert
                            numero_clean = val.strip()
                            if "Numéro de Transfert N°" in numero_clean:
                                numero_transfert = numero_clean.replace("Numéro de Transfert N°", "").strip()
                            else:
                                numero_transfert = numero_clean
                            break

                # Date de demande
                if "date de la demande" in row_text:
                    for val in row.values:
                        if isinstance(val, datetime):
                            date_demande = val
                            break

                # Date de réception souhaitée
                if "date de réception souhaitée" in row_text:
                    for val in row.values:
                        if isinstance(val, datetime):
                            date_reception_souhaitee = val
                            break

                # Adresse destinataire
                if "adresse destinataire" in row_text:
                    for j, val in enumerate(row.values):
                        if pd.notna(val) and "adresse destinataire" in str(val).lower():
                            if j + 1 < len(row.values) and pd.notna(row.values[j + 1]):
                                adresse_destinataire = str(row.values[j + 1]).strip()
                            break

                # Adresse enlèvement
                if "adresse enlèvement" in row_text:
                    for j, val in enumerate(row.values):
                        if pd.notna(val) and "adresse enlèvement" in str(val).lower():
                            if j + 1 < len(row.values) and pd.notna(row.values[j + 1]):
                                adresse_enlevement = str(row.values[j + 1]).strip()
                            break

                # Remarques
                if "règle du rapatriement" in row_text:
                    remarques = " ".join(row_values)
                    break

            # Créer le rapatriement avec les informations extraites
            rappatriement = Rappatriement(
                numero_transfert=numero_transfert,
                date_derniere_maj=datetime.now().replace(tzinfo=None),  # Date actuelle
                responsable_diffusion="Service Entrepôts & Distribution",
                date_demande=date_demande,
                date_reception_souhaitee=date_reception_souhaitee,
                contacts="",
                adresse_destinataire=adresse_destinataire,
                adresse_enlevement=adresse_enlevement,
                remarques=remarques
            )

            # Convertir le DataFrame en liste de dictionnaires
            data = df.to_dict('records')

            # Parser chaque ligne comme un produit
            for i, row in enumerate(data):
                try:
                    # Vérifier si la ligne contient au moins les données minimales
                    code_prdt = self._find_column_value(row, 'code_prdt')
                    designation_prdt = self._find_column_value(row, 'designation_prdt')

                    # Debug pour voir les valeurs trouvées
                    logger.debug(f"Ligne {i+1} - code_prdt: '{code_prdt}', designation_prdt: '{designation_prdt}'")

                    # Ignorer les lignes sans code produit ou avec des erreurs
                    if not code_prdt or not designation_prdt:
                        logger.debug(f"Ligne {i+1} ignorée : données insuffisantes")
                        continue

                    # Ignorer les lignes qui ne sont pas des produits (remarques, totaux, etc.)
                    if (designation_prdt.lower() in ['remarques', 'remarque', 'note', 'total', 'somme'] or
                        code_prdt.lower() in ['remarques', 'remarque', 'note', 'total', 'somme'] or
                        code_prdt.lower().startswith('remarques') or
                        designation_prdt.lower().startswith('remarques')):
                        logger.debug(f"Ligne {i+1} ignorée : ligne de remarques/total")
                        continue

                    # Créer le produit (la normalisation se fait automatiquement dans le modèle Pydantic)
                    produit = ProduitRappatriement(
                        prelevement=self._find_column_value(row, 'prelevement'),
                        code_prdt=code_prdt,
                        designation_prdt=designation_prdt,
                        lot=self._find_column_value(row, 'lot') or "",
                        poids_net=self._find_column_value(row, 'poids_net') or '0',  # Normalisation automatique dans Pydantic
                        type_emballage=self._find_column_value(row, 'type_emballage') or 'AUTRE',  # Normalisation automatique dans Pydantic
                        stock_solde=self._find_column_value(row, 'stock_solde') or False,  # Normalisation automatique dans Pydantic
                        nb_contenants=self._find_column_value(row, 'nb_contenants') or '0',  # Normalisation automatique dans Pydantic
                        nb_palettes=self._find_column_value(row, 'nb_palettes') or '0',  # Normalisation automatique dans Pydantic
                        dimension_palettes=self._find_column_value(row, 'dimension_palettes') or "",
                        code_onu=self._find_column_value(row, 'code_onu') or "",
                        grp_emballage=self._find_column_value(row, 'grp_emballage') or "",
                        po=clean_string_value(self._find_column_value(row, 'po'))  # Champ optionnel
                    )

                    rappatriement.ajouter_produit(produit)

                except Exception as e:
                    logger.warning(f"Erreur lors du décodage de la ligne {i+1}: {e}")
                    continue

            logger.info(f"Fichier {file_path} décodé avec succès. {len(rappatriement.produits)} produits créés.")
            return [rappatriement]

        except Exception as e:
            logger.error(f"Erreur lors du décodage du fichier {file_path}: {str(e)}")
            raise
