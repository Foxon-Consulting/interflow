# Architecture InterFlow Frontend

## Vue d'ensemble

InterFlow Frontend est une application de gestion logistique organisée selon une architecture en couches avec une séparation claire des responsabilités. L'application gère les stocks, besoins, réceptions, rappatriements et analyses de couverture.

## Architecture Générale

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Services      │    │   Backend API   │
│   (Next.js)     │◄──►│   Layer         │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Query   │    │   TypeScript    │    │   Database      │
│   Cache         │    │   Models        │    │   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Structure des Fichiers

```
src/
├── app/                          # Pages (Next.js App Router)
│   ├── besoins/                 # Module Besoins Opérationnels
│   │   ├── page.tsx             # Liste et analyse des besoins
│   │   └── create/page.tsx      # Création de nouveaux besoins
│   ├── stocks/page.tsx          # Gestion des stocks
│   ├── receptions/page.tsx      # Suivi des réceptions
│   ├── rappatriements/          # Module Rappatriements
│   │   ├── page.tsx             # Liste des rappatriements
│   │   └── create/page.tsx      # Création de rappatriements
│   ├── matieres/page.tsx        # Catalogue des matières
│   ├── analyses/page.tsx        # Analyses de couverture
│   ├── layout.tsx               # Layout principal
│   └── page.tsx                 # Dashboard d'accueil
├── components/                   # Composants réutilisables
│   ├── ui/                      # Composants UI de base (shadcn/ui)
│   ├── layouts/                 # Layouts de pages
│   ├── filters/                 # Composants de filtrage
│   ├── navigation.tsx           # Navigation principale
│   ├── data-table.tsx           # Tableau de données générique
│   └── import-file.tsx          # Composant d'import de fichiers
├── hooks/                       # Hooks React personnalisés
│   └── use-matiere-data.ts      # Hook pour téléchargement FDS
├── model/                       # Modèles TypeScript
│   ├── matiere.ts               # Modèle Matière
│   ├── besoin.ts                # Modèle Besoin
│   ├── stock.ts                 # Modèle Stock
│   ├── reception.ts             # Modèle Réception
│   ├── rappatriement.ts         # Modèle Rappatriement
│   └── analyse.ts               # Modèles d'analyse
├── services/                    # Services API
│   ├── matiere-service.ts       # API Matières
│   ├── besoin-service.ts        # API Besoins
│   ├── stock-service.ts         # API Stocks
│   ├── reception-service.ts     # API Réceptions
│   ├── rappatriement-service.ts # API Rappatriements
│   ├── analyse-service.ts       # API Analyses
│   └── import-service.ts        # Service d'import générique
├── providers/                   # Providers React
│   └── query-provider.tsx       # Provider React Query
└── lib/                         # Utilitaires
    └── utils.ts                 # Utilitaires Tailwind CSS
```

## Couches de l'Architecture

### 1. Couche Présentation (Pages)

**Responsabilité :** Interface utilisateur et logique d'affichage

#### Pages principales
- **Dashboard** (`/`) : Vue d'ensemble avec accès aux modules
- **Besoins** (`/besoins`) : Gestion des besoins avec analyse de couverture
- **Stocks** (`/stocks`) : Inventaire avec filtrage par magasin
- **Réceptions** (`/receptions`) : Suivi des réceptions internes/externes
- **Rappatriements** (`/rappatriements`) : Gestion des transferts
- **Matières** (`/matieres`) : Catalogue avec téléchargement FDS
- **Analyses** (`/analyses`) : Analyses de couverture avec graphiques

### 2. Couche Composants

**Responsabilité :** UI modulaire et réutilisable

#### Composants clés
- **ResourcePageLayout** : Layout standardisé pour les pages de données
- **DataTable** : Tableau générique avec tri et pagination
- **SearchFilter** : Composant de filtrage réutilisable
- **ImportFile** : Import de fichiers CSV/XLSX
- **Navigation** : Menu principal de l'application

### 3. Couche Services

**Responsabilité :** Communication avec l'API backend

#### Services par module
```typescript
// Pattern uniforme pour tous les services
export async function fetchAllEntityData(): Promise<EntityModel[]>
export async function createEntity(data: Entity): Promise<EntityModel>
export async function updateEntity(id: string, data: Partial<Entity>): Promise<EntityModel>
export async function deleteEntity(id: string): Promise<void>
export async function importEntityFromFile(file: File): Promise<void>
export async function flushEntity(): Promise<void>
```

### 4. Couche Modèles

**Responsabilité :** Types TypeScript et validation des données

#### Modèles principaux
- **MatiereModel** : Matières premières avec propriétés SEVESO
- **BesoinModel** : Besoins avec états de couverture
- **StockModel** : Stocks avec localisation par magasin
- **ReceptionModel** : Réceptions avec qualification
- **RappatriementModel** : Transferts avec produits associés

### 5. Couche Infrastructure

**Responsabilité :** Gestion d'état et utilitaires

- **React Query** : Cache et synchronisation des données
- **Import Service** : Service centralisé pour l'import de fichiers
- **TypeScript** : Typage statique pour la robustesse

## Flux de Données

### 1. Chargement de données
```
Page Component
    ↓ useQuery
React Query Cache
    ↓ queryFn
Service Layer
    ↓ fetch
Backend API
    ↓ response
TypeScript Models
    ↓ return
Component State
```

### 2. Mutations (Create/Update/Delete)
```
User Action
    ↓ onClick
Page Component
    ↓ mutationFn
Service Layer
    ↓ POST/PUT/DELETE
Backend API
    ↓ onSuccess
Query Invalidation
    ↓ refetch
Updated UI
```

### 3. Import de fichiers
```
File Upload
    ↓ ImportFile Component
Import Service
    ↓ detectFileType
Validation
    ↓ FormData
Backend API
    ↓ onSuccess
Cache Invalidation
    ↓ refetch
Updated Data
```

## Patterns Architecturaux

### 1. Gestion d'État
- **React Query** pour le cache des données serveur
- **useState** pour l'état local des composants
- **localStorage** pour la persistance côté client

### 2. Navigation et Routing
- **Next.js App Router** avec structure de dossiers
- **Navigation component** centralisé
- **Route handlers** pour les API endpoints

### 3. Validation et Types
- **TypeScript strict** avec interfaces complètes
- **Modèles de données** avec méthodes de sérialisation
- **Validation côté client** avant envoi API

### 4. Performance
- **Code splitting** automatique par page
- **React Query cache** avec invalidation intelligente
- **Optimistic updates** pour les mutations
- **Lazy loading** des composants lourds

## Configuration et Déploiement

### Environnements
```bash
# Développement
NEXT_PUBLIC_API_URL=http://localhost:5000

# Production
NEXT_PUBLIC_API_URL=https://api.production.com
NODE_ENV=production
```

### Docker
- **Multi-stage build** pour optimiser la taille
- **Non-root user** pour la sécurité
- **Standalone output** pour les performances

### CI/CD
- **ESLint** pour la qualité du code
- **TypeScript** check pour la validation
- **Build verification** avant déploiement

## Bonnes Pratiques Appliquées

### 1. Séparation des Responsabilités
- Pages ↔ Logique d'affichage uniquement
- Services ↔ Communication API uniquement
- Modèles ↔ Structure de données uniquement

### 2. Réutilisabilité
- Composants UI génériques (DataTable, SearchFilter)
- Services avec patterns uniformes
- Hooks personnalisés pour la logique métier

### 3. Maintenabilité
- Structure de dossiers cohérente
- Conventions de nommage claires
- Documentation inline et README

### 4. Performance
- React Query pour éviter les re-fetches inutiles
- Lazy loading des composants
- Optimisation des re-renders

### 5. Sécurité
- Validation TypeScript stricte
- Sanitisation des entrées utilisateur
- Variables d'environnement pour les configurations

## Évolutivité

L'architecture permet facilement :
- **Ajout de nouveaux modules** en suivant les patterns existants
- **Extension des modèles** pour de nouvelles propriétés
- **Intégration de nouvelles APIs** via la couche service
- **Amélioration de l'UI** sans impact sur la logique métier 