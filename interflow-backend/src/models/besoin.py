from pydantic import BaseModel, Field
from models.matieres import Matiere

from datetime import datetime, timedelta
from enum import Enum
from typing import List, Iterator, Optional

class Etat(Enum):
    INCONNU = "inconnu"
    PARTIEL = "partiel"  # Couverture partielle
    COUVERT = "couvert"
    NON_COUVERT = "non_couvert"  # Ajout pour la cohérence


class Besoin(BaseModel):
    id: Optional[str] = Field(None, description="Identifiant unique du besoin (généré automatiquement)")
    matiere: Matiere = Field(..., description="Matière associée au besoin")
    quantite: float = Field(..., description="Quantité nécessaire", ge=0)
    echeance: datetime = Field(..., description="Date d'échéance du besoin")
    etat: Etat = Field(..., description="État du besoin")
    lot: str = Field(..., description="Numéro de lot")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Générer l'id à partir du code_mp de la matière + échéance + lot si non fourni
        if not self.id and self.matiere:
            date_str = self.echeance.strftime("%Y%m%d")
            lot_str = self.lot.strip() if self.lot else ""
            if lot_str:
                self.id = f"{self.matiere.code_mp}_{date_str}_{lot_str}"
            else:
                self.id = f"{self.matiere.code_mp}_{date_str}"

    def model_dump(self):
        return {
            "id": self.id,
            "matiere": self.matiere.model_dump(),
            "quantite": self.quantite,
            "echeance": self.echeance.isoformat() if self.echeance else None,
            "etat": self.etat.value,
            "lot": self.lot
        }

    def model_dump_json(self, **kwargs):
        """
        Sérialise le modèle en JSON

        Args:
            **kwargs: Arguments passés à json.dumps

        Returns:
            str: Le JSON sérialisé
        """
        import json
        return json.dumps(self.model_dump(), **kwargs)

    @classmethod
    def from_model_dump(cls, data: dict):
        """
        Désérialise un dictionnaire en modèle Besoin

        Args:
            data: Le dictionnaire à désérialiser

        Returns:
            Besoin: L'instance de Besoin créée
        """
        # Copie du dictionnaire pour éviter de modifier l'original
        processed_data = data.copy()

        # Gestion des valeurs par défaut pour les champs obligatoires
        if "etat" not in processed_data or not processed_data["etat"]:
            processed_data["etat"] = Etat.INCONNU

        if "lot" not in processed_data or not processed_data["lot"]:
            processed_data["lot"] = ""

        # Si etat est une string, la convertir en enum
        if isinstance(processed_data["etat"], str):
            try:
                processed_data["etat"] = Etat(processed_data["etat"])
            except ValueError:
                processed_data["etat"] = Etat.INCONNU

        # Gestion de la matière si c'est un dictionnaire
        if "matiere" in processed_data and isinstance(processed_data["matiere"], dict):
            from models.matieres import Matiere
            processed_data["matiere"] = Matiere.from_model_dump(processed_data["matiere"])

        # Gestion de l'échéance si c'est une string
        if "echeance" in processed_data and isinstance(processed_data["echeance"], str):
            try:
                echeance = datetime.fromisoformat(processed_data["echeance"])
                # S'assurer que la date est naive (sans timezone) pour éviter les erreurs de comparaison
                if echeance.tzinfo is not None:
                    echeance = echeance.replace(tzinfo=None)
                processed_data["echeance"] = echeance
            except ValueError:
                # Fallback pour d'autres formats de date
                try:
                    processed_data["echeance"] = datetime.strptime(processed_data["echeance"], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    processed_data["echeance"] = datetime.now().replace(tzinfo=None)

        # On ne passe jamais id, il sera généré automatiquement
        processed_data.pop("id", None)

        # Création de l'instance
        try:
            return cls(**processed_data)
        except Exception as e:
            print(f"Erreur lors de la création du besoin: {e}")
            # En dernier recours, créer un besoin avec des valeurs par défaut
            from models.matieres import Matiere
            return cls(
                matiere=processed_data.get("matiere", Matiere(code_mp="UNKNOWN", nom="Matière inconnue")),
                quantite=processed_data.get("quantite", 0.0),
                echeance=processed_data.get("echeance", datetime.now().replace(tzinfo=None)),
                etat=processed_data.get("etat", Etat.INCONNU),
                lot=processed_data.get("lot", "")
            )
