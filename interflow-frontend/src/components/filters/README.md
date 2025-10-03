# Composant SearchFilter

Un composant réutilisable pour ajouter des fonctionnalités de recherche et de filtrage à vos pages.

## Installation

```typescript
import { SearchFilter, FilterConfig } from "@/components/filters";
```

## Utilisation actuelle dans l'application

Le composant `SearchFilter` est actuellement utilisé dans les pages suivantes :
- **Besoins** (`/app/besoins/page.tsx`) - Filtrage par état de couverture
- **Stocks** (`/app/stocks/page.tsx`) - Filtrage par magasin (dynamique)
- **Réceptions** (`/app/receptions/page.tsx`) - Filtrage par type et état
- **Rappatriements** (`/app/rappatriements/page.tsx`) - Filtrage par type d'emballage

## Utilisation de base

```typescript
// États pour les filtres
const [rechercheText, setRechercheText] = useState("");
const [filtreType, setFiltreType] = useState<string>("tous");

// Configuration des filtres
const filterConfigs: FilterConfig[] = [
  {
    key: "type",
    label: "Type",
    options: [
      { value: "option1", label: "Option 1" },
      { value: "option2", label: "Option 2" }
    ]
  }
];

const filterValues = {
  type: filtreType
};

const handleFilterChange = (filterKey: string, value: string) => {
  if (filterKey === "type") {
    setFiltreType(value);
  }
};

// Dans votre JSX
<SearchFilter
  searchValue={rechercheText}
  onSearchChange={setRechercheText}
  searchPlaceholder="Rechercher..."
  filters={filterConfigs}
  filterValues={filterValues}
  onFilterChange={handleFilterChange}
  onRefresh={refetch}
  resultCount={filteredData.length}
  resultLabel="résultat(s) trouvé(s)"
  isLoading={isLoading}
/>
```

## Props

### Props obligatoires

- `searchValue`: string - Valeur actuelle de la recherche
- `onSearchChange`: (value: string) => void - Fonction appelée lors du changement de recherche

### Props optionnelles

- `searchPlaceholder`: string - Placeholder du champ de recherche (défaut: "Rechercher...")
- `filters`: FilterConfig[] - Configuration des filtres par select
- `filterValues`: Record<string, string> - Valeurs actuelles des filtres
- `onFilterChange`: (filterKey: string, value: string) => void - Fonction appelée lors du changement de filtre
- `onRefresh`: () => void - Fonction appelée lors du clic sur "Recharger"
- `onReset`: () => void - Fonction appelée lors du clic sur "Reset"
- `resultCount`: number - Nombre de résultats trouvés
- `resultLabel`: string - Label pour les résultats (défaut: "résultat(s) trouvé(s)")
- `title`: string - Titre du panneau de filtres (défaut: "Filtres et Recherche")
- `className`: string - Classes CSS supplémentaires
- `children`: ReactNode - Contenu additionnel à afficher dans le panneau
- `isLoading`: boolean - État de chargement

## Exemples d'implémentation

### Page Rappatriements

```typescript
const filterConfigs: FilterConfig[] = [
  {
    key: "typeEmballage",
    label: "Type d'emballage",
    options: [
      { value: "carton", label: "Carton" },
      { value: "sac", label: "Sac" },
      { value: "conteneur", label: "Conteneur" },
      { value: "autre", label: "Autre" }
    ]
  }
];
```

### Page Réceptions

```typescript
const filterConfigs: FilterConfig[] = [
  {
    key: "type",
    label: "Type",
    options: [
      { value: TypeReception.EXTERNE, label: "Prestataire" },
      { value: TypeReception.INTERNE, label: "Interne" }
    ]
  },
  {
    key: "etat",
    label: "État",
    options: [
      { value: EtatReception.EN_COURS, label: "En cours" },
      { value: EtatReception.TERMINEE, label: "Terminée" },
      // ...
    ]
  }
];
```

### Page Stocks (filtres dynamiques)

```typescript
const filterConfigs: FilterConfig[] = useMemo(() => {
  if (!stockData) return [];
  
  const magasinsUniques = [...new Set(stockData.map(s => s.magasin))].filter(Boolean).sort();
  
  return [
    {
      key: "magasin",
      label: "Magasin",
      options: magasinsUniques.map(m => ({ value: m, label: m }))
    }
  ];
}, [stockData]);
```

### Page Besoins

```typescript
const filterConfigs: FilterConfig[] = useMemo(() => {
  return [
    {
      key: "etat",
      label: "État de couverture",
      options: [
        { value: "tous", label: "Tous les états" },
        { value: "COUVERT", label: "Couvert" },
        { value: "PARTIEL", label: "Partiel" },
        { value: "NON_COUVERT", label: "Non couvert" },
        { value: "INCONNU", label: "Inconnu" }
      ]
    }
  ];
}, []);
```

## Logique de filtrage

Pour implémenter la logique de filtrage dans votre composant :

```typescript
// Filtrage des données
const donneesFiltrees = useMemo(() => {
  if (!donnees) return [];
  
  return donnees.filter((item) => {
    const matchRecherche = rechercheText === "" || 
      item.nom.toLowerCase().includes(rechercheText.toLowerCase()) ||
      item.code.toLowerCase().includes(rechercheText.toLowerCase());
    
    const matchType = filtreType === "tous" || item.type === filtreType;
    
    return matchRecherche && matchType;
  });
}, [donnees, rechercheText, filtreType]);
```

## Fonctionnalités

- ✅ Recherche textuelle avec placeholder configurable
- ✅ Filtres par select avec options configurables
- ✅ Bouton de reset pour réinitialiser tous les filtres
- ✅ Bouton de rechargement optionnel
- ✅ Compteur de résultats avec label configurable
- ✅ Support du state de chargement
- ✅ Interface responsive
- ✅ Contenu additionnel via children
- ✅ Titre configurable
- ✅ Classes CSS personnalisées 