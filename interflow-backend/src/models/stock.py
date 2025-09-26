from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Iterator, Union
from datetime import datetime
from models.matieres import Matiere

class Stock(BaseModel):
    id: Optional[str] = Field(None, description="Identifiant unique du stock (généré automatiquement)")
    article: str = Field(..., description="Code de l'article")
    libelle_article: str = Field(..., description="Libellé de l'article")
    du: Optional[str] = Field(None, description="Date d'utilisation")
    quantite: float = Field(..., description="Quantité disponible", ge=0)
    udm: str = Field(..., description="Unité de mesure")
    statut_lot: str = Field(..., description="Statut du lot")
    division: str = Field(..., description="Division")
    magasin: str = Field(..., description="Code du magasin")
    emplacement: str = Field(..., description="Emplacement dans le magasin")
    contenant: str = Field(..., description="Contenant")
    statut_proprete: str = Field(..., description="Statut de propreté")
    reutilisable: str = Field(..., description="Réutilisable ou non")
    statut_contenant: str = Field(..., description="Statut du contenant")
    classification: Optional[str] = Field(None, description="Classification")
    restriction: Optional[str] = Field(None, description="Restrictions")
    lot_fournisseur: Optional[str] = Field(None, description="Lot fournisseur")
    capacite: Optional[float] = Field(None, description="Capacité")
    commentaire: Optional[str] = Field(None, description="Commentaire")
    date_creation: Optional[datetime] = Field(None, description="Date de création")
    dluo: Optional[datetime] = Field(None, description="Date limite d'utilisation optimale")
    matiere: Matiere | None = Field(None, description="Matière associée")

    @field_validator('division', mode='before')
    @classmethod
    def normalize_division(cls, v):
        """Normalise les codes division (supprime les zéros de début)"""
        if not v:
            return ""
        value_str = str(v).strip()
        if value_str.isdigit() and len(value_str) > 1:
            normalized = str(int(value_str))
            if len(normalized) <= 4:  # Codes division max 4 chiffres
                return normalized
        return value_str

    @field_validator('lot_fournisseur', mode='before')
    @classmethod
    def normalize_lot_fournisseur(cls, v):
        """Normalise les lots fournisseur (supprime .0 des entiers)"""
        if not v:
            return None
        value_str = str(v).strip()
        # Supprimer .0 si c'est un entier
        if value_str.endswith('.0') and value_str.replace('.0', '').isdigit():
            return value_str.replace('.0', '')
        return value_str

    @field_validator('capacite', 'quantite', mode='before')
    @classmethod
    def normalize_numeric_values(cls, v):
        """Normalise les valeurs numériques (convertit les virgules en points)"""
        if v is None:
            return None if 'capacite' in cls.__name__ else 0.0

        # Si c'est déjà un nombre, le garder
        if isinstance(v, (int, float)):
            return float(v)

        value_str = str(v).strip()

        # Convertir les virgules en points
        if ',' in value_str:
            # Gérer les cas spéciaux comme "500," -> "500.0"
            if value_str.endswith(','):
                value_str = value_str[:-1] + '.0'
            else:
                value_str = value_str.replace(',', '.')

        try:
            return float(value_str)
        except ValueError:
            return None if 'capacite' in cls.__name__ else 0.0

    @field_validator('restriction', 'classification', 'commentaire', 'du', mode='before')
    @classmethod
    def clean_string_fields(cls, v):
        """Nettoie les champs string pour gérer les valeurs NaN"""
        if v is None:
            return None

        # Si c'est déjà une string valide, la garder
        if isinstance(v, str):
            value_str = v.strip()
            if value_str.lower() in ['nan', 'none', 'null', '']:
                return None
            return value_str

        # Si c'est un float NaN, retourner None
        if isinstance(v, float) and str(v).lower() == 'nan':
            return None

        # Convertir en string et nettoyer
        value_str = str(v).strip()
        if value_str.lower() in ['nan', 'none', 'null', '']:
            return None

        return value_str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # La matière sera initialisée par le repository si nécessaire
        if not self.matiere:
            # Créer une matière temporaire avec le libellé
            self.matiere = Matiere(code_mp="TOBEDEFINED", nom=self.libelle_article)
        # Générer une clé primaire composite basée sur le tuple unique
        self.id = f"{self.article}_{self.magasin}_{self.emplacement}_{self.contenant}"

    @classmethod
    def from_model_dump(cls, data: dict):
        return cls(**data)
