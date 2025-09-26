"""
Décodeur pour les besoins depuis CSV
"""
from typing import List, Optional
import logging
from models.besoin import Besoin, Etat
from models.matieres import Matiere
from datetime import datetime
from lib.decoders.decoder import Decoder
from pathlib import Path

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


class CSVBesoinsDecoder(Decoder[Besoin]):
    """
    Décodeur pour les besoins depuis CSV
    """

    def __init__(self):
        """
        Initialise le décodeur CSV
        """
        self.supported_extensions = ['.csv']

    def decode_row(self, row: dict) -> Besoin:
        """
        Décode une ligne CSV en objet Besoin

        Args:
            row: Dictionnaire représentant une ligne CSV

        Returns:
            Besoin: L'objet Besoin créé
        """
        try:
            # Afficher la ligne pour debug
            logger.debug(f"Ligne à décoder: {row}")

            # Le CSV a une structure spécifique avec une première colonne vide
            # Les colonnes sont : [vide], Code MP, Libellé MP, Mag Appro Ext, Stock dispo 0102, etc.

            # Extraire les données par nom de colonne
            code_produit = row.get('Code MP') or ""
            designation = row.get('Libellé MP') or ""
            quantite_str = row.get('Qté Besoin total') or "0"

            # Ignorer les lignes avec des champs obligatoires vides
            if not code_produit or not designation:
                raise ValueError(f"code MP vide")

            # Créer la matière
            matiere = Matiere(
                code_mp=code_produit,
                nom=designation
            )

            # Parser la quantité (gérer les espaces et virgules françaises)
            try:
                quantite_str_clean = quantite_str.replace(' ', '').replace(',', '.')
                quantite = float(quantite_str_clean)
            except ValueError:
                quantite = 0.0

            # Créer le besoin avec une échéance par défaut
            besoin = Besoin(
                matiere=matiere,
                quantite=quantite,
                echeance=datetime.now().replace(tzinfo=None),  # Pas d'information de date dans ce format
                etat=Etat.INCONNU,  # Par défaut
                lot=""  # Pas d'information de lot dans ce format
            )

            return besoin

        except Exception as e:
            logger.error(f"Erreur lors du décodage de la ligne: {e}")
            raise

    def decode_file(self, file_path: Path) -> List[Besoin]:
        """
        Décode un fichier CSV en liste de besoins

        Args:
            file_path: Chemin vers le fichier CSV

        Returns:
            List[Besoin]: Liste des besoins créés
        """
        import csv

        try:
            if not file_path.exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")

            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"Format de fichier non supporté. Formats supportés: {self.supported_extensions}")

            besoins = []
            lignes_ignorees = 0

            with open(file_path, 'r', encoding='utf-8-sig') as file:
                # Lire toutes les lignes
                lines = file.readlines()

                # Analyser la structure du CSV
                # Les données commencent à la ligne 8 (index 7)
                # Les colonnes sont : [vide], Code MP, Libellé MP, Mag Appro Ext, Stock dispo 0102, etc.
                data_lines = lines[7:]  # Commencer à partir de la ligne 8 (index 7)

                # Créer un reader CSV simple sans en-tête
                reader = csv.reader(data_lines)

                # Afficher les colonnes détectées pour debug
                logger.info(f"Lecture du CSV avec {len(data_lines)} lignes de données")

                # Extraire les dates d'échéance (ligne 7, index 6)
                dates_line = lines[6]
                dates_reader = csv.reader([dates_line])
                dates = next(dates_reader)
                logger.info(f"Dates trouvées: {dates[:10]}...")

                # Parser les dates en objets datetime
                parsed_dates = []
                for date_str in dates:
                    if date_str and str(date_str).strip() and str(date_str).strip() != "nan":
                        try:
                            # Essayer différents formats de date
                            date_clean = str(date_str).strip()
                            if '/' in date_clean:
                                # Format DD/MM/YYYY
                                parsed_date = datetime.strptime(date_clean, '%d/%m/%Y')
                            elif '-' in date_clean:
                                # Format YYYY-MM-DD
                                parsed_date = datetime.strptime(date_clean, '%Y-%m-%d')
                            else:
                                # Essayer de parser comme un nombre (timestamp Excel)
                                try:
                                    import pandas as pd
                                    parsed_date = pd.to_datetime(date_str)
                                except:
                                    parsed_date = None
                        except (ValueError, TypeError):
                            parsed_date = None
                    else:
                        parsed_date = None
                    parsed_dates.append(parsed_date)

                logger.info(f"Dates parsées: {[d.strftime('%Y-%m-%d') if d else 'None' for d in parsed_dates[:10]]}...")

                for i, row in enumerate(reader):
                    try:
                        # Le CSV a une structure fixe avec une première colonne vide
                        # Colonnes: [vide], Code MP, Libellé MP, Mag Appro Ext, Stock dispo 0102, etc.
                        if len(row) < 2:
                            continue

                        # Extraire les données par position
                        code_produit = row[1] if len(row) > 1 else ""  # Code MP
                        designation = row[2] if len(row) > 2 else ""   # Libellé MP
                        quantite_totale_str = row[7] if len(row) > 7 else "0"  # Qté Besoin total

                        # Ignorer les lignes avec des champs obligatoires vides
                        if not code_produit or not designation or not is_valid_code_mp(code_produit):
                            continue

                        # Créer la matière
                        matiere = Matiere(
                            code_mp=code_produit,
                            nom=designation
                        )

                        # Parser la quantité totale (gérer tous les types d'espaces et virgules françaises)
                        try:
                            quantite_totale_str_clean = quantite_totale_str.replace('\u202f', '').replace('\u00a0', '').replace(' ', '').replace(',', '.')
                            quantite_totale = float(quantite_totale_str_clean)
                        except ValueError:
                            quantite_totale = 0.0

                        # Note: On ne crée plus de besoin avec la quantité totale
                        # Seuls les besoins détaillés par date d'échéance sont créés

                        # Parcourir les colonnes de dates pour créer des besoins détaillés
                        for col_idx in range(9, len(row)):  # Commencer à la colonne 9 (première date)
                            if col_idx < len(parsed_dates) and parsed_dates[col_idx]:
                                # Extraire la quantité pour cette date
                                quantite_str = row[col_idx] if col_idx < len(row) else "0"

                                if quantite_str and quantite_str != "0":
                                    try:
                                        # Nettoyer la quantité en supprimant tous les types d'espaces (séparateurs de milliers) et en remplaçant les virgules par des points
                                        # Gérer les espaces Unicode (U+202F, U+00A0, etc.) et les espaces normaux
                                        quantite_str_clean = quantite_str.replace('\u202f', '').replace('\u00a0', '').replace(' ', '').replace(',', '.')
                                        quantite = float(quantite_str_clean)

                                        if quantite > 0:
                                            # Vérifier que la date n'est pas la date actuelle (cas où le parsing a échoué)
                                            if parsed_dates[col_idx].strftime('%Y-%m-%d') != datetime.now().strftime('%Y-%m-%d'):
                                                # Créer le besoin pour cette date spécifique
                                                besoin = Besoin(
                                                    matiere=matiere,
                                                    quantite=quantite,
                                                    echeance=parsed_dates[col_idx],
                                                    etat=Etat.INCONNU,
                                                    lot=""
                                                )
                                                besoins.append(besoin)
                                    except ValueError:
                                        # Ignorer si la quantité n'est pas un nombre valide
                                        pass

                    except Exception as e:
                        logger.error(f"Erreur lors du décodage de la ligne {i+8}: {e}")
                        lignes_ignorees += 1
                        continue

            if lignes_ignorees > 0:
                logger.info(f"⚠ {lignes_ignorees} lignes ignorées (erreurs de décodage)")

            logger.info(f"Fichier {file_path} décodé avec succès. {len(besoins)} besoins créés.")
            return besoins

        except Exception as e:
            logger.error(f"Erreur lors du décodage du fichier {file_path}: {str(e)}")
            raise
