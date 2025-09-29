// Configuration de l'API
// Utilise les API Routes Next.js qui proxifient vers le backend en interne
// En développement, peut utiliser l'URL directe du backend si définie
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

// Log pour débuguer
console.log('🔍 API Configuration:', {
  NODE_ENV: process.env.NODE_ENV,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  API_BASE_URL,
  isServer: typeof window === 'undefined'
});

// Configuration des endpoints
export const API_ENDPOINTS = {
  // Besoins
  BESOINS: '/besoins',
  BESOINS_EN_COURS: '/besoins/en-cours',
  
  // Stocks
  STOCKS: '/stocks',
  
  // Réceptions
  RECEPTIONS: '/receptions',
  RECEPTIONS_BY_TYPE: '/receptions/type',
  RECEPTIONS_BY_ETAT: '/receptions/etat',
  RECEPTIONS_BY_MATIERE: '/receptions/matiere',
  GENERER_BON_RECEPTION: '/receptions/generer-bon',
  
  // Rapatriements
  RAPPATRIEMENTS: '/rappatriements',
  RAPPATRIEMENTS_EN_COURS: '/rappatriements/en-cours',
  
  // Matières
  MATIERES: '/matieres',
  
  // Analyses
  ANALYSE_BESOINS: '/analyse/besoins',
  ANALYSE_GLOBALE: '/analyse',
  ANALYSE_MATIERE: '/analyse/matiere',
} as const; 