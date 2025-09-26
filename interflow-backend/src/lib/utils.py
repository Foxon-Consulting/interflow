from datetime import datetime
from enum import Enum
from typing import Any, List, Dict, Optional
import pandas as pd

# Fonction pour sérialiser les types spéciaux en JSON
def json_serializer(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, "model_dump"):
        return obj.model_dump()
    raise TypeError(f"Type {type(obj)} n'est pas sérialisable en JSON")


def compare_models(model1: Any, model2: Any) -> List[Dict[str, Any]]:
    """
    Compare deux modèles Pydantic, retourne les différences sous la forme :
    [
        {
            "key": "key",
            "value1": "value1",
            "value2": "value2"
        }
    ]
    """
    diff = []

    for key, value in model1.model_dump().items():
        if value != model2.model_dump()[key]:
            diff.append({
                "key": key,
                "value1": value,
                "value2": model2.model_dump()[key]
            })

    return diff


def parse_date(value: Any, format_str: str = '%d/%m/%Y %H:%M:%S') -> Optional[datetime]:
    """
    Parse une date de manière robuste

    Args:
        value: Valeur à parser (string, pandas.Timestamp, etc.)
        format_str: Format de date attendu

    Returns:
        datetime ou None si parsing échoue
    """
    if not value or pd.isna(value):
        return None

    try:
        if isinstance(value, str):
            return datetime.strptime(value, format_str)
        elif isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        else:
            return pd.to_datetime(value).to_pydatetime()
    except (ValueError, TypeError):
        return None


def validate_required_fields(row: dict, required_fields: List[str]) -> bool:
    """
    Valide que tous les champs obligatoires sont présents et non vides

    Args:
        row: Dictionnaire représentant une ligne
        required_fields: Liste des champs obligatoires

    Returns:
        True si tous les champs sont valides, False sinon
    """
    for field in required_fields:
        value = row.get(field, '').strip() if isinstance(row.get(field), str) else str(row.get(field, '')).strip()
        if not value:
            print(f"❌ Champ obligatoire vide: {field}")
            return False
    return True
