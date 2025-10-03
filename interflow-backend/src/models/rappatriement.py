from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional


class ProduitRappatriement(BaseModel):
    """
    Modèle pour un produit dans un rapatriement
    """
    prelevement: bool = Field(False, description="Pour prélèvement")
    code_prdt: str = Field(..., description="Code du produit")
    designation_prdt: str = Field(..., description="Désignation du produit")
    lot: str = Field(..., description="Numéro de lot")
    poids_net: float = Field(..., description="Poids net", ge=0)
    type_emballage: str = Field(..., description="Type d'emballage")
    stock_solde: bool = Field(False, description="Stock soldé")
    nb_contenants: int = Field(..., description="Nombre de contenants", ge=0)
    nb_palettes: int = Field(..., description="Nombre de palettes", ge=0)
    dimension_palettes: str = Field(..., description="Dimensions des palettes")
    code_onu: str = Field(..., description="Code ONU")
    grp_emballage: str = Field(..., description="Groupe d'emballage")
    po: Optional[str] = Field(None, description="Numéro de commande")

    @field_validator('poids_net', 'nb_contenants', 'nb_palettes', mode='before')
    @classmethod
    def normalize_numeric_values(cls, v):
        """Normalise les valeurs numériques (convertit les virgules en points)"""
        if v is None:
            return 0.0 if 'poids_net' in cls.__name__ else 0

        # Si c'est déjà un nombre, le garder
        if isinstance(v, (int, float)):
            return float(v) if 'poids_net' in cls.__name__ else int(v)

        value_str = str(v).strip()

        # Convertir les virgules en points
        if ',' in value_str:
            # Gérer les cas spéciaux comme "500," -> "500.0"
            if value_str.endswith(','):
                value_str = value_str[:-1] + '.0'
            else:
                value_str = value_str.replace(',', '.')

        try:
            return float(value_str) if 'poids_net' in cls.__name__ else int(float(value_str))
        except ValueError:
            return 0.0 if 'poids_net' in cls.__name__ else 0

    @field_validator('prelevement', mode='before')
    @classmethod
    def normalize_prelevement(cls, v):
        """Normalise le champ prelevement en booléen"""
        if v is None:
            return False

        # Si c'est déjà un booléen, le garder
        if isinstance(v, bool):
            return v

        # Si c'est une string, vérifier si c'est "Pour Prlvm"
        if isinstance(v, str):
            value_str = v.strip()
            if value_str.lower() in ['nan', 'none', 'null', '']:
                return False
            return value_str.lower() == 'pour prlvm'

        # Si c'est un float NaN, retourner False
        if isinstance(v, float) and str(v).lower() == 'nan':
            return False

        # Convertir en string et vérifier
        value_str = str(v).strip()
        if value_str.lower() in ['nan', 'none', 'null', '']:
            return False

        return value_str.lower() == 'pour prlvm'

    @field_validator('code_prdt', 'designation_prdt', 'lot', 'dimension_palettes',
                    'code_onu', 'grp_emballage', 'po', mode='before')
    @classmethod
    def clean_string_fields(cls, v):
        """Nettoie les champs string pour gérer les valeurs NaN"""
        if v is None:
            return "" if 'po' not in cls.__name__ else None

        # Si c'est déjà une string valide, la garder
        if isinstance(v, str):
            value_str = v.strip()
            if value_str.lower() in ['nan', 'none', 'null', '']:
                return "" if 'po' not in cls.__name__ else None
            return value_str

        # Si c'est un float NaN, retourner valeur par défaut
        if isinstance(v, float) and str(v).lower() == 'nan':
            return "" if 'po' not in cls.__name__ else None

        # Convertir en string et nettoyer
        value_str = str(v).strip()
        if value_str.lower() in ['nan', 'none', 'null', '']:
            return "" if 'po' not in cls.__name__ else None

        return value_str

    @field_validator('type_emballage', mode='before')
    @classmethod
    def normalize_type_emballage(cls, v):
        """Normalise le type d'emballage"""
        if v is None:
            return ""

        # Si c'est déjà une string valide, la nettoyer
        if isinstance(v, str):
            value_str = v.strip()
            if value_str.lower() in ['nan', 'none', 'null', '']:
                return ""
            return value_str

        # Si c'est un float NaN, retourner vide
        if isinstance(v, float) and str(v).lower() == 'nan':
            return ""

        # Convertir en string et nettoyer
        value_str = str(v).strip()
        if value_str.lower() in ['nan', 'none', 'null', '']:
            return ""

        return value_str

    @field_validator('stock_solde', mode='before')
    @classmethod
    def normalize_bool(cls, v):
        """Normalise les valeurs booléennes"""
        if v is None:
            return False

        if isinstance(v, bool):
            return v

        if isinstance(v, str):
            value_lower = v.lower().strip()
            return value_lower in ['oui', 'yes', 'true', '1', 'x']

        if isinstance(v, (int, float)):
            return bool(v)

        return False


class Rappatriement(BaseModel):
    """
    Modèle pour un rapatriement
    """
    numero_transfert: Optional[str] = Field(None, description="Numéro de transfert")
    date_derniere_maj: Optional[datetime] = Field(None, description="Date de dernière mise à jour")
    responsable_diffusion: str = Field(..., description="Responsable de la diffusion")
    date_demande: Optional[datetime] = Field(None, description="Date de demande")
    date_reception_souhaitee: Optional[datetime] = Field(None, description="Date de réception souhaitée")
    contacts: str = Field(..., description="Contacts")
    adresse_destinataire: str = Field(..., description="Adresse du destinataire")
    adresse_enlevement: str = Field(..., description="Adresse d'enlèvement")
    produits: List[ProduitRappatriement] = Field(default_factory=list, description="Liste des produits")
    remarques: Optional[str] = Field(None, description="Remarques")

    @field_validator('numero_transfert', 'responsable_diffusion', 'contacts', 'adresse_destinataire',
                    'adresse_enlevement', 'remarques', mode='before')
    @classmethod
    def clean_string_fields(cls, v):
        """Nettoie les champs string pour gérer les valeurs NaN"""
        if v is None:
            return "" if 'remarques' not in cls.__name__ else None

        # Si c'est déjà une string valide, la garder
        if isinstance(v, str):
            value_str = v.strip()
            if value_str.lower() in ['nan', 'none', 'null', '']:
                return "" if 'remarques' not in cls.__name__ else None
            return value_str

        # Si c'est un float NaN, retourner valeur par défaut
        if isinstance(v, float) and str(v).lower() == 'nan':
            return "" if 'remarques' not in cls.__name__ else None

        # Convertir en string et nettoyer
        value_str = str(v).strip()
        if value_str.lower() in ['nan', 'none', 'null', '']:
            return "" if 'remarques' not in cls.__name__ else None

        return value_str

    def ajouter_produit(self, produit: ProduitRappatriement):
        """
        Ajoute un produit au rapatriement
        """
        self.produits.append(produit)

    def calculer_poids_total(self) -> float:
        """
        Calcule le poids total de tous les produits
        """
        return sum(produit.poids_net for produit in self.produits)

    def calculer_nb_palettes_total(self) -> int:
        """
        Calcule le nombre total de palettes
        """
        return sum(produit.nb_palettes for produit in self.produits)

    def calculer_nb_contenants_total(self) -> int:
        """
        Calcule le nombre total de contenants
        """
        return sum(produit.nb_contenants for produit in self.produits)

    def model_dump(self) -> dict:
        """
        Sérialise le modèle en dictionnaire
        """
        data = super().model_dump()

        # Convertir les dates en strings si elles existent
        if self.date_derniere_maj:
            data['date_derniere_maj'] = self.date_derniere_maj.isoformat()
        if self.date_demande:
            data['date_demande'] = self.date_demande.isoformat()
        if self.date_reception_souhaitee:
            data['date_reception_souhaitee'] = self.date_reception_souhaitee.isoformat()

        return data

    @classmethod
    def from_model_dump(cls, data: dict) -> 'Rappatriement':
        """
        Désérialise un dictionnaire en modèle
        """
        # Convertir les dates si elles existent en s'assurant qu'elles sont naive
        if data.get('date_derniere_maj'):
            date_derniere_maj = datetime.fromisoformat(data['date_derniere_maj'])
            if date_derniere_maj.tzinfo is not None:
                date_derniere_maj = date_derniere_maj.replace(tzinfo=None)
            data['date_derniere_maj'] = date_derniere_maj
        if data.get('date_demande'):
            date_demande = datetime.fromisoformat(data['date_demande'])
            if date_demande.tzinfo is not None:
                date_demande = date_demande.replace(tzinfo=None)
            data['date_demande'] = date_demande
        if data.get('date_reception_souhaitee'):
            date_reception_souhaitee = datetime.fromisoformat(data['date_reception_souhaitee'])
            if date_reception_souhaitee.tzinfo is not None:
                date_reception_souhaitee = date_reception_souhaitee.replace(tzinfo=None)
            data['date_reception_souhaitee'] = date_reception_souhaitee

        # Convertir les produits
        if data.get('produits'):
            produits = []
            for produit_data in data['produits']:
                produits.append(ProduitRappatriement(**produit_data))
            data['produits'] = produits

        return cls(**data)
