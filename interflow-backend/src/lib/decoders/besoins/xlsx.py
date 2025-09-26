"""
Décodeur pour les besoins depuis XLSX
"""
from typing import List, Union, Dict, Optional
from pathlib import Path
import pandas as pd
import logging
from models.besoin import Besoin, Etat
from models.matieres import Matiere
from datetime import datetime
from lib.decoders.decoder import Decoder
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


def is_valid_code_mp(code_mp: str) -> bool:
    """
    Vérifie si un code MP respecte le format attendu (6 caractères alphanumériques)

    Args:
        code_mp: Le code MP à valider

    Returns:
        bool: True si le code MP est valide, False sinon
    """
    if not code_mp or code_mp == "nan" or code_mp == "":
        return False

    # Ignorer les codes numériques courts (comme "67", "75")
    if code_mp.isdigit() and len(code_mp) < 3:
        return False

    # Le format attendu est 6 caractères alphanumériques (ex: M63244)
    # Mais on accepte aussi les codes plus courts s'ils ne sont pas purement numériques
    if len(code_mp) < 3:
        return False

    return True


def parse_quantite_precise(quantite_raw, precision_decimale: int = 6) -> float:
    """
    Parse une quantité avec une précision élevée

    Args:
        quantite_raw: Valeur brute de la quantité
        precision_decimale: Nombre de décimales à conserver

    Returns:
        float: Quantité parsée avec la précision demandée
    """
    try:
        if pd.isna(quantite_raw) or quantite_raw is None:
            return 0.0

        # Convertir en string pour éviter les problèmes de précision float
        if isinstance(quantite_raw, (int, float)):
            # Utiliser Decimal pour une précision maximale
            decimal_value = Decimal(str(quantite_raw))
            # Arrondir à la précision demandée
            rounded_decimal = decimal_value.quantize(
                Decimal('0.' + '0' * precision_decimale),
                rounding=ROUND_HALF_UP
            )
            return float(rounded_decimal)
        else:
            # Si c'est déjà une string, essayer de la parser
            quantite_str = str(quantite_raw).strip()
            if not quantite_str or quantite_str.lower() in ['nan', 'none', 'null', '']:
                return 0.0

            # Nettoyer et parser
            quantite_str_clean = quantite_str.replace(',', '.')
            decimal_value = Decimal(quantite_str_clean)
            rounded_decimal = decimal_value.quantize(
                Decimal('0.' + '0' * precision_decimale),
                rounding=ROUND_HALF_UP
            )
            return float(rounded_decimal)

    except (ValueError, TypeError, Exception) as e:
        logger.warning(f"Erreur lors du parsing de la quantité '{quantite_raw}': {e}")
        return 0.0


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


class XLSXBesoinsDecoder(Decoder[Besoin]):
    """
    Décodeur pour les besoins depuis XLSX
    """

    def __init__(self, precision_decimale: int = 6):
        """
        Initialise le décodeur XLSX

        Args:
            precision_decimale: Nombre de décimales à conserver pour les quantités (défaut: 6)
        """
        self.supported_extensions = ['.xlsx', '.xls']
        self.precision_decimale = precision_decimale

        # Mapping flexible des colonnes - plusieurs noms possibles pour chaque champ
        self.column_mapping = {
            'code_mp': ['Code MP', 'Code', 'Référence', 'Code Produit'],
            'libelle_mp': ['Libellé MP', 'Libellé', 'Description', 'Nom Produit'],
            'quantite': ['Quantité', 'Qté', 'Qte', 'Montant'],
            'date_echeance': ['Date Échéance', 'Échéance', 'Date', 'Deadline'],
            'etat': ['État', 'Statut', 'Status', 'Etat'],
            'lot': ['Lot', 'Numéro Lot', 'Lot N°']
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
                value = str(row[col_name]).strip()
                if value and value.lower() not in ['nan', 'none', 'null']:
                    return value

        return None

    def decode_row(self, row: dict) -> Besoin:
        """
        Décode une ligne XLSX en objet Besoin

        Args:
            row: Dictionnaire représentant une ligne XLSX

        Returns:
            Besoin: L'objet Besoin créé
        """
        try:
            # Extraire les champs avec mapping flexible
            code_mp = self._find_column_value(row, 'code_mp') or ""
            libelle_mp = self._find_column_value(row, 'libelle_mp') or ""
            quantite_str = self._find_column_value(row, 'quantite') or "0"

            # Ignorer les lignes avec des champs obligatoires vides
            if not code_mp:
                raise ValueError(f"Ligne ignorée: code MP vide")

            # Créer la matière
            matiere = Matiere(
                code_mp=code_mp,
                nom=libelle_mp if libelle_mp else f"Matière {code_mp}"
            )

            # Parser la quantité avec précision élevée
            quantite = parse_quantite_precise(quantite_str, self.precision_decimale)

            # Parser l'échéance
            echeance_str = self._find_column_value(row, 'date_echeance')
            echeance = datetime.now().replace(tzinfo=None)  # Par défaut
            if echeance_str:
                try:
                    echeance = datetime.strptime(echeance_str, '%d/%m/%Y')
                except ValueError:
                    try:
                        echeance = datetime.strptime(echeance_str, '%Y-%m-%d')
                    except ValueError:
                        pass

            # Parser l'état
            etat_str = self._find_column_value(row, 'etat')
            etat = Etat.INCONNU  # Par défaut
            if etat_str:
                try:
                    etat = Etat(etat_str.lower())
                except ValueError:
                    pass

            # Parser le lot
            lot = self._find_column_value(row, 'lot') or ""

            # Créer le besoin (la normalisation se fait automatiquement dans le modèle Pydantic)
            besoin = Besoin(
                matiere=matiere,
                quantite=quantite,
                echeance=echeance,
                etat=etat,
                lot=lot
            )

            return besoin

        except Exception as e:
            logger.error(f"Erreur lors du décodage de la ligne: {e}")
            raise

    def decode_file(self, file_path: Path) -> List[Besoin]:
        """
        Décode un fichier XLSX en liste de besoins

        Args:
            file_path: Chemin vers le fichier XLSX

        Returns:
            List[Besoin]: Liste des besoins créés
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")

            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"Format de fichier non supporté. Formats supportés: {self.supported_extensions}")

            # Lire le fichier Excel avec pandas
            logger.info(f"Lecture du fichier XLSX: {file_path}")

            # Essayer de lire la feuille "Rapport 0102 par jour" spécifiquement
            try:
                df = pd.read_excel(file_path, sheet_name="Rapport 0102 par jour", header=None)
                logger.info(f"Feuille 'Rapport 0102 par jour' lue: {df.shape[0]} lignes, {df.shape[1]} colonnes")
            except ValueError:
                # Si la feuille n'existe pas, lire la première feuille
                df = pd.read_excel(file_path, header=None)
                logger.info(f"Feuille par défaut lue: {df.shape[0]} lignes, {df.shape[1]} colonnes")

            # Analyser la structure du fichier
            # Ligne 4 (index 3) contient les en-têtes
            # Ligne 6 (index 5) contient les dates d'échéance
            # Ligne 7+ (index 6+) contient les données

            if len(df) < 7:
                raise ValueError("Fichier trop court, structure invalide")

            # Extraire les en-têtes (ligne 4, index 3)
            headers = df.iloc[3].tolist()
            logger.info(f"En-têtes trouvés: {headers[:10]}...")

            # Extraire les dates d'échéance (ligne 6, index 5)
            dates = df.iloc[5].tolist()
            logger.info(f"Dates trouvées: {dates[:10]}...")

            # Extraire les données (ligne 7+, index 6+)
            data_rows = df.iloc[6:].reset_index(drop=True)

            besoins = []
            lignes_ignorees = 0

            for idx, row in data_rows.iterrows():
                try:
                    # Extraire les informations de base
                    code_mp = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
                    libelle_mp = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
                    quantite_totale_str = str(row.iloc[7]).strip() if pd.notna(row.iloc[7]) else "0"

                    # Ignorer les lignes vides, sans code MP ou lignes de total
                    if not code_mp or code_mp == "nan" or code_mp == "" or code_mp == "75" or not is_valid_code_mp(code_mp):
                        continue

                    # Créer la matière
                    matiere = Matiere(
                        code_mp=code_mp,
                        nom=libelle_mp if libelle_mp and libelle_mp != "nan" else f"Matière {code_mp}"
                    )

                    # Parser la quantité totale (pour information, mais on ne crée pas de besoin avec)
                    quantite_totale = parse_quantite_precise(quantite_totale_str, self.precision_decimale)

                    # Note: On ne crée plus de besoin avec la quantité totale
                    # Seuls les besoins détaillés par date d'échéance sont créés

                    # Parcourir les colonnes de dates pour créer des besoins détaillés
                    for col_idx in range(9, len(row)):  # Commencer à la colonne 9 (première date)
                        if pd.notna(dates[col_idx]) and isinstance(dates[col_idx], datetime):
                            quantite_raw = row.iloc[col_idx]

                            # Ignorer si pas de quantité ou quantité = 0
                            if pd.isna(quantite_raw) or quantite_raw == 0:
                                continue

                            quantite = parse_quantite_precise(quantite_raw, self.precision_decimale)
                            if quantite <= 0:
                                continue

                            # Vérifier que la date n'est pas la date actuelle (cas où le parsing a échoué)
                            if dates[col_idx].strftime('%Y-%m-%d') != datetime.now().strftime('%Y-%m-%d'):
                                # Créer le besoin pour cette date spécifique
                                besoin = Besoin(
                                    matiere=matiere,
                                    quantite=quantite,
                                    echeance=dates[col_idx],
                                    etat=Etat.INCONNU,
                                    lot=""  # Pas d'information de lot
                                )
                                besoins.append(besoin)

                except Exception as e:
                    logger.warning(f"Erreur lors du décodage de la ligne {idx+7}: {e}")
                    lignes_ignorees += 1
                    continue

            logger.info(f"Fichier {file_path} décodé avec succès. {len(besoins)} besoins créés.")
            if lignes_ignorees > 0:
                logger.info(f"⚠ {lignes_ignorees} lignes ignorées")

            return besoins

        except Exception as e:
            logger.error(f"Erreur lors du décodage du fichier {file_path}: {str(e)}")
            raise

    def decode_complex_structure(self, file_path: Union[str, Path]) -> List[Besoin]:
        """
        Décode un fichier XLSX avec structure complexe (en-têtes multi-lignes)
        Spécifiquement pour la feuille "Rapport 0102 par jour"

        Args:
            file_path: Chemin vers le fichier XLSX

        Returns:
            List[Besoin]: Liste des besoins créés
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")

            # Lire le fichier sans en-têtes
            df = pd.read_excel(file_path, sheet_name="Rapport 0102 par jour", header=None)
            logger.info(f"Fichier lu: {df.shape[0]} lignes, {df.shape[1]} colonnes")

            # Extraire les en-têtes (ligne 4, index 3)
            headers = df.iloc[3].tolist()
            logger.info(f"En-têtes trouvés: {headers[:10]}...")

            # Extraire les dates d'échéance (ligne 5, index 4)
            dates = df.iloc[4].tolist()
            logger.info(f"Dates trouvées: {dates[:10]}...")

            # Extraire les données (ligne 6+, index 5+)
            data_rows = df.iloc[5:].reset_index(drop=True)

            besoins = []
            lignes_ignorees = 0

            for idx, row in data_rows.iterrows():
                try:
                    # Extraire les informations de base
                    code_mp = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
                    libelle_mp = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""

                    # Ignorer les lignes vides, sans code MP ou lignes de total
                    if not code_mp or code_mp == "nan" or code_mp == "" or code_mp == "75" or not is_valid_code_mp(code_mp):
                        continue

                    # Créer la matière
                    matiere = Matiere(
                        code_mp=code_mp,
                        nom=libelle_mp if libelle_mp and libelle_mp != "nan" else f"Matière {code_mp}"
                    )

                    # Parcourir les colonnes de dates pour créer des besoins
                    for col_idx in range(8, len(row)):  # Commencer à la colonne 8 (première date)
                        if pd.notna(dates[col_idx]) and isinstance(dates[col_idx], datetime):
                            quantite_raw = row.iloc[col_idx]

                            # Ignorer si pas de quantité ou quantité = 0
                            if pd.isna(quantite_raw) or quantite_raw == 0:
                                continue

                            quantite = parse_quantite_precise(quantite_raw, self.precision_decimale)
                            if quantite <= 0:
                                continue

                            # Déterminer l'état du besoin
                            etat = Etat.INCONNU  # Par défaut

                            # Créer le besoin
                            besoin = Besoin(
                                matiere=matiere,
                                quantite=quantite,
                                echeance=dates[col_idx],
                                etat=etat,
                                lot=""  # Pas d'information de lot dans ce fichier
                            )

                            besoins.append(besoin)

                except Exception as e:
                    logger.warning(f"Erreur lors du décodage de la ligne {idx}: {e}")
                    lignes_ignorees += 1
                    continue

            logger.info(f"Fichier {file_path} décodé avec succès. {len(besoins)} besoins créés.")
            if lignes_ignorees > 0:
                logger.info(f"⚠ {lignes_ignorees} lignes ignorées")

            return besoins

        except Exception as e:
            logger.error(f"Erreur lors du décodage du fichier {file_path}: {str(e)}")
            raise
