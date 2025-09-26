# Repositories - Documentation

## Architecture

Les repositories utilisent le pattern **Repository** avec le pattern **Strategy** pour le stockage des données.

### Structure

```
repositories/
├── base_repository.py               # Repository de base générique
├── storage_strategies.py            # Stratégies de stockage (JSON, CSV)
├── besoins_repository.py            # Repository des besoins
├── receptions_repository.py         # Repository des réceptions
├── rappatriements_repository.py     # Repository des rapatriements
├── stocks_repository.py             # Repository des stocks
├── matieres_premieres_repository.py # Repository des matières
└── __init__.py                      # Exports
```

## BaseRepository

### Fonctionnalités communes
- **CRUD** : Create, Read, Update, Delete
- **Filtrage** : Par attributs
- **Import/Export** : CSV, JSON
- **Gestion des erreurs** : Valeurs par défaut et instances de secours

### Méthodes principales
```python
class BaseRepository[T]:
    def get_all() -> List[T]
    def get_by_id(id_value: Any) -> Optional[T]
    def create(item: T) -> T
    def update(id_value: Any, updated_item: T) -> Optional[T]
    def delete(id_value: Any) -> bool
    def filter(**kwargs) -> List[T]
    def import_from_csv(csv_path: str, decoder_class) -> None
    def flush() -> None
    def count() -> int
    def exists(id_value: Any) -> bool
```

## Repositories spécialisés

### BesoinsRepository
- **Modèle** : `Besoin`
- **ID** : `id` (auto-généré)
- **États** : `Etat.INCONNU`, `Etat.PARTIEL`, `Etat.COUVERT`, `Etat.NON_COUVERT`

#### Méthodes métier
```python
def get_besoins_by_etat(etat: Etat) -> List[Besoin]
def get_besoins_actuels_by_horizon(horizon_days: int, date_initiale: datetime) -> List[Besoin]
def get_besoins_critiques(seuil_jours: int, date_reference: datetime) -> List[Besoin]
def filter_besoins_advanced(**filters) -> List[Besoin]
def update_etat(id: int, nouvel_etat: Etat) -> Optional[Besoin]
```

### ReceptionsRepository
- **Modèle** : `Reception`
- **ID** : `id` (auto-généré ou basé sur ordre_article_date_poste pour les réceptions internes)
- **États** : `EtatReception.EN_COURS`, `EtatReception.TERMINEE`, `EtatReception.ANNULEE`, `EtatReception.RELACHE`
- **Types** : `TypeReception.INTERNE`, `TypeReception.PRESTATAIRE`

#### Méthodes métier
```python
def get_receptions_by_etat(etat: EtatReception) -> List[Reception]
def get_receptions_by_matiere(code_mp: str) -> List[Reception]
def get_receptions_by_type(type_reception: TypeReception) -> List[Reception]
def get_receptions_by_fournisseur(fournisseur: str) -> List[Reception]
def get_total_quantity_by_matiere(code_mp: str) -> float
def update_etat(id: str, nouvel_etat: EtatReception) -> Optional[Reception]
def filter_receptions_advanced(**filters) -> List[Reception]
```

### RappatriementsRepository
- **Modèle** : `Rappatriement`
- **ID** : `numero_transfert`
- **Emballages** : `TypeEmballage.SAC`, `TypeEmballage.CONTENEUR`, `TypeEmballage.AUTRE`

#### Méthodes métier
```python
def get_rappatriement_by_numero(numero_transfert: str) -> Optional[Rappatriement]
def get_rappatriements_by_date_range(date_debut: datetime, date_fin: datetime) -> List[Rappatriement]
def get_rappatriements_by_responsable(responsable: str) -> List[Rappatriement]
def get_rappatriements_by_adresse_destinataire(adresse_partielle: str) -> List[Rappatriement]
def get_rappatriements_by_produit(code_produit: str) -> List[Rappatriement]
def get_rappatriements_by_matiere(code_matiere: str) -> List[Rappatriement]
def get_rappatriements_by_type_emballage(type_emballage: TypeEmballage) -> List[Rappatriement]
def get_rappatriements_by_poids_min(poids_min: float) -> List[Rappatriement]
def get_rappatriements_by_nb_palettes_min(nb_palettes_min: int) -> List[Rappatriement]
def update_rappatriement(numero_transfert: str, **updates) -> Optional[Rappatriement]
def filter_rappatriements_advanced(**filters) -> List[Rappatriement]
```

### StocksRepository
- **Modèle** : `Stock`
- **ID** : `{article}_{magasin}_{emplacement}_{contenant}`

#### Méthodes métier
```python
def get_internal_stocks() -> List[Stock]
def get_external_stocks() -> List[Stock]
def get_stocks_by_matiere(code_mp: str) -> List[Stock]
def get_stocks_by_magasin(magasin: str) -> List[Stock]
def get_stocks_by_statut(statut_lot: str) -> List[Stock]
def get_total_quantity_by_matiere(code_mp: str) -> float
def get_total_internal_quantity_by_matiere(code_mp: str) -> float
def get_total_external_quantity_by_matiere(code_mp: str) -> float
def update_quantity(id: str, nouvelle_quantite: float) -> Optional[Stock]
def filter_stocks_advanced(**filters) -> List[Stock]
```

### MatieresPremieresRepository
- **Modèle** : `Matiere`
- **ID** : `code_mp`

#### Méthodes métier
```python
def get_matiere_by_code(code_mp: str) -> Optional[Matiere]
def get_matiere_by_name(nom: str) -> Optional[Matiere]
def get_matieres_by_type(type_matiere: str) -> List[Matiere]
def from_name(name: str) -> Matiere
def from_code_mp(code_mp: str) -> Matiere
def import_from_json(json_path: str) -> None
```

## Stratégies de stockage

### JSONStorageStrategy
- Stockage en format JSON
- Encodage UTF-8
- Gestion des erreurs de décodage

### CSVStorageStrategy
- Stockage en format CSV
- Encodage UTF-8
- Gestion des en-têtes

### Utilisation
```python
from repositories.storage_strategies import JSONStorageStrategy, CSVStorageStrategy

# Repository avec stockage JSON
json_storage = JSONStorageStrategy()
besoins_repo = BesoinsRepository(json_storage)

# Repository avec stockage CSV
csv_storage = CSVStorageStrategy()
stocks_repo = StocksRepository(csv_storage)
```

## Bonnes pratiques

### 1. Gestion des erreurs
```python
# Les repositories gèrent automatiquement les erreurs
try:
    besoin = besoins_repo.get_by_id("BESOIN_001")
except Exception as e:
    print(f"Erreur: {e}")
    # Le repository retourne None ou une instance par défaut
```

### 2. Import de données
```python
# Import depuis CSV avec décodeur spécialisé
besoins_repo.import_from_csv("data/besoins.csv")  # Utilise BODecoder

# Import depuis JSON
matieres_repo.import_from_json("data/matieres.json")

# Import de rapatriements depuis fichiers Excel
rappatriements_repo.import_excel_files(["fichier1.xlsx", "fichier2.xlsx"])
```

### 3. Filtrage avancé
```python
# Filtrage simple
besoins = besoins_repo.filter(etat=Etat.INCONNU)

# Filtrage avancé pour les besoins
besoins = besoins_repo.filter_besoins_advanced(
    etat=Etat.INCONNU,
    code_mp="MP001",
    date_debut=datetime.now(),
    quantite_min=100.0
)

# Filtrage avancé pour les réceptions
receptions = receptions_repo.filter_receptions_advanced(
    etat=EtatReception.EN_COURS,
    type_reception=TypeReception.INTERNE,
    quantite_min=50.0,
    date_reception_debut=datetime(2024, 1, 1)
)

# Filtrage avancé pour les rapatriements
rappatriements = rappatriements_repo.filter_rappatriements_advanced(
    responsable="John",
    type_emballage=TypeEmballage.SAC,
    poids_min=100.0,
    date_debut=datetime(2024, 1, 1)
)
```

### 4. Mise à jour d'état
```python
# Mise à jour d'état avec validation
besoin = besoins_repo.update_etat("BESOIN_001", Etat.COUVERT)
reception = receptions_repo.update_etat("REC_001", EtatReception.TERMINEE)
```

## Cohérence avec les modèles

### Enums utilisés
- **`Etat`** : États des besoins (dans `models.besoin`)
- **`EtatReception`** : États des réceptions (dans `models.reception`)
- **`TypeReception`** : Types de réceptions (dans `models.reception`)
- **`TypeEmballage`** : Types d'emballage (dans `models.rappatriement`)

### Validation automatique
- Les repositories utilisent les modèles Pydantic
- Validation automatique des données
- Gestion des erreurs de validation

### Sérialisation/Désérialisation
```python
# Les modèles fournissent automatiquement
item.model_dump()           # Sérialisation
ModelClass.from_model_dump() # Désérialisation
```

## Exemples d'utilisation

### Initialisation
```python
from repositories import (
    BesoinsRepository,
    ReceptionsRepository,
    RappatriementsRepository,
    StocksRepository,
    JSONStorageStrategy
)

# Créer les repositories
storage = JSONStorageStrategy()
besoins_repo = BesoinsRepository(storage)
receptions_repo = ReceptionsRepository(storage)
rappatriements_repo = RappatriementsRepository(storage)
stocks_repo = StocksRepository(storage)
```

### Opérations CRUD
```python
# Créer
nouveau_besoin = Besoin(matiere=matiere, quantite=100, echeance=datetime.now())
besoin_creé = besoins_repo.create(nouveau_besoin)

nouvelle_reception = Reception(
    matiere=matiere,
    quantite=50.0,
    type=TypeReception.PRESTATAIRE,
    date_creation=datetime.now()
)
reception_creee = receptions_repo.create(nouvelle_reception)

# Lire
besoin = besoins_repo.get_by_id("BESOIN_001")
reception = receptions_repo.get_by_id("REC_001")
rappatriement = rappatriements_repo.get_rappatriement_by_numero("TRANS_001")
tous_besoins = besoins_repo.get_all()

# Mettre à jour
besoin.quantite = 150
besoin_mis_a_jour = besoins_repo.update("BESOIN_001", besoin)

# Supprimer
supprimé = besoins_repo.delete("BESOIN_001")
```

### Requêtes métier
```python
# Besoins critiques
besoins_critiques = besoins_repo.get_besoins_critiques(seuil_jours=7)

# Réceptions par état
receptions_en_cours = receptions_repo.get_receptions_by_etat(EtatReception.EN_COURS)

# Rapatriements par responsable
rappatriements_john = rappatriements_repo.get_rappatriements_by_responsable("John")

# Rapatriements par plage de dates
rappatriements_mois = rappatriements_repo.get_rappatriements_by_date_range(
    datetime(2024, 1, 1),
    datetime(2024, 1, 31)
)

# Stocks internes
stocks_internes = stocks_repo.get_internal_stocks()

# Quantité totale par matière
quantite_totale_stock = stocks_repo.get_total_quantity_by_matiere("MP001")
quantite_totale_reception = receptions_repo.get_total_quantity_by_matiere("MP001")
```
