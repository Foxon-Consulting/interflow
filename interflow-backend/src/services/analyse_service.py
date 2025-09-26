"""
Service pour analyser la couverture des besoins par les stocks disponibles
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from models.besoin import Besoin, Etat
from models.stock import Stock
from models.reception import Reception, TypeReception
from models.rappatriement import Rappatriement
from models.analyse import (
    AnalyseCouverture,
    AnalyseMatiere,
    CouvertureBesoin,
    AnalyseChronologique,
    EtapeChronologique,
    PremierBesoinNonCouvert,
    StatistiquesMatiere
)
from repositories import BesoinsRepository, StocksRepository, ReceptionsRepository, RappatriementsRepository


class AnalyseService:
    """
    Service pour analyser la couverture des besoins par les stocks et commandes
    """

    def __init__(self,
                 besoins_repo: BesoinsRepository,
                 stocks_repo: StocksRepository,
                 receptions_repo: ReceptionsRepository,
                 rappatriements_repo: RappatriementsRepository):
        """
        Initialise le service avec les repositories nécessaires

        Args:
            besoins_repo: Repository des besoins
            stocks_repo: Repository des stocks
            receptions_repo: Repository des réceptions
            rappatriements_repo: Repository des rapatriements
        """
        self.besoins_repo = besoins_repo
        self.stocks_repo = stocks_repo
        self.receptions_repo = receptions_repo
        self.rappatriements_repo = rappatriements_repo

    # ========== MÉTHODES UTILITAIRES (PRIVÉES) ==========

    def _normalize_date(self, date: Optional[datetime]) -> datetime:
        """Normalise une date en s'assurant qu'elle est naive (sans timezone)"""
        if date is None:
            return datetime.now().replace(tzinfo=None)
        elif date.tzinfo is not None:
            return date.replace(tzinfo=None)
        return date

    def _string_to_etat(self, etat_str: str) -> Etat:
        """Convertit un état string vers l'enum Etat"""
        mapping = {
            "COUVERT": Etat.COUVERT,
            "PARTIEL": Etat.PARTIEL,
            "NON_COUVERT": Etat.NON_COUVERT
        }
        return mapping.get(etat_str, Etat.NON_COUVERT)

    def _calculate_rappatriements_quantity(self, code_mp: str, rappatriements: List[Rappatriement]) -> float:
        """Calcule la quantité de rappatriements pour une matière donnée"""
        quantite_total = 0.0
        for rappatriement in rappatriements:
            for produit in rappatriement.produits:
                if (code_mp.lower() in produit.code_prdt.lower() or
                    code_mp.lower() in produit.designation_prdt.lower()):
                    quantite_total += produit.poids_net
        return quantite_total

    def _calculate_coverage_state(self, stock_disponible: float, quantite_besoin: float) -> tuple[str, float, float]:
        """
        Calcule l'état de couverture d'un besoin

        Returns:
            tuple: (etat, quantite_disponible, pourcentage_couverture)
        """
        if stock_disponible >= quantite_besoin:
            return "COUVERT", quantite_besoin, 100.0
        elif stock_disponible > 0:
            return "PARTIEL", stock_disponible, (stock_disponible / quantite_besoin) * 100
        else:
            return "NON_COUVERT", 0.0, 0.0

    def _analyze_matiere_chronological_coverage(self, besoins_matiere: List[Besoin], stock_initial: float) -> List[Dict[str, Any]]:
        """
        Analyse chronologique simplifiée pour une matière

        Returns:
            Liste des résultats de couverture par besoin
        """
        besoins_tries = sorted(besoins_matiere, key=lambda b: b.echeance)
        couverture_results = []
        stock_courant = stock_initial

        for besoin in besoins_tries:
            etat_str, quantite_disponible, pourcentage = self._calculate_coverage_state(
                stock_courant, besoin.quantite
            )

            # Consommer le stock
            if etat_str == "COUVERT":
                stock_courant -= besoin.quantite
            elif etat_str == "PARTIEL":
                stock_courant = 0

            couverture_results.append({
                "besoin": besoin,
                "etat_couverture": etat_str,
                "quantite_disponible": quantite_disponible,
                "pourcentage_couverture": pourcentage,
                "stock_restant": stock_courant
            })

        return couverture_results

    # ========== MÉTHODES PUBLIQUES PRINCIPALES ==========

    def analyze_coverage(self, date_initiale: datetime = None, horizon_days: int = 5) -> AnalyseCouverture:
        """
        Analyse complète de la couverture des besoins sur un horizon donné

        Args:
            date_initiale: Date de début de l'analyse
            horizon_days: Nombre de jours d'horizon pour l'analyse

        Returns:
            AnalyseCouverture: Modèle contenant l'analyse de couverture complète
        """
        date_initiale = self._normalize_date(date_initiale)
        date_limite = date_initiale + timedelta(days=horizon_days)

        # Récupérer les besoins par matière
        besoins_par_matiere = self.besoins_repo.get_besoins_actuels_by_horizon_grouped(horizon_days, date_initiale)

        # Analyser chaque matière
        analyses_matiere = {}
        for code_mp, besoins_matiere in besoins_par_matiere.items():
            analyse_matiere = self._analyze_single_matiere(code_mp, besoins_matiere)
            analyses_matiere[code_mp] = self._create_analyse_matiere_pydantic(analyse_matiere)

        # Créer les statistiques globales
        all_couvertures = []
        for analyse in analyses_matiere.values():
            all_couvertures.extend(analyse.couverture_par_besoin)

        stats_par_matiere = self._calculate_matiere_stats_from_couvertures(all_couvertures)

        return AnalyseCouverture(
            horizon_jours=horizon_days,
            date_initiale=date_initiale,
            date_limite=date_limite,
            analyse_par_matiere=analyses_matiere,
            statistiques_par_matiere=stats_par_matiere
        )

    def analyze_matiere_coverage(self, code_mp: str, date_initiale: datetime = None, horizon_days: int = 5) -> AnalyseCouverture:
        """
        Analyse la couverture des besoins pour une matière première spécifique

        Args:
            code_mp: Code de la matière première à analyser
            date_initiale: Date de début de l'analyse
            horizon_days: Nombre de jours d'horizon pour l'analyse

        Returns:
            AnalyseCouverture: Modèle contenant l'analyse de couverture pour cette matière
        """
        date_initiale = self._normalize_date(date_initiale)
        besoins_matiere = self.besoins_repo.get_besoins_actuels_by_matiere_and_horizon(
            code_mp, horizon_days, date_initiale
        )

        if not besoins_matiere:
            return self._create_empty_analyse(code_mp, date_initiale, horizon_days)

        analyse_matiere = self._analyze_single_matiere(code_mp, besoins_matiere)
        analyse_matiere_pydantic = self._create_analyse_matiere_pydantic(analyse_matiere)

        return AnalyseCouverture(
            horizon_jours=horizon_days,
            date_initiale=date_initiale,
            date_limite=date_initiale + timedelta(days=horizon_days),
            analyse_par_matiere={},
            statistiques_par_matiere={},
            analyse_matiere=analyse_matiere_pydantic
        )

    def analyze_besoins(self) -> List[Besoin]:
        """
        Analyse et retourne une copie de tous les besoins avec leurs états de couverture calculés
        selon la logique chronologique (couvre les besoins les plus anciens en premier) par matière première.

        Cette fonction est pure : elle ne modifie pas les données du repository.
        Analyse tous les besoins existants sans notion d'horizon temporel.

        Returns:
            List[Besoin]: Copies de tous les besoins avec leurs états de couverture calculés
        """
        # Récupérer tous les besoins inconnus, groupés par matière
        all_besoins = self.besoins_repo.get_besoins_by_etat(Etat.INCONNU)
        besoins_par_matiere = {}

        # Grouper les besoins par matière première
        for besoin in all_besoins:
            code_mp = besoin.matiere.code_mp
            if code_mp not in besoins_par_matiere:
                besoins_par_matiere[code_mp] = []
            besoins_par_matiere[code_mp].append(besoin)

        # Liste des copies de besoins avec états calculés
        besoins_analyses = []

        for code_mp, besoins_matiere in besoins_par_matiere.items():
            # Calculer le stock disponible pour la couverture
            stock_disponible = self._get_coverage_stock_for_matiere(code_mp)

            # Analyser chronologiquement cette matière
            couverture_results = self._analyze_matiere_chronological_coverage(besoins_matiere, stock_disponible)

            # Créer les copies des besoins avec états calculés
            for result in couverture_results:
                besoin_copie = Besoin(
                    id=result["besoin"].id,
                    matiere=result["besoin"].matiere,
                    quantite=result["besoin"].quantite,
                    echeance=result["besoin"].echeance,
                    etat=self._string_to_etat(result["etat_couverture"]),
                    lot=result["besoin"].lot
                )
                besoins_analyses.append(besoin_copie)

        # Retrier par échéance pour un affichage cohérent
        return sorted(besoins_analyses, key=lambda b: b.echeance)

    # ========== MÉTHODES UTILITAIRES PRIVÉES ==========

    def _get_coverage_stock_for_matiere(self, code_mp: str) -> float:
        """Calcule le stock disponible pour la couverture d'une matière"""
        stocks_internes = self.stocks_repo.get_internal_stocks_by_matiere(code_mp)
        rappatriements = self.rappatriements_repo.get_rappatriements_by_matiere(code_mp)

        quantite_stock_internes = sum(stock.quantite for stock in stocks_internes)
        quantite_rappatriements = self._calculate_rappatriements_quantity(code_mp, rappatriements)

        return quantite_stock_internes + quantite_rappatriements

    def _analyze_single_matiere(self, code_mp: str, besoins_matiere: List[Besoin]) -> Dict[str, Any]:
        """Analyse complète d'une matière première"""
        # Récupérer les données
        stocks_internes = self.stocks_repo.get_internal_stocks_by_matiere(code_mp)
        stocks_externes = self.stocks_repo.get_external_stocks_by_matiere(code_mp)
        receptions_en_cours = self.receptions_repo.get_receptions_en_cours()
        rappatriements_en_cours = self.rappatriements_repo.get_rappatriements_by_matiere(code_mp)

        # Calculer les quantités
        quantite_stock_internes = sum(stock.quantite for stock in stocks_internes)
        quantite_rappatriements = self._calculate_rappatriements_quantity(code_mp, rappatriements_en_cours)
        quantite_receptions = sum(r.quantite for r in receptions_en_cours if r.matiere.code_mp == code_mp)

        # Stocks externes par magasin
        stocks_externes_dict = {}
        for stock in stocks_externes:
            stocks_externes_dict[stock.magasin] = stocks_externes_dict.get(stock.magasin, 0) + stock.quantite

        # Analyse chronologique
        stock_couverture = quantite_stock_internes + quantite_rappatriements
        couverture_results = self._analyze_matiere_chronological_coverage(besoins_matiere, stock_couverture)

        # Calculer les statistiques
        quantite_besoin_totale = sum(b.quantite for b in besoins_matiere)
        total_besoins = len(besoins_matiere)
        total_couverts = len([r for r in couverture_results if r["etat_couverture"] == "COUVERT"])
        taux_couverture = (total_couverts / total_besoins * 100) if total_besoins > 0 else 0

        # Analyse chronologique détaillée
        analyse_chrono = self._create_chronological_analysis(besoins_matiere, stock_couverture)

        return {
            "code_mp": code_mp,
            "nom_matiere": besoins_matiere[0].matiere.nom if besoins_matiere else "Matière inconnue",
            "total_besoins": total_besoins,
            "total_couverts": total_couverts,
            "taux_couverture": taux_couverture,
            "quantite_besoin_totale": quantite_besoin_totale,
            "quantite_stock_internes": quantite_stock_internes,
            "stocks_externes": stocks_externes_dict,
            "quantite_receptions": quantite_receptions,
            "quantite_rappatriements": quantite_rappatriements,
            "quantite_totale_disponible": quantite_stock_internes + sum(stocks_externes_dict.values()) + quantite_receptions + quantite_rappatriements,
            "stock_couverture_disponible": stock_couverture,
            "stock_manquant": max(0, quantite_besoin_totale - stock_couverture),
            "couverture_par_besoin": couverture_results,
            "analyse_chronologique": analyse_chrono
        }

    def _create_chronological_analysis(self, besoins_matiere: List[Besoin], stock_initial: float) -> Dict[str, Any]:
        """Crée l'analyse chronologique détaillée"""
        besoins_tries = sorted(besoins_matiere, key=lambda b: b.echeance)
        stock_disponible = stock_initial
        couverture_chronologique = []
        premier_besoin_non_couvert = None

        for i, besoin in enumerate(besoins_tries):
            etat_str, _, _ = self._calculate_coverage_state(stock_disponible, besoin.quantite)

            # Enregistrer le premier besoin non entièrement couvert
            if premier_besoin_non_couvert is None and etat_str != "COUVERT":
                premier_besoin_non_couvert = {
                    "index": i,
                    "echeance": besoin.echeance.strftime("%Y-%m-%d"),
                    "quantite_besoin": besoin.quantite,
                    "stock_restant": stock_disponible,
                    "quantite_manquante": besoin.quantite - stock_disponible
                }

            # Calculer stock après
            stock_apres = stock_disponible
            if etat_str == "COUVERT":
                stock_apres -= besoin.quantite
            elif etat_str == "PARTIEL":
                stock_apres = 0

            couverture_chronologique.append({
                "echeance": besoin.echeance.strftime("%Y-%m-%d"),
                "quantite_besoin": besoin.quantite,
                "stock_avant": stock_disponible,
                "stock_apres": stock_apres,
                "etat": etat_str
            })

            stock_disponible = stock_apres

        return {
            "couverture_chronologique": couverture_chronologique,
            "premier_besoin_non_couvert": premier_besoin_non_couvert,
            "stock_initial": stock_initial,
            "stock_final": stock_disponible
        }

    def _create_analyse_matiere_pydantic(self, analyse_data: Dict[str, Any]) -> AnalyseMatiere:
        """Convertit les données d'analyse en modèle Pydantic AnalyseMatiere"""
        # Créer les couvertures par besoin
        couvertures_pydantic = []
        for result in analyse_data["couverture_par_besoin"]:
            couverture = CouvertureBesoin(
                besoin=result["besoin"],
                quantite_besoin=result["besoin"].quantite,
                quantite_stock_internes=analyse_data["quantite_stock_internes"],
                stocks_externes=analyse_data["stocks_externes"],
                quantite_receptions=analyse_data["quantite_receptions"],
                quantite_rappatriements=analyse_data["quantite_rappatriements"],
                quantite_disponible_couverture=result["quantite_disponible"],
                etat_couverture=self._string_to_etat(result["etat_couverture"]),
                pourcentage_couverture=result["pourcentage_couverture"],
                stock_restant_apres_consommation=result["stock_restant"]
            )
            couvertures_pydantic.append(couverture)

        # Créer l'analyse chronologique
        analyse_chrono = self._create_analyse_chronologique_pydantic(analyse_data["analyse_chronologique"])

        return AnalyseMatiere(
            code_mp=analyse_data["code_mp"],
            nom_matiere=analyse_data["nom_matiere"],
            total_besoins=analyse_data["total_besoins"],
            total_couverts=analyse_data["total_couverts"],
            taux_couverture=analyse_data["taux_couverture"],
            quantite_besoin_totale=analyse_data["quantite_besoin_totale"],
            quantite_stock_internes=analyse_data["quantite_stock_internes"],
            stocks_externes=analyse_data["stocks_externes"],
            quantite_receptions=analyse_data["quantite_receptions"],
            quantite_rappatriements=analyse_data["quantite_rappatriements"],
            quantite_totale_disponible=analyse_data["quantite_totale_disponible"],
            stock_couverture_disponible=analyse_data["stock_couverture_disponible"],
            stock_manquant=analyse_data["stock_manquant"],
            couverture_par_besoin=couvertures_pydantic,
            analyse_chronologique=analyse_chrono
        )

    def _create_analyse_chronologique_pydantic(self, analyse_chrono: Dict[str, Any]) -> AnalyseChronologique:
        """Crée un modèle Pydantic pour l'analyse chronologique"""
        etapes_chrono = []
        for etape in analyse_chrono["couverture_chronologique"]:
            etapes_chrono.append(EtapeChronologique(
                echeance=etape["echeance"],
                quantite_besoin=etape["quantite_besoin"],
                stock_avant=etape["stock_avant"],
                stock_apres=etape["stock_apres"],
                etat=self._string_to_etat(etape["etat"])
            ))

        premier_besoin = None
        if analyse_chrono["premier_besoin_non_couvert"]:
            premier = analyse_chrono["premier_besoin_non_couvert"]
            premier_besoin = PremierBesoinNonCouvert(
                index=premier["index"],
                echeance=premier["echeance"],
                quantite_besoin=premier["quantite_besoin"],
                stock_restant=premier["stock_restant"],
                quantite_manquante=premier["quantite_manquante"]
            )

        return AnalyseChronologique(
            couverture_chronologique=etapes_chrono,
            premier_besoin_non_couvert=premier_besoin,
            stock_initial=analyse_chrono["stock_initial"],
            stock_final=analyse_chrono["stock_final"]
        )

    def _calculate_matiere_stats_from_couvertures(self, couvertures: List[CouvertureBesoin]) -> Dict[str, StatistiquesMatiere]:
        """Calcule les statistiques par matière à partir des couvertures"""
        stats_par_matiere = {}

        for couverture in couvertures:
            code_mp = couverture.besoin.matiere.code_mp
            nom = couverture.besoin.matiere.nom

            if code_mp not in stats_par_matiere:
                stats_par_matiere[code_mp] = StatistiquesMatiere(
                    nom=nom,
                    total_besoins=0,
                    total_couverts=0,
                    total_partiels=0,
                    total_non_couverts=0,
                    quantite_besoin_totale=0,
                    quantite_disponible_totale=0,
                    stocks_externes={},
                    quantite_rappatriements=0,
                    taux_couverture=0,
                    taux_partiel=0,
                    taux_non_couvert=0
                )

            stats = stats_par_matiere[code_mp]
            stats.total_besoins += 1
            stats.quantite_besoin_totale += couverture.quantite_besoin
            stats.quantite_disponible_totale += couverture.quantite_disponible_couverture

            # Éviter les doublons pour les quantités globales par matière
            if stats.quantite_rappatriements == 0:
                stats.quantite_rappatriements = couverture.quantite_rappatriements
            if not stats.stocks_externes:
                stats.stocks_externes = couverture.stocks_externes

            # Compter les états
            if couverture.etat_couverture == Etat.COUVERT:
                stats.total_couverts += 1
            elif couverture.etat_couverture == Etat.PARTIEL:
                stats.total_partiels += 1
            else:
                stats.total_non_couverts += 1

        # Calculer les pourcentages
        for stats in stats_par_matiere.values():
            if stats.total_besoins > 0:
                stats.taux_couverture = (stats.total_couverts / stats.total_besoins) * 100
                stats.taux_partiel = (stats.total_partiels / stats.total_besoins) * 100
                stats.taux_non_couvert = (stats.total_non_couverts / stats.total_besoins) * 100

        return stats_par_matiere

    def _create_empty_analyse(self, code_mp: str, date_initiale: datetime, horizon_days: int) -> AnalyseCouverture:
        """Crée une analyse vide pour une matière sans besoins"""
        analyse_matiere_vide = AnalyseMatiere(
            code_mp=code_mp,
            nom_matiere="Matière inconnue",
            total_besoins=0,
            total_couverts=0,
            taux_couverture=0,
            quantite_besoin_totale=0,
            quantite_stock_internes=0,
            stocks_externes={},
            quantite_receptions=0,
            quantite_rappatriements=0,
            quantite_totale_disponible=0,
            stock_couverture_disponible=0,
            stock_manquant=0,
            couverture_par_besoin=[],
            analyse_chronologique=AnalyseChronologique(
                couverture_chronologique=[],
                premier_besoin_non_couvert=None,
                stock_initial=0,
                stock_final=0
            )
        )

        return AnalyseCouverture(
            horizon_jours=horizon_days,
            date_initiale=date_initiale,
            date_limite=date_initiale + timedelta(days=horizon_days),
            analyse_par_matiere={},
            statistiques_par_matiere={},
            analyse_matiere=analyse_matiere_vide
        )
