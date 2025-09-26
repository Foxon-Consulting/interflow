# Exemples d'Utilisation - Nouvelle Architecture

Ce dossier contient des exemples d'utilisation de la nouvelle architecture de repositories avec le pattern Strategy.

## 📁 Fichiers d'Exemples

### 1. `exemple_complet_repositories.py`
**Description** : Exemple complet d'utilisation de tous les repositories
- ✅ Création des repositories avec JSON storage
- ✅ Utilisation des méthodes métier spécifiques
- ✅ Import depuis CSV et JSON
- ✅ Opérations avancées et filtrage
- ✅ Exemple de migration future vers DB

**Utilisation** :
```bash
python src/examples/exemple_complet_repositories.py
```

### 2. `exemple_besoin_coverage_service.py`
**Description** : Exemple d'utilisation du service de couverture des besoins
- ✅ Initialisation du service avec les nouveaux repositories
- ✅ Analyse de couverture des besoins
- ✅ Création automatique de commandes
- ✅ Analyse détaillée de la couverture

**Utilisation** :
```bash
python src/examples/exemple_besoin_coverage_service.py
```

### 3. `exemple_import_json_matieres.py`
**Description** : Exemple spécifique pour l'import JSON des matières
- ✅ Import depuis différents formats JSON
- ✅ Création de fichiers JSON de référence
- ✅ Utilisation avancée des matières
- ✅ Gestion des erreurs

**Utilisation** :
```bash
python src/examples/exemple_import_json_matieres.py
```

## 🚀 Avantages de la Nouvelle Architecture

### **Simplicité**
- **5 repositories** au lieu de 8+ classes
- **Code centralisé** dans `BaseRepository`
- **Pas de duplication** de logique

### **Évolutivité**
```python
# Aujourd'hui : JSON
storage = JSONStorage("data")
besoins_repo = BesoinsRepository(storage)

# Demain : Base de données
storage = DBStorage(db_config)
besoins_repo = BesoinsRepository(storage)  # Même interface !
```

### **Import CSV Intégré**
```python
# Import automatique depuis CSV
besoins_repo.import_from_csv("data/besoins.csv")
```

### **Factory Pattern**
```python
# Création simple avec factory
besoins_repo = create_json_repository(BesoinsRepository)
```

## 📊 Comparaison Avant/Après

| Aspect | Avant | Après |
|--------|-------|-------|
| **Fichiers** | 7 fichiers | 3 fichiers |
| **Lignes de code** | ~1000 lignes | ~400 lignes |
| **Duplication** | 80% | 0% |
| **Migration DB** | Complexe | 1 ligne à changer |
| **Maintenance** | Difficile | Simple |

## 🔧 Utilisation Rapide

### **Création d'un Repository**
```python
from repositories import create_json_repository, BesoinsRepository

# Méthode simple
besoins_repo = create_json_repository(BesoinsRepository)

# Méthode explicite
from repositories.storage_strategies import JSONStorage
storage = JSONStorage("data")
besoins_repo = BesoinsRepository(storage)
```

### **Import depuis CSV et JSON**
```python
# Import automatique depuis CSV
besoins_repo.import_from_csv("data/besoins.csv")
stocks_repo.import_from_csv("data/stocks.csv")

# Import depuis JSON (pour les matières)
matieres_repo.import_from_json("data/matieres.json")
```

### **Utilisation des Méthodes**
```python
# Récupération des données
besoins_list = besoins_repo.get_besoins_list()
stocks_matiere = stocks_repo.get_stocks_by_matiere("CODE123")

# Création
nouveau_besoin = Besoin(...)
besoins_repo.create(nouveau_besoin)

# Mise à jour
besoin.etat = BesoinEtat.COUVERT
besoins_repo.update(besoin.id, besoin)
```

## 🎯 Migration Future

La migration vers une base de données sera aussi simple que :

```python
# Avant
storage = JSONStorage("data")

# Après
storage = DBStorage(db_config)

# Le reste du code reste identique !
```

## 📝 Notes

- Tous les exemples utilisent la nouvelle architecture Strategy
- Les exemples redondants ont été supprimés pour éviter la confusion
- Chaque exemple est autonome et peut être exécuté indépendamment
- Les exemples incluent la gestion d'erreurs et les cas limites
- Le fichier `exemple_complet_repositories.py` couvre tous les cas d'usage principaux
