from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional
from models.besoin import Etat, Besoin


class CouvertureBesoin(BaseModel):
    """Modèle pour la couverture d'un besoin spécifique"""
    besoin: Besoin
    quantite_besoin: float
    quantite_stock_internes: float
    stocks_externes: Dict[str, float]  # magasin -> quantité
    quantite_receptions: float
    quantite_rappatriements: float
    quantite_disponible_couverture: float
    etat_couverture: Etat
    pourcentage_couverture: float
    stock_restant_apres_consommation: float


class EtapeChronologique(BaseModel):
    """Modèle pour une étape de l'analyse chronologique"""
    echeance: str
    quantite_besoin: float
    stock_avant: float
    stock_apres: float
    etat: Etat


class PremierBesoinNonCouvert(BaseModel):
    """Modèle pour le premier besoin non couvert"""
    index: int
    echeance: str
    quantite_besoin: float
    stock_restant: float
    quantite_manquante: float


class AnalyseChronologique(BaseModel):
    """Modèle pour l'analyse chronologique"""
    couverture_chronologique: List[EtapeChronologique]
    premier_besoin_non_couvert: Optional[PremierBesoinNonCouvert] = None
    stock_initial: float
    stock_final: float


class AnalyseMatiere(BaseModel):
    """Modèle pour l'analyse d'une matière spécifique"""
    code_mp: str
    nom_matiere: str
    total_besoins: int
    total_couverts: int
    taux_couverture: float
    quantite_besoin_totale: float
    quantite_stock_internes: float
    stocks_externes: Dict[str, float]  # magasin -> quantité
    quantite_receptions: float
    quantite_rappatriements: float
    quantite_totale_disponible: float
    stock_couverture_disponible: float  # stocks internes + commandes + rapatriements
    stock_manquant: float  # quantité manquante pour couvrir tous les besoins
    couverture_par_besoin: List[CouvertureBesoin]
    analyse_chronologique: AnalyseChronologique


class StatistiquesMatiere(BaseModel):
    """Modèle pour les statistiques d'une matière"""
    nom: str
    total_besoins: int
    total_couverts: int
    total_partiels: int
    total_non_couverts: int
    quantite_besoin_totale: float
    quantite_disponible_totale: float
    stocks_externes: Dict[str, float]  # magasin -> quantité
    quantite_rappatriements: float
    taux_couverture: float
    taux_partiel: float
    taux_non_couvert: float


# Suppression de BesoinsNonCouverts car redondant avec l'Etat du Besoin


class AnalyseCouverture(BaseModel):
    """Modèle principal pour l'analyse de couverture"""
    horizon_jours: int
    date_initiale: datetime
    date_limite: datetime

    # Pour analyse complète (toutes les matières)
    analyse_par_matiere: Dict[str, AnalyseMatiere]
    statistiques_par_matiere: Dict[str, StatistiquesMatiere]

    # Pour analyse matière unique
    analyse_matiere: Optional[AnalyseMatiere] = None

    def total_besoins(self) -> int:
        if self.analyse_matiere:
            return self.analyse_matiere.total_besoins
        return sum(am.total_besoins for am in self.analyse_par_matiere.values())

    def total_couverts(self) -> int:
        if self.analyse_matiere:
            return self.analyse_matiere.total_couverts
        return sum(am.total_couverts for am in self.analyse_par_matiere.values())

    def taux_couverture(self) -> float:
        total = self.total_besoins()
        if total == 0:
            return 0.0
        return self.total_couverts() / total * 100
