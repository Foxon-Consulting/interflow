"""
Modèles Pydantic pour l'application Interflow Backend
"""

from .besoin import Besoin, Etat
from .stock import Stock
from .reception import Reception, EtatReception, TypeReception
from .rappatriement import Rappatriement, ProduitRappatriement, TypeEmballage
from .matieres import Matiere
from .analyse import AnalyseCouverture, AnalyseMatiere, CouvertureBesoin, AnalyseChronologique, EtapeChronologique, PremierBesoinNonCouvert, StatistiquesMatiere

__all__ = [
    # Modèles métier
    "Besoin",
    "Etat",
    "Stock",
    "Reception",
    "EtatReception",
    "TypeReception",
    "Rappatriement",
    "ProduitRappatriement",
    "TypeEmballage",
    "Matiere",
    "AnalyseCouverture",
    "AnalyseMatiere",
    "CouvertureBesoin",
    "AnalyseChronologique",
    "EtapeChronologique",
    "PremierBesoinNonCouvert",
    "StatistiquesMatiere"
]
