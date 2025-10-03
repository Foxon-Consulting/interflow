"""
Endpoints pour la gestion des rapatriements
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from repositories.storage_strategies import JSONStorageStrategy
from repositories import RappatriementsRepository
from models.rappatriement import Rappatriement
from services.data_service import DataService

# Configuration du logging
logger = logging.getLogger(__name__)

# Création du router pour les rapatriements
router = APIRouter(prefix="/rappatriements", tags=["4. Rapatriements - CRUD"])



@router.get("/")
async def get_rappatriements(
    matiere_code: Optional[str] = Query(None, description="Code de la matière pour filtrer")
) -> Dict[str, Any]:
    """
    Récupère les rapatriements, éventuellement filtrés par matière

    Args:
        matiere_code: Code de la matière pour filtrer (optionnel)

    Returns:
        Liste des rapatriements
    """
    try:
        repo = DataService().rappatriements_repo
        if matiere_code:
            rappatriements = repo.get_rappatriements_by_matiere(matiere_code)
        else:
            rappatriements = repo.get_all()
        return {
            "total_rappatriements": len(rappatriements),
            "rappatriements": [rappatriement.model_dump() for rappatriement in rappatriements]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des rapatriements: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/")
async def delete_rappatriements() -> Dict[str, Any]:
    """
    Supprime tous les rapatriements (flush du repository)
    """
    try:
        repo = DataService().rappatriements_repo
        repo.flush()
        return {
            "message": "Tous les rapatriements ont été supprimés avec succès",
            "elements_supprimes": repo.count(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors du flush des rapatriements: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/{rappatriement_id}")
async def get_rappatriement_by_id(rappatriement_id: str) -> Dict[str, Any]:
    """
    Récupère un rapatriement spécifique par ID

    Args:
        rappatriement_id: ID du rapatriement à récupérer

    Returns:
        Données du rapatriement
    """
    try:
        repo = DataService().rappatriements_repo
        rappatriement = repo.get_by_id(rappatriement_id)
        if not rappatriement:
            raise HTTPException(status_code=404, detail="Rapatriement non trouvé")
        return rappatriement.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du rapatriement {rappatriement_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/")
async def create_rappatriement(rappatriement_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crée un nouveau rapatriement

    Args:
        rappatriement_data: Données du rapatriement à créer

    Returns:
        Rapatriement créé
    """
    try:
        repo = DataService().rappatriements_repo
        rappatriement = Rappatriement.from_model_dump(rappatriement_data)
        rappatriement_created = repo.create_rappatriement(rappatriement)
        return rappatriement_created.model_dump()
    except Exception as e:
        logger.error(f"Erreur lors de la création du rapatriement: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/{rappatriement_id}")
async def update_rappatriement(rappatriement_id: str, rappatriement_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Met à jour un rapatriement existant

    Args:
        rappatriement_id: ID du rapatriement à mettre à jour
        rappatriement_data: Nouvelles données du rapatriement

    Returns:
        Rapatriement mis à jour
    """
    try:
        repo = DataService().rappatriements_repo
        rappatriement = Rappatriement.from_model_dump(rappatriement_data)
        rappatriement_updated = repo.update(rappatriement_id, rappatriement)
        if not rappatriement_updated:
            raise HTTPException(status_code=404, detail="Rapatriement non trouvé")
        return rappatriement_updated.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du rapatriement {rappatriement_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/{rappatriement_id}")
async def delete_rappatriement(rappatriement_id: str) -> Dict[str, Any]:
    """
    Supprime un rapatriement

    Args:
        rappatriement_id: ID du rapatriement à supprimer

    Returns:
        Confirmation de suppression
    """
    try:
        repo = DataService().rappatriements_repo
        success = repo.delete(rappatriement_id)
        if not success:
            raise HTTPException(status_code=404, detail="Rapatriement non trouvé")
        return {"message": "Rapatriement supprimé avec succès", "rappatriement_id": rappatriement_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du rapatriement {rappatriement_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/import")
async def import_rappatriements(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Importe les rapatriements depuis un fichier CSV ou XLSX en flushing le repository

    Args:
        file: Fichier CSV ou XLSX à importer

    Returns:
        Résumé de l'import
    """
    try:
        # Vérifier que le fichier est bien un CSV ou XLSX
        if not file.filename.lower().endswith(('.csv', '.xlsx')):
            raise HTTPException(status_code=400, detail="Le fichier doit être un fichier CSV ou XLSX")

        # Sauvegarder temporairement le fichier
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Appeler le service pour l'import
            return DataService().import_rappatriements(file_path=temp_file_path, filename=file.filename)
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'import des rapatriements: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/append")
async def append_rappatriements(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Ajoute des rapatriements à partir d'un fichier CSV ou XLSX sans vider le repository existant

    Args:
        file: Fichier CSV ou XLSX à importer

    Returns:
        Résumé de l'ajout
    """
    try:
        # Vérifier que le fichier est bien un CSV ou XLSX
        if not file.filename.lower().endswith(('.csv', '.xlsx')):
            raise HTTPException(status_code=400, detail="Le fichier doit être un fichier CSV ou XLSX")

        # Sauvegarder temporairement le fichier
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Appeler le service pour l'ajout
            return DataService().append_rappatriements(file_path=temp_file_path, filename=file.filename)
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout des rapatriements: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
