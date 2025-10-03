"""
Endpoints pour la gestion des besoins
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from repositories.storage_strategies import JSONStorageStrategy
from repositories import BesoinsRepository
from models.besoin import Besoin
from services.data_service import DataService

# Configuration du logging
logger = logging.getLogger(__name__)

# Création du router pour les besoins
router = APIRouter(prefix="/besoins", tags=["1. Besoins - CRUD"])

@router.get("/")
async def get_besoins(
    matiere_code: Optional[str] = Query(None, description="Code de la matière pour filtrer")
) -> Dict[str, Any]:
    """
    Récupère la liste des besoins

    Args:
        matiere_code: Code de matière pour filtrer (optionnel)

    Returns:
        Liste des besoins
    """
    try:
        repo = DataService().besoins_repo
        if matiere_code:
            besoins = repo.filter_besoins_advanced(code_mp=matiere_code)
        else:
            besoins = repo.get_all()
        return {
            "total_besoins": len(besoins),
            "besoins": [besoin.model_dump() for besoin in besoins]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des besoins: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/")
async def delete_besoins() -> Dict[str, Any]:
    """
    Supprime tous les besoins (flush du repository)
    """
    try:
        repo = DataService().besoins_repo
        repo.flush()
        return {
            "message": "Tous les besoins ont été supprimés avec succès",
            "elements_supprimes": repo.count(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors du flush des besoins: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/{besoin_id}")
async def get_besoin_by_id(besoin_id: str) -> Dict[str, Any]:
    """
    Récupère un besoin spécifique par ID

    Args:
        besoin_id: ID du besoin à récupérer

    Returns:
        Données du besoin
    """
    try:
        repo = DataService().besoins_repo
        besoin = repo.get_by_id(besoin_id)
        if not besoin:
            raise HTTPException(status_code=404, detail="Besoin non trouvé")
        return besoin.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du besoin {besoin_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/")
async def create_besoin(besoin_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crée un nouveau besoin

    Args:
        besoin_data: Données du besoin à créer

    Returns:
        Besoin créé
    """
    try:
        repo = DataService().besoins_repo
        besoin = Besoin.from_model_dump(besoin_data)
        besoin_created = repo.create(besoin)
        return besoin_created.model_dump()
    except Exception as e:
        logger.error(f"Erreur lors de la création du besoin: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/{besoin_id}")
async def update_besoin(besoin_id: str, besoin_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Met à jour un besoin existant

    Args:
        besoin_id: ID du besoin à mettre à jour
        besoin_data: Nouvelles données du besoin

    Returns:
        Besoin mis à jour
    """
    try:
        repo = DataService().besoins_repo
        besoin = Besoin.from_model_dump(besoin_data)
        besoin_updated = repo.update(besoin_id, besoin)
        if not besoin_updated:
            raise HTTPException(status_code=404, detail="Besoin non trouvé")
        return besoin_updated.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du besoin {besoin_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/{besoin_id}")
async def delete_besoin(besoin_id: str) -> Dict[str, Any]:
    """
    Supprime un besoin

    Args:
        besoin_id: ID du besoin à supprimer

    Returns:
        Confirmation de suppression
    """
    try:
        repo = DataService().besoins_repo
        success = repo.delete(besoin_id)
        if not success:
            raise HTTPException(status_code=404, detail="Besoin non trouvé")
        return {"message": "Besoin supprimé avec succès", "besoin_id": besoin_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du besoin {besoin_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/import")
async def import_besoins(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Importe les besoins depuis un fichier CSV ou XLSX en flushing le repository

    Args:
        file: Fichier XLSX à importer

    Returns:
        Résumé de l'import
    """
    try:
        # Vérifier que le fichier est bien un CSV ou XLSX
        if not file.filename.lower().endswith(('.xlsx')):
            raise HTTPException(status_code=400, detail="Le fichier doit être un fichier XLSX")

        # Sauvegarder temporairement le fichier
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Appeler le service pour l'import
            return DataService().import_besoins(file_path=temp_file_path, filename=file.filename)
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'import des besoins: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/import_from_s3")
async def import_besoins_from_s3() -> Dict[str, Any]:
    """
    Importe les besoins depuis un fichier XLSX d'un bucket S3 et flush d'abord le repository
    """
    try:
        return DataService().import_besoins_from_s3()
    except Exception as e:
        logger.error(f"Erreur lors de l'import des besoins: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
