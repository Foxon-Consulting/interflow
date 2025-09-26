from pydantic import BaseModel, Field, field_validator
from models.matieres import Matiere
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Iterator


class EtatReception(Enum):
    EN_COURS = "en_cours"
    TERMINEE = "terminée"
    ANNULEE = "annulée"
    RELACHE = "relâché"
    EN_ATTENTE = "en_attente"

class TypeReception(Enum):
    PRESTATAIRE = "prestataire"
    INTERNE = "interne"

class Reception(BaseModel):
    id: Optional[str] = Field(None, description="Identifiant unique de la réception (généré automatiquement)")
    type: TypeReception = Field(TypeReception.PRESTATAIRE, description="Type de réception")
    matiere: Matiere = Field(..., description="Matière réceptionnée")
    quantite: float = Field(..., description="Quantité réceptionnée", ge=0)
    lot: Optional[str] = Field("", description="Numéro de lot")
    qualification: bool = Field(False, description="Qualification requise")
    date_creation: datetime = Field(..., description="Date de création de la réception")
    date_modification: Optional[datetime] = Field(None, description="Date de dernière modification")

    # Champs spécifiques aux réceptions internes
    ordre: Optional[str] = Field(None, description="Numéro d'ordre")
    type_ordre: Optional[str] = Field(None, description="Type d'ordre")
    statut_ordre: Optional[str] = Field(None, description="Statut de l'ordre")
    poste: Optional[str] = Field(None, description="Poste de travail")
    statut_poste: Optional[str] = Field(None, description="Statut du poste")
    division: Optional[str] = Field(None, description="Division")
    magasin: Optional[str] = Field(None, description="Magasin")
    article: Optional[str] = Field(None, description="Code article")
    libelle_article: Optional[str] = Field(None, description="Libellé de l'article")
    ref_externe: Optional[str] = Field(None, description="Référence externe")
    description_externe: Optional[str] = Field(None, description="Description externe")
    quantite_ordre: Optional[float] = Field(None, description="Quantité de l'ordre")
    quantite_receptionnee: Optional[float] = Field(None, description="Quantité réceptionnée")
    udm: Optional[str] = Field(None, description="Unité de mesure")
    fournisseur: Optional[str] = Field(None, description="Fournisseur")
    description_fournisseur: Optional[str] = Field(None, description="Description du fournisseur")
    date_reception: Optional[datetime] = Field(None, description="Date de réception")

    # État unifié (pour compatibilité)
    etat: EtatReception = Field(EtatReception.EN_COURS, description="État de la réception")

    @field_validator('quantite_ordre', 'quantite_receptionnee', 'quantite', mode='before')
    @classmethod
    def normalize_numeric_values(cls, v):
        """Normalise les valeurs numériques (convertit les virgules en points)"""
        if v is None:
            return None if 'quantite_ordre' in cls.__name__ or 'quantite_receptionnee' in cls.__name__ else 0.0

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
            return None if 'quantite_ordre' in cls.__name__ or 'quantite_receptionnee' in cls.__name__ else 0.0

    @field_validator('ordre', 'type_ordre', 'statut_ordre', 'poste', 'statut_poste', 'division',
                    'magasin', 'article', 'libelle_article', 'ref_externe', 'description_externe',
                    'udm', 'fournisseur', 'description_fournisseur', 'lot', mode='before')
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

        # Générer l'id si non fourni
        if not self.id:
            if self.type == TypeReception.INTERNE and self.ordre and self.article:
                # Utiliser ordre + article + date_reception + poste (sans heure)
                if self.date_reception:
                    date_str = self.date_reception.strftime("%Y%m%d")
                    poste_str = self.poste if self.poste else "NOPOSTE"
                    self.id = f"{self.ordre}_{self.article}_{date_str}_{poste_str}"
                else:
                    # Si pas de date de réception, utiliser la date de création
                    date_str = self.date_creation.strftime("%Y%m%d")
                    poste_str = self.poste if self.poste else "NOPOSTE"
                    self.id = f"{self.ordre}_{self.article}_{date_str}_{poste_str}"
            else:
                # Pour les réceptions prestataires, utiliser un id auto-généré
                import uuid
                self.id = str(uuid.uuid4())

        # Convertir les états de réceptions internes vers l'état unifié
        if self.type == TypeReception.INTERNE and self.statut_ordre:
            if self.statut_ordre.upper() in ["RELÂCHÉ", "RELACHE"]:
                self.etat = EtatReception.RELACHE
            elif self.statut_ordre.upper() in ["EN_ATTENTE", "EN ATTENTE"]:
                self.etat = EtatReception.EN_ATTENTE
            elif self.statut_ordre.upper() in ["TERMINÉ", "TERMINE"]:
                self.etat = EtatReception.TERMINEE
            elif self.statut_ordre.upper() in ["ANNULÉ", "ANNULE"]:
                self.etat = EtatReception.ANNULEE
            else:
                self.etat = EtatReception.EN_COURS

    def model_dump(self) -> Dict[str, Any]:
        """Sérialise le modèle en dictionnaire"""
        return {
            "id": self.id,
            "type": self.type.value if self.type else None,
            "matiere": self.matiere.model_dump() if self.matiere else None,
            "quantite": self.quantite,
            "lot": self.lot,
            "qualification": self.qualification,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "etat": self.etat.value if self.etat else None,
            # Champs spécifiques aux réceptions internes
            "ordre": self.ordre,
            "type_ordre": self.type_ordre,
            "statut_ordre": self.statut_ordre,
            "poste": self.poste,
            "statut_poste": self.statut_poste,
            "division": self.division,
            "magasin": self.magasin,
            "article": self.article,
            "libelle_article": self.libelle_article,
            "ref_externe": self.ref_externe,
            "description_externe": self.description_externe,
            "quantite_ordre": self.quantite_ordre,
            "quantite_receptionnee": self.quantite_receptionnee,
            "udm": self.udm,
            "fournisseur": self.fournisseur,
            "description_fournisseur": self.description_fournisseur,
            "date_reception": self.date_reception.isoformat() if self.date_reception else None
        }

    @classmethod
    def from_model_dump(cls, data: Dict[str, Any]) -> 'Reception':
        """
        Désérialise un dictionnaire en modèle, avec gestion des valeurs manquantes

        Args:
            data: Le dictionnaire à désérialiser

        Returns:
            Reception: L'instance de Reception créée
        """
        # Copie du dictionnaire pour éviter de modifier l'original
        processed_data = data.copy()

        # Valeurs par défaut pour les champs manquants
        if "id" not in processed_data:
            processed_data["id"] = None

        if "type" not in processed_data:
            processed_data["type"] = TypeReception.PRESTATAIRE
        elif isinstance(processed_data["type"], str):
            try:
                processed_data["type"] = TypeReception(processed_data["type"])
            except ValueError:
                processed_data["type"] = TypeReception.PRESTATAIRE

        if "quantite" not in processed_data:
            processed_data["quantite"] = 0.0

        if "lot" not in processed_data:
            processed_data["lot"] = ""

        if "qualification" not in processed_data:
            processed_data["qualification"] = False

        if "date_creation" not in processed_data:
            processed_data["date_creation"] = datetime.now().replace(tzinfo=None)
        elif isinstance(processed_data["date_creation"], str):
            try:
                date_creation = datetime.fromisoformat(processed_data["date_creation"])
                # S'assurer que la date est naive (sans timezone) pour éviter les erreurs de comparaison
                if date_creation.tzinfo is not None:
                    date_creation = date_creation.replace(tzinfo=None)
                processed_data["date_creation"] = date_creation
            except ValueError:
                processed_data["date_creation"] = datetime.now().replace(tzinfo=None)

        if "date_modification" not in processed_data:
            processed_data["date_modification"] = datetime.now().replace(tzinfo=None)
        elif isinstance(processed_data["date_modification"], str):
            try:
                date_modification = datetime.fromisoformat(processed_data["date_modification"])
                # S'assurer que la date est naive (sans timezone) pour éviter les erreurs de comparaison
                if date_modification.tzinfo is not None:
                    date_modification = date_modification.replace(tzinfo=None)
                processed_data["date_modification"] = date_modification
            except ValueError:
                processed_data["date_modification"] = datetime.now().replace(tzinfo=None)

        # Gestion de date_reception si elle existe
        if "date_reception" in processed_data and isinstance(processed_data["date_reception"], str):
            try:
                date_reception = datetime.fromisoformat(processed_data["date_reception"])
                # S'assurer que la date est naive (sans timezone) pour éviter les erreurs de comparaison
                if date_reception.tzinfo is not None:
                    date_reception = date_reception.replace(tzinfo=None)
                processed_data["date_reception"] = date_reception
            except ValueError:
                processed_data["date_reception"] = None

        if "etat" not in processed_data:
            processed_data["etat"] = EtatReception.EN_COURS
        elif isinstance(processed_data["etat"], str):
            etat_found = False
            for etat in EtatReception:
                if etat.value == processed_data["etat"]:
                    processed_data["etat"] = etat
                    etat_found = True
                    break
            if not etat_found:
                processed_data["etat"] = EtatReception.EN_COURS

        # Traitement de la matière
        if "matiere" not in processed_data or processed_data["matiere"] is None:
            # Créer une matière par défaut
            processed_data["matiere"] = Matiere(code_mp="UNKNOWN", nom="Matière inconnue")
        elif isinstance(processed_data["matiere"], dict):
            try:
                processed_data["matiere"] = Matiere.from_model_dump(processed_data["matiere"])
            except Exception:
                processed_data["matiere"] = Matiere(code_mp="UNKNOWN", nom="Matière inconnue")

        # Création de l'instance
        try:
            return cls(**processed_data)
        except Exception as e:
            print(f"Erreur lors de la création de la réception: {e}")
            # En dernier recours, créer une réception avec des valeurs par défaut
            return cls(
                id=None,  # Sera généré automatiquement
                matiere=Matiere(code_mp="UNKNOWN", nom="Matière inconnue"),
                quantite=0,
                lot="",
                qualification=False,
                date_creation=datetime.now().replace(tzinfo=None),
                date_modification=datetime.now().replace(tzinfo=None),
                etat=EtatReception.EN_COURS
            )
