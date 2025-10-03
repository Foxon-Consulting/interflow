"""
Endpoints pour la gestion des stocks
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from models.stock import Stock
from services.data_service import DataService

# Configuration du logging
logger = logging.getLogger(__name__)

# Création du router pour les stocks
router = APIRouter(prefix="/stocks", tags=["3. Stocks - CRUD"])


@router.get("/")
async def get_stocks(
    matiere_code: Optional[str] = Query(None, description="Code de la matière pour filtrer"),
    stock_type: Optional[str] = Query(None, description="Type de stock (interne/externe)")
) -> Dict[str, Any]:
    """
    Récupère les stocks, éventuellement filtrés par matière et type

    Args:
        matiere_code: Code de la matière pour filtrer (optionnel)
        stock_type: Type de stock ('interne' ou 'externe') (optionnel)

    Returns:
        Liste des stocks
    """
    try:
        stocks = DataService().get_stocks(matiere_code=matiere_code, stock_type=stock_type)
        
        return {
            "total_stocks": len(stocks),
            "stocks": [stock.model_dump() for stock in stocks]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stocks: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/internal")
async def get_internal_stocks(
    matiere_code: Optional[str] = Query(None, description="Code de la matière pour filtrer")
) -> Dict[str, Any]:
    """
    Récupère uniquement les stocks internes (magasins ne commençant pas par "EX")

    Args:
        matiere_code: Code de la matière pour filtrer (optionnel)

    Returns:
        Liste des stocks internes
    """
    try:
        if matiere_code:
            stocks = DataService().stocks_repo.get_internal_stocks_by_matiere(matiere_code)
        else:
            stocks = DataService().stocks_repo.get_internal_stocks()
        return {
            "total_stocks_internes": len(stocks),
            "stocks": [stock.model_dump() for stock in stocks]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stocks internes: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/external")
async def get_external_stocks(
    matiere_code: Optional[str] = Query(None, description="Code de la matière pour filtrer")
) -> Dict[str, Any]:
    """
    Récupère uniquement les stocks externes (magasins commençant par "EX")

    Args:
        matiere_code: Code de la matière pour filtrer (optionnel)

    Returns:
        Liste des stocks externes
    """
    try:
        if matiere_code:
            stocks = DataService().stocks_repo.get_external_stocks_by_matiere(matiere_code)
        else:
            stocks = DataService().stocks_repo.get_external_stocks()
        return {
            "total_stocks_externes": len(stocks),
            "stocks": [stock.model_dump() for stock in stocks]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stocks externes: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/")
async def delete_stocks() -> Dict[str, Any]:
    """
    Supprime tous les stocks (flush du repository)
    """
    try:
        service = DataService()
        service.stocks_repo.flush()
        return {
            "message": "Tous les stocks ont été supprimés avec succès",
            "elements_supprimes": service.stocks_repo.count(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors du flush des stocks: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/{stock_id}")
async def get_stock_by_id(stock_id: str) -> Dict[str, Any]:
    """
    Récupère un stock spécifique par ID

    Args:
        stock_id: ID du stock à récupérer

    Returns:
        Données du stock    
    """
    try:
        stock = DataService().stocks_repo.get_by_id(stock_id)
        if not stock:
            raise HTTPException(status_code=404, detail="Stock non trouvé")
        return stock.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du stock {stock_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/")
async def create_stock(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crée un nouveau stock

    Args:
        stock_data: Données du stock à créer

    Returns:
        Stock créé
    """
    try:
        stock = Stock.from_model_dump(stock_data)
        stock_created = DataService().stocks_repo.create(stock)
        return stock_created.model_dump()
    except Exception as e:
        logger.error(f"Erreur lors de la création du stock: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/{stock_id}")
async def update_stock(stock_id: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Met à jour un stock existant

    Args:
        stock_id: ID du stock à mettre à jour
        stock_data: Nouvelles données du stock

    Returns:
        Stock mis à jour
    """
    try:
        stock = Stock.from_model_dump(stock_data)
        stock_updated = DataService().stocks_repo.update(stock_id, stock)
        if not stock_updated:
            raise HTTPException(status_code=404, detail="Stock non trouvé")
        return stock_updated.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du stock {stock_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/{stock_id}")
async def delete_stock(stock_id: str) -> Dict[str, Any]:
    """
    Supprime un stock

    Args:
        stock_id: ID du stock à supprimer

    Returns:
        Confirmation de suppression
    """
    try:
        success = DataService().stocks_repo.delete(stock_id)
        if not success:
            raise HTTPException(status_code=404, detail="Stock non trouvé")
        return {"message": "Stock supprimé avec succès", "stock_id": stock_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du stock {stock_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/import")
async def import_stocks(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Importe les stocks depuis un fichier CSV ou XLSX en flushing le repository

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
            return DataService().import_stocks(file_path=temp_file_path, filename=file.filename)
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'import des stocks: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/import_from_s3")
async def import_stocks_from_s3() -> Dict[str, Any]:
    """
    Importe les stocks depuis un fichier XLSX d'un bucket S3 et flush d'abord le repository
    """
    try:
        data_service = DataService()
        return data_service.import_stocks_from_s3()
    except Exception as e:
        logger.error(f"Erreur lors de l'import des stocks: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
    