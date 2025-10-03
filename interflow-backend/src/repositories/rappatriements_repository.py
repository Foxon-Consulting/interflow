"""
Repository pour la gestion des rapatriements
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from .base_repository import BaseRepository
from .storage_strategies import JSONStorageStrategy, StorageStrategy
from models.rappatriement import Rappatriement, ProduitRappatriement
from lib.paths import get_repository_file

import json
import re
import os
from lib.paths import get_output_file


class RappatriementsRepository(BaseRepository[Rappatriement]):
    """
    Repository pour la gestion des rapatriements
    """

    def __init__(self, storage: StorageStrategy):
        """
        Initialise le repository des rapatriements

        Args:
            storage: Stratégie de stockage à utiliser
        """
        super().__init__(
            model_class=Rappatriement,
            storage=storage,
            id_field="numero_transfert"
        )

    def flush(self) -> None:
        """
        Vide toutes les données ET le fichier de log des fichiers traités
        """
        # Appeler la méthode flush du parent
        super().flush()

        # Supprimer le fichier de log des fichiers traités
        try:
            log_file = get_output_file("processed_rappatriement_files.json", "logs")
            if log_file.exists():
                log_file.unlink()
                print(f"✓ Fichier de log des fichiers traités supprimé : {log_file}")
        except Exception as e:
            print(f"⚠️ Erreur lors de la suppression du fichier de log : {e}")

    def get_rappatriements_list(self) -> List[Rappatriement]:
        """
        Récupère tous les rapatriements

        Returns:
            List[Rappatriement]: Une liste de rapatriements
        """
        return self.get_all()

    def create_rappatriement(self, rappatriement: Rappatriement) -> Rappatriement:
        """
        Crée un nouveau rapatriement

        Args:
            rappatriement: L'objet Rappatriement à créer

        Returns:
            Rappatriement: Le rapatriement créé avec son ID
        """
        # Générer un ID unique si pas fourni
        if not rappatriement.numero_transfert:
            rappatriement.numero_transfert = self._generate_transfer_number()

        return self.create(rappatriement)

    def get_rappatriement_by_numero(self, numero_transfert: str) -> Optional[Rappatriement]:
        """
        Récupère un rapatriement par son numéro de transfert

        Args:
            numero_transfert: Numéro de transfert du rapatriement

        Returns:
            Optional[Rappatriement]: Le rapatriement trouvé ou None
        """
        return self.get_by_id(numero_transfert)

    def get_rappatriements_by_date_range(self,
                                       date_debut: datetime,
                                       date_fin: datetime) -> List[Rappatriement]:
        """
        Récupère les rapatriements dans une plage de dates

        Args:
            date_debut: Date de début
            date_fin: Date de fin

        Returns:
            List[Rappatriement]: Liste des rapatriements dans la plage
        """
        filtered_rappatriements = []
        for rappatriement in self.get_all():
            if rappatriement.date_demande:
                if date_debut <= rappatriement.date_demande <= date_fin:
                    filtered_rappatriements.append(rappatriement)
        return filtered_rappatriements

    def get_rappatriements_by_responsable(self, responsable: str) -> List[Rappatriement]:
        """
        Récupère les rapatriements par responsable

        Args:
            responsable: Nom du responsable

        Returns:
            List[Rappatriement]: Liste des rapatriements du responsable
        """
        filtered_rappatriements = []
        for rappatriement in self.get_all():
            if responsable.lower() in rappatriement.responsable_diffusion.lower():
                filtered_rappatriements.append(rappatriement)
        return filtered_rappatriements

    def get_rappatriements_by_adresse_destinataire(self, adresse_partielle: str) -> List[Rappatriement]:
        """
        Récupère les rapatriements par adresse destinataire

        Args:
            adresse_partielle: Partie de l'adresse à rechercher

        Returns:
            List[Rappatriement]: Liste des rapatriements correspondants
        """
        filtered_rappatriements = []
        for rappatriement in self.get_all():
            if adresse_partielle.lower() in rappatriement.adresse_destinataire.lower():
                filtered_rappatriements.append(rappatriement)
        return filtered_rappatriements

    def get_rappatriements_by_produit(self, code_produit: str) -> List[Rappatriement]:
        """
        Récupère les rapatriements contenant un produit spécifique

        Args:
            code_produit: Code du produit à rechercher

        Returns:
            List[Rappatriement]: Liste des rapatriements contenant ce produit
        """
        filtered_rappatriements = []
        for rappatriement in self.get_all():
            for produit in rappatriement.produits:
                if code_produit.lower() in produit.code_prdt.lower():
                    filtered_rappatriements.append(rappatriement)
                    break  # Éviter les doublons si plusieurs produits correspondent
        return filtered_rappatriements

    def get_rappatriements_by_matiere(self, code_matiere: str) -> List[Rappatriement]:
        """
        Récupère les rapatriements contenant une matière spécifique

        Args:
            code_matiere: Code de la matière à rechercher (recherche dans code_prdt et designation_prdt)

        Returns:
            List[Rappatriement]: Liste des rapatriements contenant cette matière
        """
        filtered_rappatriements = []
        code_matiere_lower = code_matiere.lower()

        for rappatriement in self.get_all():
            for produit in rappatriement.produits:
                # Recherche dans le code produit et la désignation
                if (code_matiere_lower in produit.code_prdt.lower() or
                    code_matiere_lower in produit.designation_prdt.lower()):
                    filtered_rappatriements.append(rappatriement)
                    break  # Éviter les doublons si plusieurs produits correspondent
        return filtered_rappatriements

    def get_rappatriements_by_type_emballage(self, type_emballage: str) -> List[Rappatriement]:
        """
        Récupère les rapatriements contenant un type d'emballage spécifique

        Args:
            type_emballage: Type d'emballage recherché

        Returns:
            List[Rappatriement]: Liste des rapatriements correspondants
        """
        filtered_rappatriements = []
        for rappatriement in self.get_all():
            if any(p.type_emballage == type_emballage for p in rappatriement.produits):
                filtered_rappatriements.append(rappatriement)
        return filtered_rappatriements

    def get_rappatriements_by_poids_min(self, poids_min: float) -> List[Rappatriement]:
        """
        Récupère les rapatriements avec un poids minimum

        Args:
            poids_min: Poids minimum requis

        Returns:
            List[Rappatriement]: Liste des rapatriements correspondants
        """
        filtered_rappatriements = []
        for rappatriement in self.get_all():
            if rappatriement.calculer_poids_total() >= poids_min:
                filtered_rappatriements.append(rappatriement)
        return filtered_rappatriements

    def get_rappatriements_by_nb_palettes_min(self, nb_palettes_min: int) -> List[Rappatriement]:
        """
        Récupère les rapatriements avec un nombre minimum de palettes

        Args:
            nb_palettes_min: Nombre minimum de palettes requis

        Returns:
            List[Rappatriement]: Liste des rapatriements correspondants
        """
        filtered_rappatriements = []
        for rappatriement in self.get_all():
            if rappatriement.calculer_nb_palettes_total() >= nb_palettes_min:
                filtered_rappatriements.append(rappatriement)
        return filtered_rappatriements

    def get_statistiques_globales(self) -> Dict[str, Any]:
        """
        Calcule les statistiques globales des rapatriements

        Returns:
            Dict[str, Any]: Dictionnaire des statistiques
        """
        rappatriements = self.get_all()

        if not rappatriements:
            return {
                "total_rappatriements": 0,
                "total_produits": 0,
                "poids_total": 0,
                "total_palettes": 0,
                "total_contenants": 0,
                "types_emballage": {},
                "responsables": {}
            }

        stats = {
            "total_rappatriements": len(rappatriements),
            "total_produits": sum(len(r.produits) for r in rappatriements),
            "poids_total": sum(r.calculer_poids_total() for r in rappatriements),
            "total_palettes": sum(r.calculer_nb_palettes_total() for r in rappatriements),
            "total_contenants": sum(r.calculer_nb_contenants_total() for r in rappatriements),
            "types_emballage": {},
            "responsables": {}
        }

        # Statistiques par type d'emballage
        for rappatriement in rappatriements:
            for produit in rappatriement.produits:
                type_emb = produit.type_emballage
                if type_emb not in stats["types_emballage"]:
                    stats["types_emballage"][type_emb] = {"count": 0, "poids": 0}
                stats["types_emballage"][type_emb]["count"] += 1
                stats["types_emballage"][type_emb]["poids"] += produit.poids_net

        # Statistiques par responsable
        for rappatriement in rappatriements:
            responsable = rappatriement.responsable_diffusion
            if responsable not in stats["responsables"]:
                stats["responsables"][responsable] = {"count": 0, "poids_total": 0}
            stats["responsables"][responsable]["count"] += 1
            stats["responsables"][responsable]["poids_total"] += rappatriement.calculer_poids_total()

        return stats

    def get_rappatriements_recents(self, nb_jours: int = 30) -> List[Rappatriement]:
        """
        Récupère les rapatriements récents

        Args:
            nb_jours: Nombre de jours pour définir "récent"

        Returns:
            List[Rappatriement]: Liste des rapatriements récents
        """
        from datetime import timedelta
        date_limite = datetime.now().replace(tzinfo=None) - timedelta(days=nb_jours)
        filtered_rappatriements = []

        for rappatriement in self.get_all():
            # Considérer comme récent si la date de demande ou de dernière MAJ est récente
            if (rappatriement.date_demande and rappatriement.date_demande >= date_limite) or \
               (rappatriement.date_derniere_maj and rappatriement.date_derniere_maj >= date_limite):
                filtered_rappatriements.append(rappatriement)

        return filtered_rappatriements

    def get_rappatriements_en_cours(self) -> List[Rappatriement]:
        """
        Récupère tous les rapatriements en cours
        Pour les rapatriements, on considère que tous sont "en cours"
        jusqu'à leur livraison/réception finale

        Returns:
            List[Rappatriement]: Liste de tous les rapatriements
        """
        return self.get_all()



    def update_rappatriement(self, numero_transfert: str,
                           updates: Dict[str, Any]) -> Optional[Rappatriement]:
        """
        Met à jour un rapatriement

        Args:
            numero_transfert: Numéro de transfert du rapatriement
            updates: Dictionnaire des mises à jour

        Returns:
            Optional[Rappatriement]: Le rapatriement mis à jour ou None
        """
        rappatriement = self.get_rappatriement_by_numero(numero_transfert)
        if not rappatriement:
            return None

        # Appliquer les mises à jour
        for field, value in updates.items():
            if hasattr(rappatriement, field):
                setattr(rappatriement, field, value)

        return self.update(numero_transfert, rappatriement)

    def delete_rappatriement(self, numero_transfert: str) -> bool:
        """
        Supprime un rapatriement

        Args:
            numero_transfert: Numéro de transfert du rapatriement

        Returns:
            bool: True si supprimé, False sinon
        """
        return self.delete(numero_transfert)

    def ajouter_produit_to_rappatriement(self, numero_transfert: str,
                                       produit: ProduitRappatriement) -> Optional[Rappatriement]:
        """
        Ajoute un produit à un rapatriement

        Args:
            numero_transfert: Numéro de transfert du rapatriement
            produit: Produit à ajouter

        Returns:
            Optional[Rappatriement]: Le rapatriement mis à jour ou None
        """
        rappatriement = self.get_rappatriement_by_numero(numero_transfert)
        if not rappatriement:
            return None

        rappatriement.ajouter_produit(produit)
        return self.update(numero_transfert, rappatriement)

    def retirer_produit_from_rappatriement(self, numero_transfert: str,
                                         code_produit: str) -> Optional[Rappatriement]:
        """
        Retire un produit d'un rapatriement

        Args:
            numero_transfert: Numéro de transfert du rapatriement
            code_produit: Code du produit à retirer

        Returns:
            Optional[Rappatriement]: Le rapatriement mis à jour ou None
        """
        rappatriement = self.get_rappatriement_by_numero(numero_transfert)
        if not rappatriement:
            return None

        # Retirer le produit
        rappatriement.produits = [p for p in rappatriement.produits if p.code_prdt != code_produit]
        return self.update(numero_transfert, rappatriement)

    def _generate_transfer_number(self) -> str:
        """
        Génère un numéro de transfert unique

        Returns:
            str: Numéro de transfert unique
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        existing_numbers = [r.numero_transfert for r in self.get_all()]

        # Format: YYYYMMDDHHMMSS + compteur si besoin
        counter = 1
        numero = f"{timestamp}"

        while numero in existing_numbers:
            numero = f"{timestamp}{counter:03d}"
            counter += 1

        return numero

    def import_from_file(self, file_path: str) -> int:
        """
        Importe les rapatriements depuis un fichier CSV ou XLSX

        Args:
            file_path: Chemin vers le fichier des rapatriements

        Returns:
            int: Nombre de rapatriements importés
        """
        imported_count = 0
        try:
            if file_path.endswith('.csv'):
                raise ValueError("Le fichier doit être un fichier XLSX")
            elif file_path.endswith('.xlsx'):
                from lib.decoders.rappatriements.xlsx import XLSXRappatriementsDecoder
                decoder = XLSXRappatriementsDecoder()
            else:
                raise ValueError("Le fichier doit être un fichier CSV ou XLSX")

            rapatriements = decoder.decode_file(file_path)

            for rappatriement in rapatriements:
                # Utiliser create_rappatriement qui génère automatiquement le numéro si nécessaire
                if not rappatriement.numero_transfert:
                    rappatriement.numero_transfert = self._generate_transfer_number()

                # Ajouter directement sans vérification de doublon
                self.create(rappatriement)
                print(f"✓ Rapatriement {rappatriement.numero_transfert} ajouté depuis {Path(file_path).name}")
                imported_count += 1
        except Exception as e:
            print(f"❌ Erreur lors de l'import {file_path}: {e}")

        return imported_count

    def import_from_csv(self, csv_path: str) -> int:
        """
        Importe les rapatriements depuis un fichier CSV (compatibilité)

        Args:
            csv_path: Chemin vers le fichier CSV

        Returns:
            int: Nombre de rapatriements importés
        """
        return self.import_from_file(csv_path)

    def import_from_csv_directory(self, directory_path: str) -> int:
        """
        Importe tous les fichiers CSV de rapatriements depuis un répertoire

        Args:
            directory_path: Chemin vers le répertoire contenant les fichiers CSV

        Returns:
            int: Nombre total de rapatriements importés
        """
        from lib.paths import get_input_file
        import os

        total_imported = 0
        directory = Path(directory_path)

        if not directory.exists():
            print(f"❌ Répertoire introuvable : {directory}")
            return 0

        # Trouver tous les fichiers CSV
        csv_files = list(directory.glob("*.csv"))

        if not csv_files:
            print(f"ℹ️ Aucun fichier CSV trouvé dans {directory}")
            return 0

        print(f"📁 Traitement de {len(csv_files)} fichiers CSV dans {directory}")

        for csv_file in csv_files:
            try:
                count = self.import_from_csv(str(csv_file))
                total_imported += count
            except Exception as e:
                print(f"❌ Erreur avec le fichier {csv_file.name}: {e}")

        print(f"✅ Import terminé : {total_imported} rapatriements importés au total")
        return total_imported

    def import_from_csv_files(self, csv_files: List[str]) -> int:
        """
        Importe les rapatriements depuis une liste de fichiers CSV

        Args:
            csv_files: Liste des chemins vers les fichiers CSV

        Returns:
            int: Nombre total de rapatriements importés
        """
        total_imported = 0

        for csv_file in csv_files:
            try:
                count = self.import_from_csv(csv_file)
                total_imported += count
            except Exception as e:
                print(f"❌ Erreur avec le fichier {csv_file}: {e}")

        print(f"✅ Import de {len(csv_files)} fichiers terminé : {total_imported} rapatriements importés")
        return total_imported

    def append_csv_file(self, csv_path: str) -> int:
        """
        Ajoute un nouveau fichier CSV aux rapatriements existants
        Cette méthode est un alias de import_from_csv pour plus de clarté

        Args:
            csv_path: Chemin vers le nouveau fichier CSV

        Returns:
            int: Nombre de rapatriements ajoutés
        """
        print(f"📥 Ajout du fichier CSV : {Path(csv_path).name}")
        return self.import_from_csv(csv_path)

    def scan_and_import_new_csv(self, directory_path: str,
                               processed_files_log: Optional[str] = None) -> int:
        """
        Scanne un répertoire pour de nouveaux fichiers CSV et les importe

        Args:
            directory_path: Répertoire à scanner
            processed_files_log: Fichier de log des fichiers déjà traités (optionnel)

        Returns:
            int: Nombre de rapatriements importés
        """
        directory = Path(directory_path)
        if not directory.exists():
            print(f"❌ Répertoire introuvable : {directory}")
            return 0

        # Gérer le fichier de log des fichiers traités
        if processed_files_log:
            log_file = Path(processed_files_log)
        else:
            log_file = get_output_file("processed_rappatriement_files.json", "logs")
            log_file.parent.mkdir(parents=True, exist_ok=True)

        # Charger la liste des fichiers déjà traités
        processed_files = set()
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    processed_files = set(json.load(f))
            except Exception as e:
                print(f"⚠️ Erreur lors de la lecture du log : {e}")

        # Trouver les nouveaux fichiers CSV
        csv_files = list(directory.glob("*.csv"))
        new_files = [f for f in csv_files if str(f) not in processed_files]

        if not new_files:
            print(f"ℹ️ Aucun nouveau fichier CSV trouvé dans {directory}")
            return 0

        print(f"📁 Traitement de {len(new_files)} nouveaux fichiers CSV")

        total_imported = 0
        newly_processed = []

        for csv_file in new_files:
            try:
                count = self.import_from_csv(str(csv_file))
                total_imported += count
                newly_processed.append(str(csv_file))
            except Exception as e:
                print(f"❌ Erreur avec le fichier {csv_file.name}: {e}")

        # Mettre à jour le log des fichiers traités
        if newly_processed:
            processed_files.update(newly_processed)
            try:
                with open(log_file, 'w', encoding='utf-8') as f:
                    json.dump(list(processed_files), f, ensure_ascii=False, indent=2)
                print(f"📝 Log mis à jour : {log_file}")
            except Exception as e:
                print(f"⚠️ Erreur lors de la mise à jour du log : {e}")

        print(f"✅ Scan terminé : {total_imported} nouveaux rapatriements importés")
        return total_imported

    def filter_rappatriements_advanced(self,
                                     responsable: Optional[str] = None,
                                     date_debut: Optional[datetime] = None,
                                     date_fin: Optional[datetime] = None,
                                     adresse_destinataire: Optional[str] = None,
                                     adresse_enlevement: Optional[str] = None,
                                     code_produit: Optional[str] = None,
                                     type_emballage: Optional[str] = None,
                                     poids_min: Optional[float] = None,
                                     poids_max: Optional[float] = None,
                                     nb_palettes_min: Optional[int] = None,
                                     nb_palettes_max: Optional[int] = None) -> List[Rappatriement]:
        """
        Filtrage avancé des rapatriements avec critères multiples

        Args:
            responsable: Nom du responsable (recherche partielle)
            date_debut: Date de début pour filtrage par date de demande
            date_fin: Date de fin pour filtrage par date de demande
            adresse_destinataire: Adresse destinataire (recherche partielle)
            adresse_enlevement: Adresse enlèvement (recherche partielle)
            code_produit: Code produit à rechercher
            type_emballage: Type d'emballage
            poids_min: Poids minimum
            poids_max: Poids maximum
            nb_palettes_min: Nombre minimum de palettes
            nb_palettes_max: Nombre maximum de palettes

        Returns:
            List[Rappatriement]: Liste des rapatriements correspondants
        """
        rappatriements = self.get_all()

        # Filtrer par responsable
        if responsable:
            rappatriements = [r for r in rappatriements
                            if responsable.lower() in r.responsable_diffusion.lower()]

        # Filtrer par plage de dates
        if date_debut:
            rappatriements = [r for r in rappatriements
                            if r.date_demande and r.date_demande >= date_debut]
        if date_fin:
            rappatriements = [r for r in rappatriements
                            if r.date_demande and r.date_demande <= date_fin]

        # Filtrer par adresses
        if adresse_destinataire:
            rappatriements = [r for r in rappatriements
                            if adresse_destinataire.lower() in r.adresse_destinataire.lower()]
        if adresse_enlevement:
            rappatriements = [r for r in rappatriements
                            if adresse_enlevement.lower() in r.adresse_enlevement.lower()]

        # Filtrer par produit
        if code_produit:
            rappatriements = [r for r in rappatriements
                            if any(p.code_prdt == code_produit for p in r.produits)]

        # Filtrer par type d'emballage
        if type_emballage:
            rappatriements = [r for r in rappatriements
                            if any(p.type_emballage == type_emballage for p in r.produits)]

        # Filtrer par poids
        if poids_min:
            rappatriements = [r for r in rappatriements
                            if r.calculer_poids_total() >= poids_min]
        if poids_max:
            rappatriements = [r for r in rappatriements
                            if r.calculer_poids_total() <= poids_max]

        # Filtrer par nombre de palettes
        if nb_palettes_min:
            rappatriements = [r for r in rappatriements
                            if r.calculer_nb_palettes_total() >= nb_palettes_min]
        if nb_palettes_max:
            rappatriements = [r for r in rappatriements
                            if r.calculer_nb_palettes_total() <= nb_palettes_max]

        return rappatriements

    def export_to_csv(self, filepath: Path) -> bool:
        """
        Exporte tous les rapatriements vers un fichier CSV

        Args:
            filepath: Chemin du fichier CSV

        Returns:
            bool: True si exporté avec succès
        """
        try:
            import csv

            rappatriements = self.get_all()

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'numero_transfert', 'responsable_diffusion', 'date_demande',
                    'date_reception_souhaitee', 'adresse_destinataire', 'adresse_enlevement',
                    'nb_produits', 'poids_total', 'nb_palettes_total', 'nb_contenants_total'
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for rappatriement in rappatriements:
                    writer.writerow({
                        'numero_transfert': rappatriement.numero_transfert,
                        'responsable_diffusion': rappatriement.responsable_diffusion,
                        'date_demande': rappatriement.date_demande.isoformat() if rappatriement.date_demande else '',
                        'date_reception_souhaitee': rappatriement.date_reception_souhaitee.isoformat() if rappatriement.date_reception_souhaitee else '',
                        'adresse_destinataire': rappatriement.adresse_destinataire,
                        'adresse_enlevement': rappatriement.adresse_enlevement,
                        'nb_produits': len(rappatriement.produits),
                        'poids_total': rappatriement.calculer_poids_total(),
                        'nb_palettes_total': rappatriement.calculer_nb_palettes_total(),
                        'nb_contenants_total': rappatriement.calculer_nb_contenants_total()
                    })

            return True

        except Exception as e:
            print(f"Erreur lors de l'export CSV: {e}")
            return False
