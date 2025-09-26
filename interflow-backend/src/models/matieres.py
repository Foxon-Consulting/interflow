from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class Matiere(BaseModel):
    code_mp: str = Field(..., description="Code de la matière première")
    nom: str = Field(..., description="Nom de la matière")
    description: str | None = Field(None, description="Description de la matière")
    fds: str | None = Field(None, description="Fiche de données de sécurité")
    seveso: bool | None = Field(None, description="Classification Seveso")
    internal_reference: str | None = Field(None, description="Référence interne")

    @classmethod
    def from_model_dump(cls, data: Dict[str, Any]) -> 'Matiere':
        """
        Désérialise un dictionnaire en modèle, avec gestion des valeurs manquantes

        Args:
            data: Le dictionnaire à désérialiser

        Returns:
            Matiere: L'instance de Matiere créée
        """
        # Copie du dictionnaire pour éviter de modifier l'original
        processed_data = data.copy()

        # Valeurs par défaut pour les champs obligatoires manquants
        if "code_mp" not in processed_data or not processed_data["code_mp"]:
            processed_data["code_mp"] = "UNKNOWN"

        if "nom" not in processed_data or not processed_data["nom"]:
            processed_data["nom"] = "Matière inconnue"

        # Création de l'instance
        try:
            return cls(**processed_data)
        except Exception as e:
            print(f"Erreur lors de la création de la matière: {e}")
            # En dernier recours, créer une matière avec des valeurs par défaut
            return cls(code_mp="UNKNOWN", nom="Matière inconnue")

    def model_dump(self) -> Dict[str, Any]:
        """Sérialise le modèle en dictionnaire"""
        return {
            "code_mp": self.code_mp,
            "nom": self.nom,
            "description": self.description,
            "fds": self.fds,
            "seveso": self.seveso,
            "internal_reference": self.internal_reference
        }
