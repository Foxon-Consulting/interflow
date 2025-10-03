"""
API Interflow Backend

This module provides a FastAPI API for the Interflow backend system,
including coverage analysis, data management, and business services.
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Import des services directs (remplace les entrypoints)
from services.analyse_service import AnalyseService
from services.analyse_display_service import AnalyseDisplayService
from services.data_service import DataService

from repositories.storage_strategies import JSONStorageStrategy
from repositories import (
    ReceptionsRepository,
    RappatriementsRepository,
    MatieresPremieresRepository
)

# Import des routers modulaires
from .stock import router as stock_router
from .besoins import router as besoins_router
from .receptions import router as receptions_router
from .rappatriements import router as rapatriements_router
from .matieres import router as matieres_router
from .analyse import router as analyse_router

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Interflow Backend API",
    description="API pour la gestion des besoins, stocks, commandes et analyses de couverture",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers modulaires
app.include_router(stock_router)
app.include_router(besoins_router)
app.include_router(receptions_router)
app.include_router(rapatriements_router)
app.include_router(matieres_router)
app.include_router(analyse_router)
# app.include_router(calendrier_router)

# Initialisation des repositories et services
def get_storage_strategy():
    """Factory pour créer une instance de JSONStorageStrategy"""
    return JSONStorageStrategy()

# === ENDPOINTS DE BASE ===

@app.get("/", tags=["0. API - Informations"])
async def root():
    """
    Endpoint racine - Point d'entrée informatif de l'API

    Returns:
        Informations générales sur l'API et ses endpoints principaux
    """
    return {
        "service": "Interflow Backend API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "description": "API pour la gestion des besoins, stocks, commandes et analyses de couverture",
        "endpoints": {
            "health": "/health",
            "documentation": "/docs",
            "analyse": "/analyse",
            "data_summary": "/data/summary",
            "available_materials": "/analyse/matieres",
            "analyze_besoins": "/analyse/besoins"
        },
        "resources": {
            "besoins": {
                "list": "/besoins",
                "by_id": "/besoins/{id}",
                "create": "POST /besoins",
                "update": "PUT /besoins/{id}",
                "delete": "DELETE /besoins/{id}",
                "current": "/besoins/actuels"
            },
            "stocks": {
                "list": "/stocks",
                "by_id": "/stocks/{id}",
                "create": "POST /stocks",
                "update": "PUT /stocks/{id}",
                "delete": "DELETE /stocks/{id}"
            },
            "commandes": {
                "list": "/commandes",
                "by_id": "/commandes/{id}",
                "create": "POST /commandes",
                "update": "PUT /commandes/{id}",
                "delete": "DELETE /commandes/{id}",
                "by_type": "/commandes/type/{type}",
                "by_etat": "/commandes/etat/{etat}",
                "by_matiere": "/commandes/matiere/{code_mp}",
                "en_cours": "/commandes/en-cours",
                "bon_commande": "POST /commandes/bon-commande"
            },
            "rappatriements": {
                "list": "/rappatriements",
                "by_id": "/rappatriements/{id}",
                "create": "POST /rappatriements",
                "update": "PUT /rappatriements/{id}",
                "delete": "DELETE /rappatriements/{id}",
                "en_cours": "/rappatriements/en-cours"
            },
            "matieres": {
                "list": "/matieres",
                "by_code": "/matieres/{code_mp}",
                "create": "POST /matieres",
                "update": "PUT /matieres/{code_mp}",
                "delete": "DELETE /matieres/{code_mp}",
                "search": "/matieres/search?nom={nom}",
                "seveso": "/matieres/seveso",
                "by_type": "/matieres/type/{type}",
                "fds": "/matieres/{code_mp}/fds"
            },
            "calendrier": {
                "events": "/calendrier/events",
                "events_by_date": "/calendrier/events/{date}",
                "event_by_id": "/calendrier/events/{event_id}"
            }
        }
    }

@app.get("/health", tags=["0. API - Informations"])
async def health():
    """Endpoint de santé du service"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# === ENDPOINTS DATA ===

@app.get("/data/summary", tags=["8. Données - Résumé"])
async def get_data_summary() -> Dict[str, Any]:
    """
    Récupère un résumé des données du système

    Returns:
        Statistiques générales du système
    """
    try:
        from repositories import BesoinsRepository, ReceptionsRepository, RappatriementsRepository, MatieresPremieresRepository

        storage_strategy = get_storage_strategy()
        besoins_repo = BesoinsRepository(storage_strategy)
        receptions_repo = ReceptionsRepository(storage_strategy)
        rappatriements_repo = RappatriementsRepository(storage_strategy)
        matieres_repo = MatieresPremieresRepository(storage_strategy)

        besoins = besoins_repo.get_all()
        receptions = receptions_repo.get_all()
        rappatriements = rappatriements_repo.get_all()
        matieres = matieres_repo.get_all()

        return {
            "timestamp": datetime.now().isoformat(),
            "totaux": {
                "besoins": len(besoins),
                "receptions": len(receptions),
                "rappatriements": len(rappatriements),
                "matieres": len(matieres)
            },
            "receptions_par_etat": {
                "en_cours": len([r for r in receptions if r.etat.value == "en_cours"]),
                "terminées": len([r for r in receptions if r.etat.value == "terminée"]),
                "annulées": len([r for r in receptions if r.etat.value == "annulée"])
            },
            "besoins_urgents": len([b for b in besoins if (b.echeance - datetime.now()).days < 7])
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du résumé: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# === GESTION DES ERREURS ===

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Gestionnaire d'exceptions HTTP personnalisé"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Gestionnaire d'exceptions générales"""
    logger.error(f"Erreur non gérée: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Erreur interne du serveur",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
