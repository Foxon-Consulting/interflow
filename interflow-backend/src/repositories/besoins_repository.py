"""
Repository pour les besoins
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from repositories.base_repository import BaseRepository
from repositories.storage_strategies import StorageStrategy
from models.besoin import Besoin, Etat


class BesoinsRepository(BaseRepository[Besoin]):
    """
    Repository pour les besoins avec méthodes métier spécifiques
    """

    def __init__(self, storage: StorageStrategy):
        super().__init__(Besoin, storage, id_field="id")

    def get_besoins_by_etat(self, etat: Etat) -> List[Besoin]:
        """
        Récupère tous les besoins ayant un état donné

        Args:
            etat: L'état des besoins à récupérer

        Returns:
            List[Besoin]: Liste des besoins correspondants
        """
        return self.filter_besoins_advanced(etat=etat)



    def get_besoins_aggregated_by_timelapse(self, nb_jours: int, date_debut: datetime = None) -> List[Besoin]:
        """
        Récupère les besoins agrégés dans un intervalle de temps

        Args:
            nb_jours: Nombre de jours à considérer
            date_debut: Date de début de l'intervalle

        Returns:
            List[Besoin]: Liste des besoins agrégés
        """
        if date_debut is None:
            date_debut = datetime.now().replace(tzinfo=None)
        elif date_debut.tzinfo is not None:
            date_debut = date_debut.replace(tzinfo=None)

        date_fin = date_debut + timedelta(days=nb_jours)
        besoins_filtered = self.filter_besoins_advanced(
            date_debut=date_debut,
            date_fin=date_fin
        )
        besoins_aggregated = []

        for besoin in besoins_filtered:
            # On cherche si un besoin similaire existe déjà
            besoin_similaire = next((b for b in besoins_aggregated
                                   if b.matiere == besoin.matiere
                                   and b.etat == besoin.etat
                                   and b.lot == besoin.lot), None)

            if besoin_similaire:
                # Si on trouve un besoin similaire, on additionne les quantités
                besoin_similaire.quantite += besoin.quantite
            else:
                # Sinon on ajoute le nouveau besoin
                besoins_aggregated.append(besoin)

        return besoins_aggregated

    def filter_besoins(self, besoins: List[Besoin], **filters) -> List[Besoin]:
        """
        Filtre les besoins selon les critères spécifiés.

        Args:
            besoins: Liste des besoins à filtrer
            **filters: Critères de filtrage sous forme de paires clé-valeur
                     (ex: matiere=matiere_obj, etat=Etat.INCONNU, lot="LOT1", etc.)

        Returns:
            List[Besoin]: Nouvelle liste contenant uniquement les besoins correspondant aux critères
        """
        filtered_besoins = besoins

        for key, value in filters.items():
            if value is not None:  # On ignore les filtres None
                filtered_besoins = [
                    besoin for besoin in filtered_besoins
                    if getattr(besoin, key) == value
                ]

        return filtered_besoins

    def update_etat(self, id: int, nouvel_etat: Etat) -> Optional[Besoin]:
        """
        Met à jour l'état d'un besoin

        Args:
            id: L'identifiant du besoin
            nouvel_etat: Le nouvel état du besoin

        Returns:
            Optional[Besoin]: Le besoin mis à jour ou None si non trouvé
        """
        besoin = self.get_by_id(id)
        if besoin:
            besoin.etat = nouvel_etat
            return self.update(id, besoin)
        return None

    def import_from_file(self, file_path: str) -> None:
        """
        Importe les besoins depuis un fichier CSV ou XLSX

        Args:
            file_path: Chemin vers le fichier des besoins
        """
        if file_path.endswith('.csv'):
            from lib.decoders.besoins.csv import CSVBesoinsDecoder
            super().import_from_file(file_path, CSVBesoinsDecoder)
        elif file_path.endswith('.xlsx'):
            from lib.decoders.besoins.xlsx import XLSXBesoinsDecoder
            super().import_from_file(file_path, XLSXBesoinsDecoder)
        else:
            raise ValueError("Le fichier doit être un fichier CSV ou XLSX")

    def import_from_csv(self, csv_path: str = "data/besoins.csv") -> None:
        """
        Importe les besoins depuis un fichier CSV (compatibilité)

        Args:
            csv_path: Chemin vers le fichier CSV des besoins
        """
        self.import_from_file(csv_path)

    def filter_besoins_advanced(self,
                               etat: Optional[Etat] = None,
                               code_mp: Optional[str] = None,
                               nom_matiere: Optional[str] = None,
                               date_debut: Optional[datetime] = None,
                               date_fin: Optional[datetime] = None,
                               quantite_min: Optional[float] = None,
                               quantite_max: Optional[float] = None,
                               lot: Optional[str] = None) -> List[Besoin]:
        """
        Filtre les besoins selon des critères avancés

        Args:
            etat: État des besoins à filtrer
            code_mp: Code de la matière première
            nom_matiere: Nom de la matière première (recherche partielle)
            date_debut: Date de début pour l'échéance
            date_fin: Date de fin pour l'échéance
            quantite_min: Quantité minimale
            quantite_max: Quantité maximale
            lot: Lot spécifique

        Returns:
            List[Besoin]: Liste des besoins filtrés
        """
        besoins = self.get_all()
        filtered_besoins = besoins

        # Filtre par état
        if etat is not None:
            filtered_besoins = [b for b in filtered_besoins if b.etat == etat]

        # Filtre par code matière première
        if code_mp is not None:
            filtered_besoins = [b for b in filtered_besoins if b.matiere.code_mp == code_mp]

        # Filtre par nom de matière (recherche partielle)
        if nom_matiere is not None:
            nom_lower = nom_matiere.lower()
            filtered_besoins = [b for b in filtered_besoins
                              if nom_lower in b.matiere.nom.lower()]

        # Filtre par échéance
        if date_debut is not None:
            filtered_besoins = [b for b in filtered_besoins if b.echeance >= date_debut]

        if date_fin is not None:
            filtered_besoins = [b for b in filtered_besoins if b.echeance <= date_fin]

        # Filtre par quantité
        if quantite_min is not None:
            filtered_besoins = [b for b in filtered_besoins if b.quantite >= quantite_min]

        if quantite_max is not None:
            filtered_besoins = [b for b in filtered_besoins if b.quantite <= quantite_max]

        # Filtre par lot
        if lot is not None:
            filtered_besoins = [b for b in filtered_besoins if b.lot == lot]

        return filtered_besoins

    def get_besoins_actuels_by_horizon(self, horizon_days: int, date_initiale: datetime = None) -> List[Besoin]:
        """
        Récupère les besoins inconnus dans un horizon temporel donné

        Args:
            horizon_days: Nombre de jours d'horizon pour l'analyse
            date_initiale: Date de début de l'analyse

        Returns:
            List[Besoin]: Liste des besoins inconnus dans l'horizon
        """
        if date_initiale is None:
            date_initiale = datetime.now().replace(tzinfo=None)
        elif date_initiale.tzinfo is not None:
            date_initiale = date_initiale.replace(tzinfo=None)

        besoins_actuels = self.get_besoins_by_etat(Etat.INCONNU)
        date_limite = date_initiale + timedelta(days=horizon_days)

        return [
            besoin for besoin in besoins_actuels
            if besoin.echeance <= date_limite
        ]

    def get_besoins_critiques(self, seuil_jours: int = 7, date_reference: datetime = None) -> List[Besoin]:
        """
        Récupère les besoins critiques (échéance proche)

        Args:
            seuil_jours: Nombre de jours pour considérer un besoin comme critique
            date_reference: Date de référence pour le calcul

        Returns:
            List[Besoin]: Liste des besoins critiques
        """
        if date_reference is None:
            date_reference = datetime.now().replace(tzinfo=None)
        elif date_reference.tzinfo is not None:
            date_reference = date_reference.replace(tzinfo=None)

        date_limite = date_reference + timedelta(days=seuil_jours)
        return self.filter_besoins_advanced(
            date_fin=date_limite,
                            etat=Etat.INCONNU
        )



    def group_besoins_by_matiere(self, besoins: List[Besoin]) -> Dict[str, List[Besoin]]:
        """
        Groupe les besoins par matière première

        Args:
            besoins: Liste des besoins à grouper

        Returns:
            Dict[str, List[Besoin]]: Besoins groupés par code_mp
        """
        besoins_par_matiere = {}
        for besoin in besoins:
            code_mp = besoin.matiere.code_mp
            if code_mp not in besoins_par_matiere:
                besoins_par_matiere[code_mp] = []
            besoins_par_matiere[code_mp].append(besoin)
        return besoins_par_matiere

    def sort_besoins_by_echeance(self, besoins: List[Besoin], reverse: bool = False) -> List[Besoin]:
        """
        Trie les besoins par échéance

        Args:
            besoins: Liste des besoins à trier
            reverse: True pour trier en ordre décroissant

        Returns:
            List[Besoin]: Besoins triés par échéance
        """
        return sorted(besoins, key=lambda x: x.echeance, reverse=reverse)

    def calculate_total_quantite(self, besoins: List[Besoin]) -> float:
        """
        Calcule la quantité totale des besoins

        Args:
            besoins: Liste des besoins

        Returns:
            float: Quantité totale
        """
        return sum(besoin.quantite for besoin in besoins)

    def get_besoins_actuels_by_horizon_grouped(self, horizon_days: int, date_initiale: datetime = None) -> Dict[str, List[Besoin]]:
        """
        Récupère les besoins inconnus dans un horizon temporel donné, groupés par matière première

        Args:
            horizon_days: Nombre de jours d'horizon pour l'analyse
            date_initiale: Date de début de l'analyse

        Returns:
            Dict[str, List[Besoin]]: Besoins groupés par code de matière première
        """
        besoins_actuels = self.get_besoins_actuels_by_horizon(horizon_days, date_initiale)
        return self.group_besoins_by_matiere(besoins_actuels)

    def get_besoins_actuels_by_matiere_and_horizon(self, code_mp: str, horizon_days: int, date_initiale: datetime = None) -> List[Besoin]:
        """
        Récupère les besoins inconnus d'une matière première dans un horizon temporel donné

        Args:
            code_mp: Code de la matière première
            horizon_days: Nombre de jours d'horizon pour l'analyse
            date_initiale: Date de début de l'analyse

        Returns:
            List[Besoin]: Liste des besoins inconnus de cette matière dans l'horizon
        """
        besoins_actuels = self.get_besoins_actuels_by_horizon(horizon_days, date_initiale)
        return [besoin for besoin in besoins_actuels if besoin.matiere.code_mp == code_mp]
