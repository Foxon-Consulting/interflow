"""
Endpoints pour la gestion des réceptions
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from repositories.storage_strategies import JSONStorageStrategy
from repositories import ReceptionsRepository
from models.reception import Reception, TypeReception, EtatReception
from services.data_service import DataService

# Configuration du logging
logger = logging.getLogger(__name__)

# Création du router pour les réceptions
router = APIRouter(prefix="/receptions", tags=["2. Réceptions - CRUD"])

# Factory functions
def get_storage_strategy():
    """Factory pour créer une instance de JSONStorageStrategy"""
    return JSONStorageStrategy()

def get_receptions_repo() -> ReceptionsRepository:
    """Factory pour créer une instance de ReceptionsRepository"""
    return ReceptionsRepository(get_storage_strategy())

def get_data_service() -> DataService:
    """Factory pour créer une instance de DataService"""
    return DataService()

@router.get("/")
async def get_receptions(
    matiere_code: Optional[str] = Query(None, description="Code de la matière pour filtrer")
) -> Dict[str, Any]:
    """
    Récupère les réceptions, éventuellement filtrées par matière

    Args:
        matiere_code: Code de la matière pour filtrer (optionnel)

    Returns:
        Liste des réceptions
    """
    try:
        repo = get_receptions_repo()
        if matiere_code:
            receptions = repo.get_receptions_by_matiere(matiere_code)
        else:
            receptions = repo.get_all()
        return {
            "total_receptions": len(receptions),
            "receptions": [reception.model_dump() for reception in receptions]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des réceptions: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/")
async def delete_receptions() -> Dict[str, Any]:
    """
    Supprime tous les réceptions (flush du repository)
    """
    try:
        repo = get_receptions_repo()
        repo.flush()
        return {
            "message": "Tous les réceptions ont été supprimés avec succès",
            "elements_supprimes": repo.count(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors du flush des réceptions: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/{reception_id}")
async def get_reception_by_id(reception_id: str) -> Dict[str, Any]:
    """
    Récupère une réception spécifique par ID

    Args:
        reception_id: ID de la réception à récupérer

    Returns:
        Données de la réception
    """
    try:
        repo = get_receptions_repo()
        reception = repo.get_by_id(reception_id)
        if not reception:
            raise HTTPException(status_code=404, detail="Réception non trouvée")
        return reception.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la réception {reception_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/")
async def create_reception(reception_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crée une nouvelle réception

    Args:
        reception_data: Données de la réception à créer

    Returns:
        Réception créée
    """
    try:
        repo = get_receptions_repo()
        reception = Reception.from_model_dump(reception_data)
        reception_created = repo.create(reception)
        return reception_created.model_dump()
    except Exception as e:
        logger.error(f"Erreur lors de la création de la réception: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/{reception_id}")
async def update_reception(reception_id: str, reception_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Met à jour une réception existante

    Args:
        reception_id: ID de la réception à mettre à jour
        reception_data: Nouvelles données de la réception

    Returns:
        Réception mise à jour
    """
    try:
        repo = get_receptions_repo()
        reception = Reception.from_model_dump(reception_data)
        reception_updated = repo.update(reception_id, reception)
        if not reception_updated:
            raise HTTPException(status_code=404, detail="Réception non trouvée")
        return reception_updated.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la réception {reception_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/{reception_id}")
async def delete_reception(reception_id: str) -> Dict[str, Any]:
    """
    Supprime une réception

    Args:
        reception_id: ID de la réception à supprimer

    Returns:
        Confirmation de suppression
    """
    try:
        repo = get_receptions_repo()
        success = repo.delete(reception_id)
        if not success:
            raise HTTPException(status_code=404, detail="Réception non trouvée")
        return {"message": "Réception supprimée avec succès", "reception_id": reception_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la réception {reception_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/type/{type_reception}")
async def get_receptions_by_type(type_reception: str) -> Dict[str, Any]:
    """
    Récupère les réceptions par type

    Args:
        type_reception: Type de réception (PRESTATAIRE/INTERNE)

    Returns:
        Liste des réceptions du type spécifié
    """
    try:
        repo = get_receptions_repo()
        type_enum = TypeReception(type_reception.upper())
        receptions = repo.get_receptions_by_type(type_enum)
        return {
            "type": type_reception,
            "total_receptions": len(receptions),
            "receptions": [reception.model_dump() for reception in receptions]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des réceptions par type {type_reception}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/etat/{etat}")
async def get_receptions_by_etat(etat: str) -> Dict[str, Any]:
    """
    Récupère les réceptions par état

    Args:
        etat: État de la réception (EN_COURS/TERMINEE/ANNULEE/etc.)

    Returns:
        Liste des réceptions dans l'état spécifié
    """
    try:
        repo = get_receptions_repo()
        etat_enum = EtatReception(etat.upper())
        receptions = repo.get_receptions_by_etat(etat_enum)
        return {
            "etat": etat,
            "total_receptions": len(receptions),
            "receptions": [reception.model_dump() for reception in receptions]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des réceptions par état {etat}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/matiere/{code_mp}")
async def get_receptions_by_matiere(code_mp: str) -> Dict[str, Any]:
    """
    Récupère les réceptions pour une matière spécifique

    Args:
        code_mp: Code de la matière première

    Returns:
        Liste des réceptions pour cette matière
    """
    try:
        repo = get_receptions_repo()
        receptions = repo.get_receptions_by_matiere(code_mp)
        return {
            "matiere_code": code_mp,
            "total_receptions": len(receptions),
            "receptions": [reception.model_dump() for reception in receptions]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des réceptions pour la matière {code_mp}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/bon-reception")
async def generer_bon_reception(reception_ids: List[str]) -> Dict[str, Any]:
    """
    Génère un bon de réception pour les réceptions spécifiées

    Args:
        reception_ids: Liste des IDs de réceptions pour le bon

    Returns:
        Bon de réception généré
    """
    try:
        repo = get_receptions_repo()
        # Récupérer les réceptions
        receptions = []
        for reception_id in reception_ids:
            reception = repo.get_by_id(reception_id)
            if reception:
                receptions.append(reception)

        if not receptions:
            raise HTTPException(status_code=400, detail="Aucune réception valide trouvée")

        # Générer le bon de réception
        bon_reception = {
            "id": f"BR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "date_generation": datetime.now().isoformat(),
            "nombre_receptions": len(receptions),
            "receptions": [
                {
                    "id": reception.id,
                    "matiere_code": reception.matiere.code_mp,
                    "matiere_nom": reception.matiere.nom,
                    "quantite": reception.quantite,
                    "fournisseur": reception.fournisseur
                }
                for reception in receptions
            ],
            "total_montant_estime": sum(reception.quantite * 100 for reception in receptions)  # Estimation simpliste
        }
        return bon_reception
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la génération du bon de réception: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/import")
async def import_receptions(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Importe les réceptions depuis un fichier CSV ou XLSX en flushing le repository

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
            data_service = get_data_service()
            return data_service.import_receptions(file_path=temp_file_path, filename=file.filename)
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'import des réceptions: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
