// Configuration de l'API
// Log value of NEXT_PUBLIC_API_URL
console.log('NEXT_PUBLIC_API_URL :', process.env.NEXT_PUBLIC_API_URL);
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

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