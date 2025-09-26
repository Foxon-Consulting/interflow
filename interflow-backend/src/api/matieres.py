"""
Endpoints pour la gestion des matières
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from repositories.storage_strategies import JSONStorageStrategy
from repositories import MatieresPremieresRepository
from models.matieres import Matiere

# Configuration du logging
logger = logging.getLogger(__name__)

# Création du router pour les matières
router = APIRouter(prefix="/matieres", tags=["5. Matières - CRUD"])

# Factory functions
def get_storage_strategy():
    """Factory pour créer une instance de JSONStorageStrategy"""
    return JSONStorageStrategy()

def get_matieres_repo() -> MatieresPremieresRepository:
    """Factory pour créer une instance de MatieresPremieresRepository"""
    return MatieresPremieresRepository(get_storage_strategy())

@router.get("/")
async def get_matieres() -> Dict[str, Any]:
    """
    Récupère toutes les matières

    Returns:
        Liste des matières
    """
    try:
        repo = get_matieres_repo()
        matieres = repo.get_all()
        return {
            "total_matieres": len(matieres),
            "matieres": [matiere.model_dump() for matiere in matieres]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des matières: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/{code_mp}")
async def get_matiere_by_code(code_mp: str) -> Dict[str, Any]:
    """
    Récupère une matière par code MP

    Args:
        code_mp: Code de la matière première

    Returns:
        Données de la matière
    """
    try:
        repo = get_matieres_repo()
        matiere = repo.get_by_code_mp(code_mp)
        if not matiere:
            raise HTTPException(status_code=404, detail="Matière non trouvée")
        return matiere.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la matière {code_mp}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/")
async def create_matiere(matiere_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crée une nouvelle matière

    Args:
        matiere_data: Données de la matière à créer

    Returns:
        Matière créée
    """
    try:
        repo = get_matieres_repo()
        matiere = Matiere.from_model_dump(matiere_data)
        matiere_created = repo.create(matiere)
        return matiere_created.model_dump()
    except Exception as e:
        logger.error(f"Erreur lors de la création de la matière: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/{code_mp}")
async def update_matiere(code_mp: str, matiere_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Met à jour une matière existante

    Args:
        code_mp: Code de la matière à mettre à jour
        matiere_data: Nouvelles données de la matière

    Returns:
        Matière mise à jour
    """
    try:
        repo = get_matieres_repo()
        matiere = Matiere.from_model_dump(matiere_data)
        matiere_updated = repo.update(code_mp, matiere)
        if not matiere_updated:
            raise HTTPException(status_code=404, detail="Matière non trouvée")
        return matiere_updated.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la matière {code_mp}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/{code_mp}")
async def delete_matiere(code_mp: str) -> Dict[str, Any]:
    """
    Supprime une matière

    Args:
        code_mp: Code de la matière à supprimer

    Returns:
        Confirmation de suppression
    """
    try:
        repo = get_matieres_repo()
        success = repo.delete(code_mp)
        if not success:
            raise HTTPException(status_code=404, detail="Matière non trouvée")
        return {"message": "Matière supprimée avec succès", "code_mp": code_mp}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la matière {code_mp}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/search")
async def search_matieres(
    nom: str = Query(..., description="Nom de la matière à rechercher")
) -> Dict[str, Any]:
    """
    Recherche des matières par nom

    Args:
        nom: Nom de la matière à rechercher

    Returns:
        Liste des matières trouvées
    """
    try:
        repo = get_matieres_repo()
        matieres = repo.search_by_nom(nom)
        return {
            "recherche": nom,
            "total_matieres": len(matieres),
            "matieres": [matiere.model_dump() for matiere in matieres]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de matières: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/seveso")
async def get_matieres_seveso() -> Dict[str, Any]:
    """
    Récupère toutes les matières SEVESO

    Returns:
        Liste des matières SEVESO
    """
    try:
        repo = get_matieres_repo()
        matieres = repo.get_matieres_seveso()
        return {
            "total_matieres_seveso": len(matieres),
            "matieres": [matiere.model_dump() for matiere in matieres]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des matières SEVESO: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/type/{type_matiere}")
async def get_matieres_by_type(type_matiere: str) -> Dict[str, Any]:
    """
    Récupère les matières par type

    Args:
        type_matiere: Type de matière (acide/base/solvant/oxydant/sel)

    Returns:
        Liste des matières du type spécifié
    """
    try:
        repo = get_matieres_repo()
        matieres = repo.get_matieres_by_type(type_matiere)
        return {
            "type_matiere": type_matiere,
            "total_matieres": len(matieres),
            "matieres": [matiere.model_dump() for matiere in matieres]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des matières par type {type_matiere}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/{code_mp}/fds")
async def download_fds(code_mp: str) -> Dict[str, Any]:
    """
    Télécharge la FDS d'une matière

    Args:
        code_mp: Code de la matière première

    Returns:
        URL de téléchargement de la FDS
    """
    try:
        repo = get_matieres_repo()
        matiere = repo.get_by_code_mp(code_mp)
        if not matiere:
            raise HTTPException(status_code=404, detail="Matière non trouvée")

        # Simulation de l'URL de téléchargement FDS
        fds_url = f"https://fds.example.com/download/{code_mp}.pdf"

        return {
            "code_mp": code_mp,
            "nom_matiere": matiere.nom,
            "fds_url": fds_url,
            "date_generation": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de la FDS pour {code_mp}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
