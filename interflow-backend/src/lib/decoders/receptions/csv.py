"""
Décodeur pour les réceptions depuis CSV
"""
from typing import List
from pathlib import Path
import logging
from models.reception import Reception
from models.matieres import Matiere
from datetime import datetime
from lib.decoders.decoder import Decoder

logger = logging.getLogger(__name__)


class CSVReceptionsDecoder(Decoder[Reception]):
    """
    Décodeur pour les réceptions depuis CSV
    """

    def decode_row(self, row: dict) -> Reception:
        """
        Décode une ligne CSV en objet Reception

        Args:
            row: Dictionnaire représentant une ligne CSV

        Returns:
            Reception: L'objet Reception créé
        """
        # Extraire les champs de base
        numero_reception = row.get('Numéro Réception', '').strip()
        fournisseur = row.get('Fournisseur', '').strip()

        # Parser les dates
        date_reception = None
        if row.get('Date Réception'):
            try:
                date_reception = datetime.strptime(row['Date Réception'], '%d/%m/%Y')
            except ValueError:
                pass

        # Créer une matière à partir des données disponibles
        matiere = Matiere(
            code_mp=numero_reception,
            nom=row.get('Commentaire', 'Matière sans description')
        )

        # Créer la réception (la normalisation se fait automatiquement dans le modèle Pydantic)
        try:
            reception = Reception(
                matiere=matiere,
                quantite=row.get('Montant', '0'),  # Normalisation automatique dans Pydantic
                date_creation=date_reception or datetime.now().replace(tzinfo=None),
                # Champs optionnels
                ordre=numero_reception,
                fournisseur=fournisseur,
                article=numero_reception,
                libelle_article=row.get('Commentaire', 'Article sans description'),
                quantite_ordre=row.get('Montant', '0'),  # Normalisation automatique dans Pydantic
                udm=row.get('Devise', 'EUR'),
                type_ordre=row.get('Type Réception', 'MATIERE_PREMIERE'),
                statut_ordre=row.get('Statut', 'EN_ATTENTE'),
                description_externe=row.get('Commentaire', '')
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
        import csv

        receptions = []
        lignes_ignorees = 0

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        reception = self.decode_row(row)
                        receptions.append(reception)
                    except ValueError as e:
                        # Ignorer silencieusement les lignes avec des champs vides
                        lignes_ignorees += 1
                        continue
                    except Exception as e:
                        logger.error(f"Erreur lors du décodage de la ligne: {e}")
                        continue
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
            return []

        if lignes_ignorees > 0:
            logger.info(f"⚠ {lignes_ignorees} lignes ignorées (champs obligatoires vides)")

        return receptions
