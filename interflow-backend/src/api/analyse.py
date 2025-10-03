"""
Endpoints pour l'analyse de couverture des besoins
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from services.analyse_service import AnalyseService
from services.analyse_display_service import AnalyseDisplayService
from repositories.storage_strategies import JSONStorageStrategy

from services.data_service import DataService

# Configuration du logging
logger = logging.getLogger(__name__)

# Création du router pour l'analyse
router = APIRouter(prefix="/analyse", tags=["6. Analyse - Couverture"])

def get_analyse_service() -> AnalyseService:
    """Factory pour créer une instance de AnalyseService"""
    return AnalyseService(DataService().besoins_repo, DataService().stocks_repo, DataService().receptions_repo, DataService().rappatriements_repo)

@router.get("/")
async def analyze_coverage(
    horizon_days: int = Query(30, ge=1, le=365, description="Nombre de jours d'horizon pour l'analyse"),
    date_initiale: Optional[str] = Query(None, description="Date de début au format ISO (YYYY-MM-DD)")
) -> Dict[str, Any]:
    """
    Analyse complète de la couverture des besoins par les stocks disponibles

    Args:
        horizon_days: Nombre de jours d'horizon pour l'analyse (1-365)
        date_initiale: Date de début au format ISO (optionnel, défaut: aujourd'hui)

    Returns:
        Analyse complète de la couverture
    """
    try:
        # Parser la date initiale si fournie
        if date_initiale:
            try:
                date_debut = datetime.fromisoformat(date_initiale)
                # S'assurer que la date est naive (sans timezone) pour éviter les erreurs de comparaison
                if date_debut.tzinfo is not None:
                    date_debut = date_debut.replace(tzinfo=None)
            except ValueError:
                raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez le format ISO (YYYY-MM-DD)")
        else:
            # Utiliser datetime.now() sans timezone pour cohérence
            date_debut = datetime.now().replace(tzinfo=None)

        # Créer le service d'analyse
        analyse_service = get_analyse_service()

        # Effectuer l'analyse
        analyse = analyse_service.analyze_coverage(date_debut, horizon_days)

        # Créer le service d'affichage
        display_service = AnalyseDisplayService()

        # Formater la réponse
        return display_service.to_api_coverage_format(analyse)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de couverture: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/matiere/{code_mp}")
async def analyze_matiere_coverage(
    code_mp: str,
    horizon_days: int = Query(30, ge=1, le=365, description="Nombre de jours d'horizon pour l'analyse"),
    date_initiale: Optional[str] = Query(None, description="Date de début au format ISO (YYYY-MM-DD)")
) -> Dict[str, Any]:
    """
    Analyse de la couverture des besoins pour une matière première spécifique

    Args:
        code_mp: Code de la matière première à analyser
        horizon_days: Nombre de jours d'horizon pour l'analyse (1-365)
        date_initiale: Date de début au format ISO (optionnel, défaut: aujourd'hui)

    Returns:
        Analyse de couverture pour cette matière
    """
    try:
        # Parser la date initiale si fournie
        if date_initiale:
            try:
                date_debut = datetime.fromisoformat(date_initiale)
                # S'assurer que la date est naive (sans timezone) pour éviter les erreurs de comparaison
                if date_debut.tzinfo is not None:
                    date_debut = date_debut.replace(tzinfo=None)
            except ValueError:
                raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez le format ISO (YYYY-MM-DD)")
        else:
            # Utiliser datetime.now() sans timezone pour cohérence
            date_debut = datetime.now().replace(tzinfo=None)

        # Créer le service d'analyse
        analyse_service = get_analyse_service()

        # Effectuer l'analyse pour cette matière
        analyse = analyse_service.analyze_matiere_coverage(code_mp, date_debut, horizon_days)

        # Créer le service d'affichage
        display_service = AnalyseDisplayService()

        # Formater la réponse
        return display_service.to_api_matiere_format(analyse, code_mp)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de couverture pour la matière {code_mp}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/matieres")
async def get_available_matieres() -> Dict[str, Any]:
    """
    Récupère la liste des matières disponibles avec leurs statistiques de couverture

    Returns:
        Liste des matières avec leurs statistiques
    """
    try:
        # Créer le service d'analyse
        analyse_service = get_analyse_service()

        # Effectuer l'analyse complète pour obtenir les statistiques
        analyse = analyse_service.analyze_coverage()

        # Créer le service d'affichage
        display_service = AnalyseDisplayService()

        # Formater la réponse
        return display_service.to_api_matieres_list(analyse)

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des matières: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/besoins")
async def analyze_besoins() -> Dict[str, Any]:
    """
    Analyse tous les besoins existants et retourne leurs états de couverture calculés
    selon la logique chronologique (couvre les besoins les plus anciens en premier) par matière première.

    Cette fonction ne modifie pas les données du repository et analyse tous les besoins
    sans notion d'horizon temporel.

    Returns:
        Liste de tous les besoins avec leurs états de couverture calculés
    """
    try:
        # Créer le service d'analyse
        analyse_service = get_analyse_service()

        # Effectuer l'analyse de tous les besoins
        besoins_analyses = analyse_service.analyze_besoins()

        # Calculer des statistiques de résumé
        from collections import Counter
        etats = [b.etat.value for b in besoins_analyses]
        stats = Counter(etats)

        # Formater la réponse
        return {
            "metadata": {
                "total_besoins": len(besoins_analyses),
                "date_analyse": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "description": "Analyse complète de tous les besoins existants"
            },
            "statistiques": {
                "couvert": stats.get("couvert", 0),
                "partiel": stats.get("partiel", 0),
                "non_couvert": stats.get("non_couvert", 0),
                "inconnu": stats.get("inconnu", 0),
                "taux_couverture": round((stats.get("couvert", 0) / len(besoins_analyses)) * 100, 2) if besoins_analyses else 0
            },
            "besoins": [besoin.model_dump() for besoin in besoins_analyses]
        }

    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des besoins: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
