"""
Repository pour les réceptions
"""
from typing import List, Optional
from datetime import datetime
from repositories.base_repository import BaseRepository
from repositories.storage_strategies import StorageStrategy
from models.reception import Reception, EtatReception, TypeReception


class ReceptionsRepository(BaseRepository[Reception]):
    """
    Repository pour les réceptions avec méthodes métier spécifiques
    """

    def __init__(self, storage: StorageStrategy):
        super().__init__(Reception, storage, id_field="id")

    def get_receptions_list(self) -> List[Reception]:
        """
        Récupère toutes les réceptions

        Returns:
            List[Reception]: Une liste de réceptions
        """
        return self.get_all()

    def get_receptions_by_etat(self, etat: EtatReception) -> List[Reception]:
        """
        Récupère toutes les réceptions ayant un état donné

        Args:
            etat: L'état des réceptions à récupérer

        Returns:
            List[Reception]: Liste des réceptions correspondantes
        """
        receptions = self.filter(etat=etat.value)
        return receptions

    def get_receptions_by_matiere(self, code_mp: str) -> List[Reception]:
        """
        Récupère toutes les réceptions d'une matière donnée

        Args:
            code_mp: Le code de la matière première

        Returns:
            List[Reception]: Liste des réceptions correspondantes
        """
        receptions = self.get_all()
        filtered_receptions = [reception for reception in receptions if reception.matiere.code_mp == code_mp]
        return filtered_receptions

    def get_receptions_en_cours(self) -> List[Reception]:
        """
        Récupère toutes les réceptions en cours

        Returns:
            List[Reception]: Liste des réceptions en cours
        """
        return self.get_receptions_by_etat(EtatReception.EN_COURS)

    def get_receptions_terminees(self) -> List[Reception]:
        """
        Récupère toutes les réceptions terminées

        Returns:
            List[Reception]: Liste des réceptions terminées
        """
        return self.get_receptions_by_etat(EtatReception.TERMINEE)

    def get_receptions_annulees(self) -> List[Reception]:
        """
        Récupère toutes les réceptions annulées

        Returns:
            List[Reception]: Liste des réceptions annulées
        """
        return self.get_receptions_by_etat(EtatReception.ANNULEE)

    def update_etat(self, id: int, nouvel_etat: EtatReception) -> Optional[Reception]:
        """
        Met à jour l'état d'une réception

        Args:
            id: L'identifiant de la réception
            nouvel_etat: Le nouvel état de la réception

        Returns:
            Optional[Reception]: La réception mise à jour ou None si non trouvée
        """
        reception = self.get_by_id(id)
        if reception:
            reception.etat = nouvel_etat
            reception.date_modification = datetime.now().replace(tzinfo=None)
            return self.update(id, reception)
        return None

    def get_total_quantity_by_matiere(self, code_mp: str) -> float:
        """
        Calcule la quantité totale réceptionnée d'une matière

        Args:
            code_mp: Le code de la matière première

        Returns:
            float: La quantité totale réceptionnée
        """
        receptions = self.get_receptions_en_cours()
        return sum(reception.quantite for reception in receptions if reception.matiere.code_mp == code_mp)

    def get_receptions_prestataires(self) -> List[Reception]:
        """
        Récupère toutes les réceptions prestataires

        Returns:
            List[Reception]: Liste des réceptions prestataires
        """
        receptions = self.get_all()
        receptions = [reception for reception in receptions if reception.type == TypeReception.PRESTATAIRE]
        return receptions

    def get_receptions_internes(self) -> List[Reception]:
        """
        Récupère toutes les réceptions internes

        Returns:
            List[Reception]: Liste des réceptions internes
        """
        receptions = self.get_all()
        receptions = [reception for reception in receptions if reception.type == TypeReception.INTERNE]
        return receptions

    def get_receptions_by_type(self, type_reception: TypeReception) -> List[Reception]:
        """
        Récupère toutes les réceptions d'un type donné

        Args:
            type_reception: Type de réception à récupérer

        Returns:
            List[Reception]: Liste des réceptions du type spécifié
        """
        receptions = self.get_all()
        receptions = [reception for reception in receptions if reception.type == type_reception]
        return receptions

    def get_receptions_by_fournisseur(self, fournisseur: str) -> List[Reception]:
        """
        Récupère toutes les réceptions d'un fournisseur donné

        Args:
            fournisseur: Le nom du fournisseur

        Returns:
            List[Reception]: Liste des réceptions correspondantes
        """
        receptions = self.get_all()
        receptions = [reception for reception in receptions if reception.fournisseur == fournisseur]
        return receptions

    def get_receptions_relachees(self) -> List[Reception]:
        """
        Récupère toutes les réceptions relâchées

        Returns:
            List[Reception]: Liste des réceptions relâchées
        """
        return self.get_receptions_by_etat(EtatReception.RELACHE)

    def import_from_file(self, file_path: str) -> None:
        """
        Importe les réceptions depuis un fichier CSV ou XLSX

        Args:
            file_path: Chemin vers le fichier des réceptions
        """
        if file_path.endswith('.csv'):
            from lib.decoders.receptions.csv import CSVReceptionsDecoder
            super().import_from_file(file_path, CSVReceptionsDecoder)
        elif file_path.endswith('.xlsx'):
            from lib.decoders.receptions.xlsx import XLSXReceptionsDecoder
            super().import_from_file(file_path, XLSXReceptionsDecoder)
        else:
            raise ValueError("Le fichier doit être un fichier CSV ou XLSX")


    def filter_receptions_advanced(self,
                                 etat: Optional[EtatReception] = None,
                                 code_mp: Optional[str] = None,
                                 nom_matiere: Optional[str] = None,
                                 type_reception: Optional[TypeReception] = None,
                                 fournisseur: Optional[str] = None,
                                 quantite_min: Optional[float] = None,
                                 quantite_max: Optional[float] = None,
                                 date_reception_debut: Optional[datetime] = None,
                                 date_reception_fin: Optional[datetime] = None,
                                 ordre: Optional[str] = None,
                                 article: Optional[str] = None,
                                 poste: Optional[str] = None) -> List[Reception]:
        """
        Filtre les réceptions selon des critères avancés

        Args:
            etat: État de la réception
            code_mp: Code de la matière première
            nom_matiere: Nom de la matière première (recherche partielle)
            type_reception: Type de réception (INTERNE/PRESTATAIRE)
            fournisseur: Nom du fournisseur
            quantite_min: Quantité minimale
            quantite_max: Quantité maximale
            date_reception_debut: Date de réception de début
            date_reception_fin: Date de réception de fin
            ordre: Numéro d'ordre
            article: Code article
            poste: Poste de travail

        Returns:
            List[Reception]: Liste des réceptions filtrées
        """
        receptions = self.get_all()
        filtered_receptions = receptions

        # Filtre par état
        if etat is not None:
            filtered_receptions = [c for c in filtered_receptions if c.etat == etat]

        # Filtre par code matière première
        if code_mp is not None:
            filtered_receptions = [c for c in filtered_receptions
                                if c.matiere and c.matiere.code_mp == code_mp]

        # Filtre par nom de matière (recherche partielle)
        if nom_matiere is not None:
            nom_lower = nom_matiere.lower()
            filtered_receptions = [c for c in filtered_receptions
                                if c.matiere and nom_lower in c.matiere.nom.lower()]

        # Filtre par type de réception
        if type_reception is not None:
            filtered_receptions = [c for c in filtered_receptions if c.type == type_reception]

        # Filtre par fournisseur
        if fournisseur is not None:
            filtered_receptions = [c for c in filtered_receptions if c.fournisseur == fournisseur]

        # Filtre par quantité
        if quantite_min is not None:
            filtered_receptions = [c for c in filtered_receptions if c.quantite >= quantite_min]

        if quantite_max is not None:
            filtered_receptions = [c for c in filtered_receptions if c.quantite <= quantite_max]

        # Filtre par date de réception
        if date_reception_debut is not None:
            filtered_receptions = [c for c in filtered_receptions
                                if c.date_reception >= date_reception_debut]

        if date_reception_fin is not None:
            filtered_receptions = [c for c in filtered_receptions
                                if c.date_reception <= date_reception_fin]

        # Filtre par ordre
        if ordre is not None:
            filtered_receptions = [c for c in filtered_receptions if c.ordre == ordre]

        # Filtre par article
        if article is not None:
            filtered_receptions = [c for c in filtered_receptions if c.article == article]

        # Filtre par poste
        if poste is not None:
            filtered_receptions = [c for c in filtered_receptions if c.poste == poste]

        return filtered_receptions

    def get_receptions_critiques(self, seuil_jours: int = 7, date_reference: datetime = None) -> List[Reception]:
        """
        Récupère les réceptions critiques (réception proche)

        Args:
            seuil_jours: Nombre de jours pour considérer une réception comme critique
            date_reference: Date de référence pour le calcul

        Returns:
            List[Reception]: Liste des réceptions critiques
        """
        from datetime import timedelta
        if date_reference is None:
            date_reference = datetime.now().replace(tzinfo=None)
        elif date_reference.tzinfo is not None:
            date_reference = date_reference.replace(tzinfo=None)

        date_limite = date_reference + timedelta(days=seuil_jours)
        return self.filter_receptions_advanced(
            date_reception_fin=date_limite,
            etat=EtatReception.EN_COURS
        )

    def get_receptions_par_matiere(self, code_mp: str) -> List[Reception]:
        """
        Récupère toutes les réceptions d'une matière première spécifique

        Args:
            code_mp: Code de la matière première

        Returns:
            List[Reception]: Liste des réceptions de la matière
        """
        return self.filter_receptions_advanced(code_mp=code_mp)

    def get_receptions_par_fournisseur(self, fournisseur: str) -> List[Reception]:
        """
        Récupère toutes les réceptions d'un fournisseur spécifique

        Args:
            fournisseur: Nom du fournisseur

        Returns:
            List[Reception]: Liste des réceptions du fournisseur
        """
        return self.filter_receptions_advanced(fournisseur=fournisseur)

    def get_receptions_par_periode(self, date_debut: datetime, date_fin: datetime) -> List[Reception]:
        """
        Récupère les réceptions dans une période donnée (par date de réception)

        Args:
            date_debut: Date de début de la période
            date_fin: Date de fin de la période

        Returns:
            List[Reception]: Liste des réceptions dans la période
        """
        return self.filter_receptions_advanced(
            date_reception_debut=date_debut,
            date_reception_fin=date_fin
        )

    def get_receptions_en_retard(self, date_reference: datetime = None) -> List[Reception]:
        """
        Récupère les réceptions en retard (date de réception dépassée)

        Args:
            date_reference: Date de référence pour le calcul

        Returns:
            List[Reception]: Liste des réceptions en retard
        """
        if date_reference is None:
            date_reference = datetime.now().replace(tzinfo=None)
        elif date_reference.tzinfo is not None:
            date_reference = date_reference.replace(tzinfo=None)

        return self.filter_receptions_advanced(
            date_reception_fin=date_reference,
            etat=EtatReception.EN_COURS
        )
