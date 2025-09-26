import { Besoin, BesoinModel, Etat } from './besoin';

// ============================================================================
// MODÈLES POUR L'API D'ANALYSE (nouveaux)
// ============================================================================

/**
 * Métadonnées de l'analyse retournées par l'API
 */
export interface AnalyseApiMetadata {
  date_initiale: string;
  date_limite: string;
  horizon_jours: number;
  code_mp: string;
}

/**
 * Données principales de la matière retournées par l'API
 */
export interface AnalyseApiMatiere {
  code_mp: string;
  nom_matiere: string;
  total_besoins: number;
  total_couverts: number;
  taux_couverture: number;
  quantite_besoin_totale: number;
  quantite_stock_internes: number;
  stocks_externes: { [magasin: string]: number };
  quantite_commandes: number;
  quantite_rappatriements: number;
  quantite_totale_disponible: number;
  stock_couverture_disponible: number;
  stock_manquant: number;
}

/**
 * Détails de couverture par besoin retournés par l'API
 */
export interface CouvertureParBesoin {
  besoin_id: string;
  quantite: number;
  echeance: string;
  etat_couverture: string;
  quantite_disponible: number;
  pourcentage_couverture: number;
  stock_restant: number;
}

/**
 * Étape chronologique retournée par l'API
 */
export interface EtapeChronologiqueApi {
  echeance: string;
  quantite_besoin: number;
  stock_avant: number;
  stock_apres: number;
  etat: string;
}

/**
 * Analyse chronologique retournée par l'API
 */
export interface AnalyseApiChronologique {
  stock_initial: number;
  stock_final: number;
  premier_besoin_non_couvert: string | null;
  etapes_chronologiques: EtapeChronologiqueApi[];
}

/**
 * Réponse complète de l'API d'analyse
 */
export interface AnalyseApiResponse {
  metadata: AnalyseApiMetadata;
  analyse_matiere: AnalyseApiMatiere;
  couverture_par_besoin: CouvertureParBesoin[];
  analyse_chronologique: AnalyseApiChronologique;
}

/**
 * Modèle pour les données d'analyse simplifiées utilisées dans l'interface
 */
export interface AnalyseData {
  comparaison: string;
  besoin: number;
  stocks_internes: number;
  receptions: number;
  rappatriements: number;
  [key: string]: string | number; // Signature d'index pour compatibilité avec ChartDataItem
}

/**
 * Résultat d'analyse utilisé par le service
 */
export interface AnalyseResult {
  besoin: number;
  stocks_internes: number;
  receptions: number;
  rappatriements: number;
  stocks_externes_par_magasin: { [magasin: string]: number };
  nom_matiere?: string;
  taux_couverture?: number;
  quantite_totale_disponible?: number;
  stock_manquant?: number;
  couverture_par_besoin?: CouvertureParBesoin[];
  analyse_chronologique?: AnalyseApiChronologique;
}

// ============================================================================
// MODÈLES EXISTANTS (pour compatibilité)
// ============================================================================

export interface CouvertureBesoin {
  besoin: Besoin;
  quantite_besoin: number;
  quantite_stock_internes: number;
  quantite_stock_externes: number;
  quantite_commandes: number;
  quantite_rappatriements: number;
  quantite_disponible_couverture: number;
  etat_couverture: Etat;
  pourcentage_couverture: number;
  stock_restant_apres_consommation: number;
}

export class CouvertureBesoinModel implements CouvertureBesoin {
  besoin: Besoin;
  quantite_besoin: number;
  quantite_stock_internes: number;
  quantite_stock_externes: number;
  quantite_commandes: number;
  quantite_rappatriements: number;
  quantite_disponible_couverture: number;
  etat_couverture: Etat;
  pourcentage_couverture: number;
  stock_restant_apres_consommation: number;

  constructor(data: CouvertureBesoin) {
    this.besoin = data.besoin;
    this.quantite_besoin = data.quantite_besoin;
    this.quantite_stock_internes = data.quantite_stock_internes;
    this.quantite_stock_externes = data.quantite_stock_externes;
    this.quantite_commandes = data.quantite_commandes;
    this.quantite_rappatriements = data.quantite_rappatriements;
    this.quantite_disponible_couverture = data.quantite_disponible_couverture;
    this.etat_couverture = data.etat_couverture;
    this.pourcentage_couverture = data.pourcentage_couverture;
    this.stock_restant_apres_consommation = data.stock_restant_apres_consommation;
  }

  static fromData(data: Record<string, unknown>): CouvertureBesoinModel {
    const processedData = { ...data } as CouvertureBesoin;
    
    // Gestion du besoin
    if (processedData.besoin && typeof processedData.besoin === 'object') {
      processedData.besoin = BesoinModel.fromData(processedData.besoin as Record<string, unknown>);
    }
    
    // Gestion de l'état de couverture
    if (typeof processedData.etat_couverture === 'string') {
      processedData.etat_couverture = Object.values(Etat).find(e => e === processedData.etat_couverture) || Etat.INCONNU;
    }
    
    return new CouvertureBesoinModel(processedData);
  }
}

export interface EtapeChronologique {
  echeance: string;
  quantite_besoin: number;
  stock_avant: number;
  stock_apres: number;
  etat: Etat;
}

export class EtapeChronologiqueModel implements EtapeChronologique {
  echeance: string;
  quantite_besoin: number;
  stock_avant: number;
  stock_apres: number;
  etat: Etat;

  constructor(data: EtapeChronologique) {
    this.echeance = data.echeance;
    this.quantite_besoin = data.quantite_besoin;
    this.stock_avant = data.stock_avant;
    this.stock_apres = data.stock_apres;
    this.etat = data.etat;
  }

  static fromData(data: Record<string, unknown>): EtapeChronologiqueModel {
    const processedData = { ...data } as EtapeChronologique;
    
    // Gestion de l'état
    if (typeof processedData.etat === 'string') {
      processedData.etat = Object.values(Etat).find(e => e === processedData.etat) || Etat.INCONNU;
    }
    
    return new EtapeChronologiqueModel(processedData);
  }
}

export interface PremierBesoinNonCouvert {
  index: number;
  echeance: string;
  quantite_besoin: number;
  stock_restant: number;
  quantite_manquante: number;
}

export class PremierBesoinNonCouvertModel implements PremierBesoinNonCouvert {
  index: number;
  echeance: string;
  quantite_besoin: number;
  stock_restant: number;
  quantite_manquante: number;

  constructor(data: PremierBesoinNonCouvert) {
    this.index = data.index;
    this.echeance = data.echeance;
    this.quantite_besoin = data.quantite_besoin;
    this.stock_restant = data.stock_restant;
    this.quantite_manquante = data.quantite_manquante;
  }

  static fromData(data: Record<string, unknown>): PremierBesoinNonCouvertModel {
    return new PremierBesoinNonCouvertModel(data as PremierBesoinNonCouvert);
  }
}

export interface AnalyseChronologique {
  couverture_chronologique: EtapeChronologique[];
  premier_besoin_non_couvert?: PremierBesoinNonCouvert | null;
  stock_initial: number;
  stock_final: number;
}

export class AnalyseChronologiqueModel implements AnalyseChronologique {
  couverture_chronologique: EtapeChronologique[];
  premier_besoin_non_couvert?: PremierBesoinNonCouvert | null;
  stock_initial: number;
  stock_final: number;

  constructor(data: AnalyseChronologique) {
    this.couverture_chronologique = data.couverture_chronologique;
    this.premier_besoin_non_couvert = data.premier_besoin_non_couvert || null;
    this.stock_initial = data.stock_initial;
    this.stock_final = data.stock_final;
  }

  static fromData(data: Record<string, unknown>): AnalyseChronologiqueModel {
    const processedData = { ...data } as AnalyseChronologique;
    
    // Gestion des étapes chronologiques
    if (processedData.couverture_chronologique && Array.isArray(processedData.couverture_chronologique)) {
      processedData.couverture_chronologique = processedData.couverture_chronologique.map(
        (etape: Record<string, unknown>) => EtapeChronologiqueModel.fromData(etape)
      );
    }
    
    // Gestion du premier besoin non couvert
    if (processedData.premier_besoin_non_couvert && typeof processedData.premier_besoin_non_couvert === 'object') {
      processedData.premier_besoin_non_couvert = PremierBesoinNonCouvertModel.fromData(processedData.premier_besoin_non_couvert as Record<string, unknown>);
    }
    
    return new AnalyseChronologiqueModel(processedData);
  }
}

export interface AnalyseMatiere {
  code_mp: string;
  nom_matiere: string;
  total_besoins: number;
  total_couverts: number;
  taux_couverture: number;
  quantite_besoin_totale: number;
  quantite_stock_internes: number;
  quantite_stock_externes: number;
  quantite_commandes: number;
  quantite_rappatriements: number;
  quantite_totale_disponible: number;
  couverture_par_besoin: CouvertureBesoin[];
  analyse_chronologique: AnalyseChronologique;
}

export class AnalyseMatiereModel implements AnalyseMatiere {
  code_mp: string;
  nom_matiere: string;
  total_besoins: number;
  total_couverts: number;
  taux_couverture: number;
  quantite_besoin_totale: number;
  quantite_stock_internes: number;
  quantite_stock_externes: number;
  quantite_commandes: number;
  quantite_rappatriements: number;
  quantite_totale_disponible: number;
  couverture_par_besoin: CouvertureBesoin[];
  analyse_chronologique: AnalyseChronologique;

  constructor(data: AnalyseMatiere) {
    this.code_mp = data.code_mp;
    this.nom_matiere = data.nom_matiere;
    this.total_besoins = data.total_besoins;
    this.total_couverts = data.total_couverts;
    this.taux_couverture = data.taux_couverture;
    this.quantite_besoin_totale = data.quantite_besoin_totale;
    this.quantite_stock_internes = data.quantite_stock_internes;
    this.quantite_stock_externes = data.quantite_stock_externes;
    this.quantite_commandes = data.quantite_commandes;
    this.quantite_rappatriements = data.quantite_rappatriements;
    this.quantite_totale_disponible = data.quantite_totale_disponible;
    this.couverture_par_besoin = data.couverture_par_besoin;
    this.analyse_chronologique = data.analyse_chronologique;
  }

  static fromData(data: Record<string, unknown>): AnalyseMatiereModel {
    const processedData = { ...data } as AnalyseMatiere;
    
    // Gestion de la couverture par besoin
    if (processedData.couverture_par_besoin && Array.isArray(processedData.couverture_par_besoin)) {
      processedData.couverture_par_besoin = processedData.couverture_par_besoin.map(
        (couverture: Record<string, unknown>) => CouvertureBesoinModel.fromData(couverture)
      );
    }
    
    // Gestion de l'analyse chronologique
    if (processedData.analyse_chronologique && typeof processedData.analyse_chronologique === 'object') {
      processedData.analyse_chronologique = AnalyseChronologiqueModel.fromData(processedData.analyse_chronologique as Record<string, unknown>);
    }
    
    return new AnalyseMatiereModel(processedData);
  }
}

export interface StatistiquesMatiere {
  nom: string;
  total_besoins: number;
  total_couverts: number;
  total_partiels: number;
  total_non_couverts: number;
  quantite_besoin_totale: number;
  quantite_disponible_totale: number;
  quantite_rappatriements: number;
  taux_couverture: number;
  taux_partiel: number;
  taux_non_couvert: number;
}

export class StatistiquesMatiereModel implements StatistiquesMatiere {
  nom: string;
  total_besoins: number;
  total_couverts: number;
  total_partiels: number;
  total_non_couverts: number;
  quantite_besoin_totale: number;
  quantite_disponible_totale: number;
  quantite_rappatriements: number;
  taux_couverture: number;
  taux_partiel: number;
  taux_non_couvert: number;

  constructor(data: StatistiquesMatiere) {
    this.nom = data.nom;
    this.total_besoins = data.total_besoins;
    this.total_couverts = data.total_couverts;
    this.total_partiels = data.total_partiels;
    this.total_non_couverts = data.total_non_couverts;
    this.quantite_besoin_totale = data.quantite_besoin_totale;
    this.quantite_disponible_totale = data.quantite_disponible_totale;
    this.quantite_rappatriements = data.quantite_rappatriements;
    this.taux_couverture = data.taux_couverture;
    this.taux_partiel = data.taux_partiel;
    this.taux_non_couvert = data.taux_non_couvert;
  }

  static fromData(data: Record<string, unknown>): StatistiquesMatiereModel {
    return new StatistiquesMatiereModel(data as StatistiquesMatiere);
  }
}

export interface AnalyseCouverture {
  horizon_jours: number;
  date_initiale: Date;
  date_limite: Date;
  
  // Pour analyse complète (toutes les matières)
  couverture_par_matiere: Record<string, AnalyseMatiere>;
  statistiques_par_matiere: Record<string, StatistiquesMatiere>;
  
  // Pour analyse matière unique
  analyse_matiere?: AnalyseMatiere | null;
}

export class AnalyseCouvertureModel implements AnalyseCouverture {
  horizon_jours: number;
  date_initiale: Date;
  date_limite: Date;
  couverture_par_matiere: Record<string, AnalyseMatiere>;
  statistiques_par_matiere: Record<string, StatistiquesMatiere>;
  analyse_matiere?: AnalyseMatiere | null;

  constructor(data: AnalyseCouverture) {
    this.horizon_jours = data.horizon_jours;
    this.date_initiale = data.date_initiale;
    this.date_limite = data.date_limite;
    this.couverture_par_matiere = data.couverture_par_matiere;
    this.statistiques_par_matiere = data.statistiques_par_matiere;
    this.analyse_matiere = data.analyse_matiere || null;
  }

  static fromData(data: Record<string, unknown>): AnalyseCouvertureModel {
    const processedData = { ...data } as AnalyseCouverture;
    
    // Gestion des dates
    if (processedData.date_initiale && typeof processedData.date_initiale === 'string') {
      processedData.date_initiale = new Date(processedData.date_initiale);
    }
    
    if (processedData.date_limite && typeof processedData.date_limite === 'string') {
      processedData.date_limite = new Date(processedData.date_limite);
    }
    
    // Gestion de la couverture par matière
    if (processedData.couverture_par_matiere && typeof processedData.couverture_par_matiere === 'object') {
      const couverture: Record<string, AnalyseMatiere> = {};
      Object.entries(processedData.couverture_par_matiere).forEach(([key, value]) => {
        couverture[key] = AnalyseMatiereModel.fromData(value as Record<string, unknown>);
      });
      processedData.couverture_par_matiere = couverture;
    }
    
    // Gestion des statistiques par matière
    if (processedData.statistiques_par_matiere && typeof processedData.statistiques_par_matiere === 'object') {
      const statistiques: Record<string, StatistiquesMatiere> = {};
      Object.entries(processedData.statistiques_par_matiere).forEach(([key, value]) => {
        statistiques[key] = StatistiquesMatiereModel.fromData(value as Record<string, unknown>);
      });
      processedData.statistiques_par_matiere = statistiques;
    }
    
    // Gestion de l'analyse matière unique
    if (processedData.analyse_matiere && typeof processedData.analyse_matiere === 'object') {
      processedData.analyse_matiere = AnalyseMatiereModel.fromData(processedData.analyse_matiere as Record<string, unknown>);
    }
    
    return new AnalyseCouvertureModel(processedData);
  }

  totalBesoins(): number {
    if (this.analyse_matiere) {
      return this.analyse_matiere.total_besoins;
    }
    return Object.values(this.couverture_par_matiere).reduce(
      (total, analyse) => total + analyse.total_besoins, 0
    );
  }

  totalCouverts(): number {
    if (this.analyse_matiere) {
      return this.analyse_matiere.total_couverts;
    }
    return Object.values(this.couverture_par_matiere).reduce(
      (total, analyse) => total + analyse.total_couverts, 0
    );
  }

  tauxCouverture(): number {
    const total = this.totalBesoins();
    if (total === 0) {
      return 0;
    }
    return (this.totalCouverts() / total) * 100;
  }
} 