# InterFlow Frontend

Une application frontend de gestion logistique construite avec Next.js, permettant de gérer les stocks, besoins, réceptions, rappatriements et analyses de couverture.

## 🚀 Fonctionnalités

### Modules principaux
- **Besoins opérationnels** - Gestion et analyse des besoins avec état de couverture
- **Stocks** - Gestion des stocks avec filtrage par magasin et division
- **Réceptions** - Suivi des réceptions internes et externes
- **Rappatriements** - Gestion des transferts de produits
- **Matières** - Catalogue des matières premières avec téléchargement FDS
- **Analyses** - Analyses de couverture avec visualisations graphiques

### Fonctionnalités transversales
- Import/Export de données (CSV, XLSX)
- Filtrage et recherche avancés
- Interface responsive moderne
- Gestion des états avec React Query
- Navigation intuitive

## 🛠️ Technologies utilisées

- **[Next.js 15](https://nextjs.org/)** - Framework React avec App Router
- **[TypeScript](https://www.typescriptlang.org/)** - Typage statique
- **[Tailwind CSS](https://tailwindcss.com/)** - Framework CSS utilitaire
- **[shadcn/ui](https://ui.shadcn.com/)** - Composants UI modernes
- **[React Query](https://tanstack.com/query)** - Gestion d'état et cache
- **[Lucide React](https://lucide.dev/)** - Icônes
- **[date-fns](https://date-fns.org/)** - Manipulation des dates

## 🚀 Démarrage rapide

### Prérequis
- Node.js 18+ 
- npm ou yarn

### Installation

1. **Clonez le projet**
```bash
git clone <url-du-repo>
cd interflow-frontend
```

2. **Installez les dépendances**
```bash
npm install
```

3. **Configurez l'environnement**
```bash
# Créez un fichier .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:5000" > .env.local  # Développement local uniquement
```

4. **Lancez l'application**
```bash
npm run dev
```

5. **Ouvrez [http://localhost:3000](http://localhost:3000)**

## 🏗️ Structure du projet

```
src/
├── app/                      # Pages (App Router Next.js)
│   ├── besoins/             # Gestion des besoins
│   ├── stocks/              # Gestion des stocks
│   ├── receptions/          # Suivi des réceptions
│   ├── rappatriements/      # Gestion des rappatriements
│   ├── matieres/            # Catalogue des matières
│   └── analyses/            # Analyses de couverture
├── components/              # Composants réutilisables
│   ├── ui/                  # Composants UI de base
│   ├── layouts/             # Layouts de pages
│   └── filters/             # Composants de filtrage
├── hooks/                   # Hooks React personnalisés
├── model/                   # Modèles TypeScript
├── services/                # Services API
├── lib/                     # Utilitaires
└── providers/               # Providers React
```

## 📱 Pages et fonctionnalités

### 🏠 **Accueil** (`/`)
- Dashboard avec accès rapide aux modules
- Statistiques globales
- Navigation vers les différentes sections

### 📋 **Besoins** (`/besoins`)
- Liste des besoins opérationnels
- Analyse de couverture automatique
- Import/Export CSV/XLSX
- Filtrage par état de couverture
- Création de nouveaux besoins

### 📦 **Stocks** (`/stocks`)
- Inventaire des stocks par magasin
- Filtrage par division et statut
- Tri par code matière, quantité, dates
- Import/Export des données

### 📥 **Réceptions** (`/receptions`)
- Suivi des réceptions internes/externes
- Filtrage par type et état
- Gestion des qualifications
- Historique des réceptions

### 🚚 **Rappatriements** (`/rappatriements`)
- Gestion des transferts de produits
- Calcul automatique des poids/volumes
- Filtrage par type d'emballage
- Création de nouveaux rappatriements

### 🧪 **Matières** (`/matieres`)
- Catalogue des matières premières
- Classification par type chimique
- Téléchargement des fiches de sécurité (FDS)
- Indicateurs SEVESO

### 📊 **Analyses** (`/analyses`)
- Analyses de couverture par matière
- Graphiques de comparaison
- Horizon d'analyse configurable
- Visualisation des stocks externes

## 🚢 Déploiement

### Docker
```bash
# Build de l'image
docker build -t interflow-frontend .

# Lancement avec Docker Compose
docker-compose up -d
```

### Variables d'environnement
```bash
NEXT_PUBLIC_API_URL=http://localhost:5000  # URL directe pour le développement local
NODE_ENV=production                        # Environnement
```

## 🔧 Scripts disponibles

```bash
npm run dev          # Serveur de développement
npm run build        # Build de production
npm run start        # Serveur de production
npm run lint         # Linting ESLint
npm run type-check   # Vérification TypeScript
```

## 🏛️ Architecture

L'application suit une architecture en couches :

- **Pages** - Interface utilisateur et logique d'affichage
- **Services** - Communication avec l'API via routes Next.js
- **Modèles** - Types TypeScript et validation
- **Hooks** - Logique métier réutilisable
- **Composants** - UI modulaire et réutilisable

### Flux de données
```
Pages → Services → API Routes Next.js → Backend Python (interne)
  ↓        ↓
React Query Cache ← Modèles TypeScript
```

### API Routes (Architecture SSR)

L'application utilise les **API Routes Next.js** pour une communication sécurisée :

- **Route catch-all** : `/api/[...path]/route.ts` proxifie tous les endpoints
- **Communication interne** : Next.js ↔ Backend Python (127.0.0.1:5000)
- **Pas d'exposition** : Le backend n'est jamais exposé à l'extérieur
- **Performance** : Tout en mémoire dans le même container

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.