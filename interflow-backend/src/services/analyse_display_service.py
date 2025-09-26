"""
Service pour l'affichage des résultats d'analyse de couverture
"""
from datetime import datetime
from typing import Dict, Any, Optional
from models.analyse import AnalyseCouverture, AnalyseMatiere
from models.besoin import Etat


class AnalyseDisplayService:
    """
    Service pour afficher les résultats d'analyse de couverture de manière formatée
    et pour transformer les résultats en format API
    """
    
    @staticmethod
    def display_coverage_analysis(analyse: AnalyseCouverture) -> None:
        """
        Affiche les résultats de l'analyse de couverture de manière formatée
        
        Args:
            analyse: Modèle AnalyseCouverture contenant les résultats de l'analyse
        """
        print("=" * 80)
        print("📊 ANALYSE DE COUVERTURE DES BESOINS")
        print("=" * 80)
        
        # Informations générales
        print(f"\n🗓️ Horizon d'analyse: {analyse.horizon_jours} jours")
        print(f"🗓️ Date initiale: {analyse.date_initiale.strftime('%Y-%m-%d')}")
        print(f"📅 Date limite: {analyse.date_limite.strftime('%Y-%m-%d')}")
        
        # Déterminer le type d'analyse
        if analyse.analyse_matiere:
            # Analyse d'une matière unique
            analyse_matiere = analyse.analyse_matiere
            print(f"\n📈 STATISTIQUES GLOBALES:")
            print(f"   • Total besoins analysés: {analyse_matiere.total_besoins}")
            print(f"   • Total besoins couverts: {analyse_matiere.total_couverts}")
            print(f"   • Taux de couverture: {analyse_matiere.taux_couverture:.1f}%")
            
            print(f"\n🧪 ANALYSE DE LA MATIÈRE:")
            AnalyseDisplayService._display_matiere_summary(analyse_matiere.code_mp, analyse_matiere)
            
            # Besoins non couverts et partiels
            non_couverts = [c for c in analyse_matiere.couverture_par_besoin if c.etat_couverture == Etat.NON_COUVERT]
            partiels = [c for c in analyse_matiere.couverture_par_besoin if c.etat_couverture == Etat.PARTIEL]
        else:
            # Analyse complète (toutes les matières)
            # Calculer les statistiques globales
            total_besoins = sum(am.total_besoins for am in analyse.analyse_par_matiere.values())
            total_couverts = sum(am.total_couverts for am in analyse.analyse_par_matiere.values())
            taux_couverture = (total_couverts / total_besoins * 100) if total_besoins > 0 else 0
            
            print(f"\n📈 STATISTIQUES GLOBALES:")
            print(f"   • Total besoins analysés: {total_besoins}")
            print(f"   • Total besoins couverts: {total_couverts}")
            print(f"   • Taux de couverture: {taux_couverture:.1f}%")
            
            print(f"\n🧪 ANALYSE PAR MATIÈRE:")
            for code_mp, analyse_matiere in analyse.analyse_par_matiere.items():
                AnalyseDisplayService._display_matiere_summary(code_mp, analyse_matiere)
            
            # Besoins non couverts et partiels (toutes matières confondues)
            non_couverts = []
            partiels = []
            for analyse_matiere in analyse.analyse_par_matiere.values():
                non_couverts.extend([c for c in analyse_matiere.couverture_par_besoin if c.etat_couverture == Etat.NON_COUVERT])
                partiels.extend([c for c in analyse_matiere.couverture_par_besoin if c.etat_couverture == Etat.PARTIEL])
        
        if non_couverts:
            AnalyseDisplayService._display_non_couverts(non_couverts)
        
        if partiels:
            AnalyseDisplayService._display_partiels(partiels)
    
    @staticmethod
    def get_besoins_non_couverts(analyse: AnalyseCouverture) -> tuple[list, list]:
        """
        Extrait les besoins non couverts et partiels depuis l'analyse
        
        Args:
            analyse: Modèle AnalyseCouverture
            
        Returns:
            Tuple contenant (non_couverts, partiels)
        """
        if analyse.analyse_matiere:
            # Analyse d'une matière unique
            non_couverts = [c for c in analyse.analyse_matiere.couverture_par_besoin if c.etat_couverture == Etat.NON_COUVERT]
            partiels = [c for c in analyse.analyse_matiere.couverture_par_besoin if c.etat_couverture == Etat.PARTIEL]
        else:
            # Analyse complète (toutes les matières)
            non_couverts = []
            partiels = []
            for analyse_matiere in analyse.analyse_par_matiere.values():
                non_couverts.extend([c for c in analyse_matiere.couverture_par_besoin if c.etat_couverture == Etat.NON_COUVERT])
                partiels.extend([c for c in analyse_matiere.couverture_par_besoin if c.etat_couverture == Etat.PARTIEL])
        
        return non_couverts, partiels
    
    @staticmethod
    def display_detailed_matiere_analysis(code_mp: str, analyse: AnalyseCouverture) -> None:
        """
        Affiche l'analyse détaillée pour une matière spécifique
        
        Args:
            code_mp: Code de la matière première
            analyse: Analyse de couverture contenant l'analyse matière
        """
        if not analyse.analyse_matiere:
            print(f"❌ Erreur: Aucune analyse matière trouvée pour {code_mp}")
            return
            
        analyse_matiere = analyse.analyse_matiere
        
        print(f"\n" + "=" * 60)
        print(f"🔍 ANALYSE DÉTAILLÉE - {analyse_matiere.nom_matiere} ({code_mp})")
        print("=" * 60)
        
        # Informations sur les stocks
        print(f"\n📦 INFORMATIONS STOCKS:")
        print(f"   • Stock internes: {analyse_matiere.quantite_stock_internes} (utilisé pour couverture)")
        print(f"   • Stock externes: {analyse_matiere.quantite_stock_externes} (informations seulement)")
        print(f"   • Réceptions en cours: {analyse_matiere.quantite_receptions} (informations seulement)")
        print(f"   • Rapatriements: {analyse_matiere.quantite_rappatriements} (utilisé pour couverture)")
        print(f"   • Total disponible pour couverture: {analyse_matiere.quantite_totale_disponible}")
        
        # Couverture par besoin
        print(f"\n📋 COUVERTURE PAR BESOIN:")
        for i, couverture in enumerate(analyse_matiere.couverture_par_besoin, 1):
            besoin = couverture.besoin
            etat_icon = {Etat.COUVERT: "✅", Etat.PARTIEL: "⚠️", Etat.NON_COUVERT: "❌"}
            
            print(f"\n   {i}. {etat_icon[couverture.etat_couverture]} Besoin {besoin.id}")
            print(f"      Échéance: {besoin.echeance.strftime('%Y-%m-%d')}")
            print(f"      Quantité: {besoin.quantite}")
            print(f"      État: {couverture.etat_couverture.value}")
            print(f"      Stock disponible (internes + rapatriements): {couverture.quantite_disponible_couverture}")
            print(f"      Stock restant après: {couverture.stock_restant_apres_consommation}")
        
        # Analyse chronologique
        chrono = analyse_matiere.analyse_chronologique
        print(f"\n📅 SIMULATION CHRONOLOGIQUE (basée sur stocks internes + rapatriements):")
        print(f"   Stock initial: {chrono.stock_initial}")
        print(f"   Stock final: {chrono.stock_final}")
        
        for i, etape in enumerate(chrono.couverture_chronologique, 1):
            etat_icon = {Etat.COUVERT: "✅", Etat.NON_COUVERT: "❌", Etat.PARTIEL: "⚠️"}
            print(f"   {i}. {etape.echeance}: {etape.quantite_besoin} unités {etat_icon[etape.etat]}")
            print(f"      Stock avant: {etape.stock_avant} → après: {etape.stock_apres}")
    
    @staticmethod
    def display_stocks_summary(analyse: AnalyseCouverture) -> None:
        """
        Affiche un résumé détaillé des stocks pour une matière
        
        Args:
            analyse: Analyse de couverture contenant l'analyse matière
        """
        if not analyse.analyse_matiere:
            print(f"❌ Erreur: Aucune analyse matière trouvée")
            return
            
        analyse_matiere = analyse.analyse_matiere
        
        print(f"\n📊 RÉSUMÉ DES STOCKS:")
        print(f"   • Stock internes: {analyse_matiere.quantite_stock_internes} (utilisé pour couverture)")
        print(f"   • Stock externes: {analyse_matiere.quantite_stock_externes} (non utilisé)")
        print(f"   • Réceptions: {analyse_matiere.quantite_receptions} (non utilisé)")
        print(f"   • Rapatriements: {analyse_matiere.quantite_rappatriements} (utilisé pour couverture)")
        print(f"   • Total disponible: {analyse_matiere.quantite_totale_disponible}")
        
        # Calcul des pourcentages
        total_stock = analyse_matiere.quantite_stock_internes + analyse_matiere.quantite_stock_externes
        if total_stock > 0:
            pct_internes = (analyse_matiere.quantite_stock_internes / total_stock) * 100
            pct_externes = (analyse_matiere.quantite_stock_externes / total_stock) * 100
            print(f"   • Répartition: {pct_internes:.1f}% internes, {pct_externes:.1f}% externes")
    
    @staticmethod
    def display_available_matieres(analyse_complete: AnalyseCouverture) -> None:
        """
        Affiche la liste des matières disponibles
        
        Args:
            analyse_complete: Analyse complète contenant toutes les matières
        """
        print("📋 Codes de matières disponibles:")
        for mp_code in sorted(analyse_complete.couverture_par_matiere.keys()):
            nom_matiere = analyse_complete.couverture_par_matiere[mp_code].nom_matiere
            print(f"   • {mp_code}: {nom_matiere}")
    
    # === MÉTHODES DE TRANSFORMATION API ===
    
    @staticmethod
    def to_api_coverage_format(analyse: AnalyseCouverture) -> Dict[str, Any]:
        """
        Convertit l'analyse de couverture en format JSON pour l'API
        
        Args:
            analyse: Modèle AnalyseCouverture
            
        Returns:
            Dict contenant l'analyse formatée pour l'API
        """
        # Extraire les besoins non couverts et partiels
        non_couverts, partiels = AnalyseDisplayService.get_besoins_non_couverts(analyse)
        
        # Calculer les statistiques globales
        total_besoins = sum(am.total_besoins for am in analyse.analyse_par_matiere.values())
        total_couverts = sum(am.total_couverts for am in analyse.analyse_par_matiere.values())
        taux_couverture = (total_couverts / total_besoins * 100) if total_besoins > 0 else 0
        
        return {
            "metadata": {
                "date_initiale": analyse.date_initiale.isoformat(),
                "date_limite": analyse.date_limite.isoformat(),
                "horizon_jours": analyse.horizon_jours
            },
            "statistiques_globales": {
                "total_besoins": total_besoins,
                "total_couverts": total_couverts,
                "total_non_couverts": len(non_couverts),
                "total_partiels": len(partiels),
                "taux_couverture": round(taux_couverture, 2)
            },
            "analyse_par_matiere": {
                code_mp: {
                    "code_mp": analyse_matiere.code_mp,
                    "nom_matiere": analyse_matiere.nom_matiere,
                    "total_besoins": analyse_matiere.total_besoins,
                    "total_couverts": analyse_matiere.total_couverts,
                    "taux_couverture": round(analyse_matiere.taux_couverture, 2),
                    "quantite_besoin_totale": analyse_matiere.quantite_besoin_totale,
                    "quantite_stock_internes": analyse_matiere.quantite_stock_internes,
                    "stocks_externes": analyse_matiere.stocks_externes,
                    "quantite_receptions": analyse_matiere.quantite_receptions,
                    "quantite_rappatriements": analyse_matiere.quantite_rappatriements,
                    "quantite_totale_disponible": analyse_matiere.quantite_totale_disponible,
                    "stock_couverture_disponible": analyse_matiere.stock_couverture_disponible,
                    "stock_manquant": analyse_matiere.stock_manquant
                }
                for code_mp, analyse_matiere in analyse.analyse_par_matiere.items()
            },
            "besoins_non_couverts": [
                {
                    "besoin_id": couverture.besoin.id,
                    "matiere_code": couverture.besoin.matiere.code_mp,
                    "matiere_nom": couverture.besoin.matiere.nom,
                    "quantite": couverture.besoin.quantite,
                    "echeance": couverture.besoin.echeance.isoformat(),
                    "quantite_disponible": couverture.quantite_disponible_couverture,
                    "quantite_manquante": couverture.besoin.quantite - couverture.quantite_disponible_couverture
                }
                for couverture in non_couverts
            ],
            "besoins_partiels": [
                {
                    "besoin_id": couverture.besoin.id,
                    "matiere_code": couverture.besoin.matiere.code_mp,
                    "matiere_nom": couverture.besoin.matiere.nom,
                    "quantite": couverture.besoin.quantite,
                    "echeance": couverture.besoin.echeance.isoformat(),
                    "quantite_disponible": couverture.quantite_disponible_couverture,
                    "pourcentage_couverture": round(couverture.pourcentage_couverture, 2)
                }
                for couverture in partiels
            ]
        }
    
    @staticmethod
    def to_api_matiere_format(analyse: AnalyseCouverture, code_mp: str) -> Dict[str, Any]:
        """
        Convertit l'analyse d'une matière spécifique en format JSON pour l'API
        
        Args:
            analyse: Modèle AnalyseCouverture
            code_mp: Code de la matière première
            
        Returns:
            Dict contenant l'analyse de la matière formatée pour l'API
        """
        if not analyse.analyse_matiere:
            raise ValueError(f"Aucune analyse trouvée pour la matière {code_mp}")
        
        analyse_matiere = analyse.analyse_matiere
        
        return {
            "metadata": {
                "date_initiale": analyse.date_initiale.isoformat(),
                "date_limite": analyse.date_limite.isoformat(),
                "horizon_jours": analyse.horizon_jours,
                "code_mp": code_mp
            },
            "analyse_matiere": {
                "code_mp": analyse_matiere.code_mp,
                "nom_matiere": analyse_matiere.nom_matiere,
                "total_besoins": analyse_matiere.total_besoins,
                "total_couverts": analyse_matiere.total_couverts,
                "taux_couverture": round(analyse_matiere.taux_couverture, 2),
                "quantite_besoin_totale": analyse_matiere.quantite_besoin_totale,
                "quantite_stock_internes": analyse_matiere.quantite_stock_internes,
                "stocks_externes": analyse_matiere.stocks_externes,
                "quantite_receptions": analyse_matiere.quantite_receptions,
                "quantite_rappatriements": analyse_matiere.quantite_rappatriements,
                "quantite_totale_disponible": analyse_matiere.quantite_totale_disponible,
                "stock_couverture_disponible": analyse_matiere.stock_couverture_disponible,
                "stock_manquant": analyse_matiere.stock_manquant
            },
            "couverture_par_besoin": [
                {
                    "besoin_id": couverture.besoin.id,
                    "quantite": couverture.besoin.quantite,
                    "echeance": couverture.besoin.echeance.isoformat(),
                    "etat_couverture": couverture.etat_couverture.value,
                    "quantite_disponible": couverture.quantite_disponible_couverture,
                    "pourcentage_couverture": round(couverture.pourcentage_couverture, 2),
                    "stock_restant": couverture.stock_restant_apres_consommation
                }
                for couverture in analyse_matiere.couverture_par_besoin
            ],
            "analyse_chronologique": {
                "stock_initial": analyse_matiere.analyse_chronologique.stock_initial,
                "stock_final": analyse_matiere.analyse_chronologique.stock_final,
                "premier_besoin_non_couvert": (
                    {
                        "index": analyse_matiere.analyse_chronologique.premier_besoin_non_couvert.index,
                        "echeance": analyse_matiere.analyse_chronologique.premier_besoin_non_couvert.echeance,
                        "quantite_besoin": analyse_matiere.analyse_chronologique.premier_besoin_non_couvert.quantite_besoin,
                        "quantite_manquante": analyse_matiere.analyse_chronologique.premier_besoin_non_couvert.quantite_manquante
                    }
                    if analyse_matiere.analyse_chronologique.premier_besoin_non_couvert
                    else None
                ),
                "etapes_chronologiques": [
                    {
                        "echeance": etape.echeance,
                        "quantite_besoin": etape.quantite_besoin,
                        "stock_avant": etape.stock_avant,
                        "stock_apres": etape.stock_apres,
                        "etat": etape.etat.value
                    }
                    for etape in analyse_matiere.analyse_chronologique.couverture_chronologique
                ]
            }
        }
    
    @staticmethod
    def to_api_matieres_list(analyse: AnalyseCouverture) -> Dict[str, Any]:
        """
        Convertit la liste des matières disponibles en format JSON pour l'API
        
        Args:
            analyse: Analyse complète contenant toutes les matières
            
        Returns:
            Dict contenant la liste des matières formatée pour l'API
        """
        matieres = []
        for code_mp, analyse_matiere in analyse.analyse_par_matiere.items():
            matieres.append({
                "code_mp": code_mp,
                "nom_matiere": analyse_matiere.nom_matiere,
                "total_besoins": analyse_matiere.total_besoins,
                "taux_couverture": round(analyse_matiere.taux_couverture, 2)
            })
        
        # Trier par nom de matière
        matieres.sort(key=lambda x: x["nom_matiere"])
        
        return {
            "total_matieres": len(matieres),
            "matieres": matieres
        }
    
    @staticmethod
    def _display_matiere_summary(code_mp: str, analyse_matiere: AnalyseMatiere) -> None:
        """Affiche un résumé pour une matière"""
        print(f"\n   📦 Matière: {analyse_matiere.nom_matiere} ({code_mp})")
        print(f"      • Besoins: {analyse_matiere.total_besoins} | Couverts: {analyse_matiere.total_couverts}")
        print(f"      • Taux couverture: {analyse_matiere.taux_couverture:.1f}%")
        print(f"      • Quantité besoin total: {analyse_matiere.quantite_besoin_totale}")
        print(f"      • Stock internes: {analyse_matiere.quantite_stock_internes}")
        print(f"      • Réceptions en cours: {analyse_matiere.quantite_receptions}")
        print(f"      • Rapatriements en cours: {analyse_matiere.quantite_rappatriements}")
        print(f"      • Stock disponible pour couverture: {analyse_matiere.stock_couverture_disponible}")
        print(f"      • Stock manquant: {analyse_matiere.stock_manquant}")
        
        # Afficher les stocks externes par magasin
        stocks_externes_total = sum(analyse_matiere.stocks_externes.values())
        print(f"      • Stock externes: {stocks_externes_total}")
        if analyse_matiere.stocks_externes:
            for magasin, quantite in analyse_matiere.stocks_externes.items():
                print(f"        - {magasin}: {quantite}")
        print(f"      • Total disponible (couverture): {analyse_matiere.quantite_totale_disponible}")
        
        # Analyse chronologique
        chrono = analyse_matiere.analyse_chronologique
        if chrono.premier_besoin_non_couvert:
            premier = chrono.premier_besoin_non_couvert
            print(f"      ⚠️  Premier besoin non couvert: {premier.echeance} (manque {premier.quantite_manquante})")
    
    @staticmethod
    def _display_non_couverts(non_couverts: list) -> None:
        """Affiche les besoins non couverts"""
        print(f"\n❌ BESOINS NON COUVERTS ({len(non_couverts)}):")
        for couverture in non_couverts:
            besoin = couverture.besoin
            jours_restants = (besoin.echeance - datetime.now().replace(tzinfo=None)).days
            print(f"   • {besoin.matiere.nom}: {besoin.quantite} unités")
            print(f"     Échéance: {besoin.echeance.strftime('%Y-%m-%d')} ({jours_restants} jours)")
            print(f"     Disponible (internes + rapatriements): {couverture.quantite_disponible_couverture} | Manque: {besoin.quantite - couverture.quantite_disponible_couverture}")
    
    @staticmethod
    def _display_partiels(partiels: list) -> None:
        """Affiche les besoins partiellement couverts"""
        print(f"\n⚠️  BESOINS PARTIELLEMENT COUVERTS ({len(partiels)}):")
        for couverture in partiels:
            besoin = couverture.besoin
            jours_restants = (besoin.echeance - datetime.now().replace(tzinfo=None)).days
            print(f"   • {besoin.matiere.nom}: {besoin.quantite} unités")
            print(f"     Échéance: {besoin.echeance.strftime('%Y-%m-%d')} ({jours_restants} jours)")
            print(f"     Couverture: {couverture.pourcentage_couverture:.1f}%")
            print(f"     Stock disponible (internes + rapatriements): {couverture.quantite_disponible_couverture}") 