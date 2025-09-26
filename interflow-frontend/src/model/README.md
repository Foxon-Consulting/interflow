# Modèles TypeScript

Ce dossier contient les modèles TypeScript correspondants aux modèles Python de l'API FastAPI.

## Structure

### 📁 Fichiers

- **`matiere.ts`** - Modèle de base pour les matières premières
- **`besoin.ts`** - Modèle pour les besoins opérationnels (Besoins)
- **`stock.ts`** - Modèle pour la gestion des stocks
- **`reception.ts`** - Modèle pour les réceptions (internes et externes)
- **`rappatriement.ts`** - Modèle pour les rapatriements et produits
- **`analyse.ts`** - Modèles pour l'analyse de couverture des besoins

### 🔧 Utilisation

```typescript
import { MatiereModel } from '@/model/matiere';
import { BesoinModel, Etat } from '@/model/besoin';
import { StockModel } from '@/model/stock';
import { ReceptionModel, TypeReception, EtatReception } from '@/model/reception';
import { RappatriementModel, ProduitRappatriementModel, TypeEmballage } from '@/model/rappatriement';
import { CouvertureParBesoin } from '@/model/analyse';

// Créer une matière
const matiere = new MatiereModel({
  code_mp: "H2SO4",
  nom: "Acide sulfurique",
  seveso: true
});

// Créer un besoin
const besoin = new BesoinModel({
  matiere: matiere,
  quantite: 100,
  echeance: new Date("2024-12-31"),
  etat: Etat.INCONNU,
  lot: "LOT001"
});

// Sérialiser/Désérialiser
const data = besoin.toData();
const besoinFromData = BesoinModel.fromData(data);
```

### 🔄 Correspondance avec Python

| TypeScript | Python | Description |
|------------|--------|-------------|
| `MatiereModel` | `Matiere` | Matières premières |
| `BesoinModel` | `Besoin` | Besoins opérationnels |
| `StockModel` | `Stock` | Gestion des stocks |
| `ReceptionModel` | `Reception` | Réceptions |
| `RappatriementModel` | `Rappatriement` | Rapatriements |
| `ProduitRappatriementModel` | `ProduitRappatriement` | Produits de rapatriement |
| `AnalyseCouvertureModel` | `AnalyseCouverture` | Analyses de couverture |

### 📋 Enums

- **`Etat`** - États des besoins (INCONNU, PARTIEL, COUVERT, NON_COUVERT)
- **`TypeReception`** - Types de réceptions (EXTERNE, INTERNE)
- **`EtatReception`** - États des réceptions (EN_COURS, TERMINEE, ANNULEE, etc.)
- **`TypeEmballage`** - Types d'emballages (CARTON, SAC, CONTENEUR, AUTRE)

### 🛠️ Méthodes

Chaque modèle dispose de :
- **`constructor(data)`** - Création avec validation
- **`static fromData(data)`** - Désérialisation depuis un objet
- **`toData()`** - Sérialisation vers un objet
- **Génération automatique d'IDs** - Pour les modèles qui en ont besoin

### 🔍 Validation

Les modèles incluent une validation automatique avec :
- Valeurs par défaut pour les champs manquants
- Gestion des erreurs de désérialisation
- Conversion de types automatique (dates, enums)
- Fallback sur des valeurs par défaut en cas d'erreur 