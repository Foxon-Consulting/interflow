import { 
  AnalyseApiResponse, 
  AnalyseData, 
  AnalyseResult,
  CouvertureParBesoin
} from "@/model/analyse";
import { BesoinModel } from "@/model/besoin";
import { API_BASE_URL, API_ENDPOINTS } from '@/config/api';

// Type pour la réponse de l'endpoint /analyse/besoins
export interface AnalyseBesoinsResponse {
  metadata: {
    total_besoins: number;
    date_analyse: string;
    description: string;
  };
  statistiques: {
    couvert: number;
    partiel: number;
    non_couvert: number;
    inconnu: number;
    taux_couverture: number;
  };
  besoins: BesoinModel[];
}

/**
 * Service pour calculer les analyses de couverture via l'API
 */
export class AnalyseService {

  /**
   * Récupère l'analyse complète de tous les besoins avec leur état de couverture
   * Utilise le nouvel endpoint /analyse/besoins
   */
  static async analyserTousLesBesoins(): Promise<AnalyseBesoinsResponse> {
    console.log(`🔬 [ANALYSE-SERVICE] Lancement de l'analyse complète des besoins`);
    
    try {
      const url = `${API_BASE_URL}${API_ENDPOINTS.ANALYSE_BESOINS}`;
      console.log(`🔬 [ANALYSE-SERVICE] Appel API: ${url}`);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log(`✅ [ANALYSE-SERVICE] Analyse complète récupérée:`, {
        total_besoins: data.metadata?.total_besoins,
        statistiques: data.statistiques,
        besoins_count: data.besoins?.length
      });
      
      // Convertir les besoins en modèles BesoinModel
      const besoinsModels = data.besoins.map((besoin: Record<string, unknown>) => {
        return BesoinModel.fromData({
          ...besoin,
          echeance: new Date(besoin.echeance as string)
        });
      });
      
      return {
        metadata: data.metadata,
        statistiques: data.statistiques,
        besoins: besoinsModels
      };
      
    } catch (error) {
      console.error(`❌ [ANALYSE-SERVICE] Erreur lors de l'analyse complète des besoins:`, error);
      throw error;
    }
  }
  
  /**
   * Récupère les données d'analyse depuis l'API globale (toutes les matières)
   */
  static async recupererAnalyseGlobale(horizonDays: number = 5, dateInitiale?: string): Promise<Record<string, CouvertureParBesoin[]>> {
    console.log(`📊 [ANALYSE-SERVICE] Récupération de l'analyse globale`);
    
    try {
      // Utiliser la date actuelle si aucune date n'est fournie
      const date = dateInitiale || new Date().toISOString().split('T')[0];
      
      const url = `${API_BASE_URL}${API_ENDPOINTS.ANALYSE_GLOBALE}?horizon_days=${horizonDays}&date_initiale=${date}`;
      console.log(`📊 [ANALYSE-SERVICE] Appel API globale: ${url}`);
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log(`📊 [ANALYSE-SERVICE] Données globales récupérées:`, data);
      
      // Regrouper les couvertures par code MP
      const couvertureParCodeMp: Record<string, CouvertureParBesoin[]> = {};
      
             // L'API globale retourne une structure différente, adapter selon la réponse réelle
       if (data.couverture_par_matiere) {
         Object.entries(data.couverture_par_matiere).forEach(([codeMp, analyseMatiere]: [string, unknown]) => {
           const matiere = analyseMatiere as Record<string, unknown>;
           if (matiere.couverture_par_besoin) {
             couvertureParCodeMp[codeMp] = matiere.couverture_par_besoin as CouvertureParBesoin[];
           }
         });
       } else if (data.couverture_par_besoin) {
        // Si l'API retourne directement un tableau, regrouper par code MP extrait de l'ID
        const couvertures = data.couverture_par_besoin as CouvertureParBesoin[];
        couvertures.forEach(couverture => {
          // Extraire le code MP de l'ID du besoin (format probable: "codeMp_date_quantite" ou similaire)
          const codeMp = this.extractCodeMpFromBesoinId(couverture.besoin_id);
          if (codeMp) {
            if (!couvertureParCodeMp[codeMp]) {
              couvertureParCodeMp[codeMp] = [];
            }
            couvertureParCodeMp[codeMp].push(couverture);
          }
        });
      }
      
      console.log(`📊 [ANALYSE-SERVICE] Couvertures regroupées par code MP:`, couvertureParCodeMp);
      return couvertureParCodeMp;
      
    } catch (error) {
      console.error(`❌ [ANALYSE-SERVICE] Erreur lors de la récupération de l'analyse globale:`, error);
      throw error;
    }
  }

  /**
   * Extrait le code MP de l'ID du besoin
   */
  private static extractCodeMpFromBesoinId(besoinId: string): string | null {
    // L'ID du besoin peut avoir différents formats selon l'API
    // Essayer différentes stratégies d'extraction
    
    // Stratégie 1: ID contient le code MP au début (ex: "H2SO4_2024-01-15_100")
    const parts = besoinId.split('_');
    if (parts.length > 0) {
      return parts[0];
    }
    
    // Stratégie 2: ID contient le code MP entre des délimiteurs
    const match = besoinId.match(/^([A-Z0-9]+)/);
    if (match) {
      return match[1];
    }
    
    // Stratégie 3: retourner l'ID tel quel si pas de pattern reconnu
    console.warn(`⚠️ [ANALYSE-SERVICE] Format d'ID de besoin non reconnu: ${besoinId}`);
    return besoinId;
  }

  /**
   * Récupère les données d'analyse depuis l'API
   */
  static async recupererDonneesAnalyse(codeMp: string, horizonDays: number = 5, dateInitiale?: string): Promise<AnalyseApiResponse> {
    // console.log(`📊 [ANALYSE-SERVICE] Récupération des données d'analyse pour le code MP: ${codeMp}`);
    
    try {
      // Utiliser la date actuelle si aucune date n'est fournie
      const date = dateInitiale || new Date().toISOString().split('T')[0];
      
      const url = `${API_BASE_URL}${API_ENDPOINTS.ANALYSE_MATIERE}/${codeMp}?horizon_days=${horizonDays}&date_initiale=${date}`;
      // console.log(`📊 [ANALYSE-SERVICE] Appel API: ${url}`);
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status} ${response.statusText}`);
      }
      
      const data: AnalyseApiResponse = await response.json();
      // console.log(`📊 [ANALYSE-SERVICE] Données récupérées avec succès:`, data);
      
      return data;
      
    } catch (error) {
      console.error(`❌ [ANALYSE-SERVICE] Erreur lors de la récupération des données d'analyse pour ${codeMp}:`, error);
      throw error;
    }
  }
  
  /**
   * Calcule les quantités pour un code MP donné en utilisant l'API
   */
  static async calculerQuantites(codeMp: string, horizonDays: number = 5, dateInitiale?: string): Promise<AnalyseResult> {
    // console.log(`📊 [ANALYSE-SERVICE] Calcul des quantités pour le code MP: ${codeMp}`);
    
    try {
      const apiData = await this.recupererDonneesAnalyse(codeMp, horizonDays, dateInitiale);
      
      const result: AnalyseResult = {
        besoin: apiData.analyse_matiere.quantite_besoin_totale,
        stocks_internes: apiData.analyse_matiere.quantite_stock_internes,
        receptions: apiData.analyse_matiere.quantite_commandes, // Utiliser quantite_commandes à la place
        rappatriements: apiData.analyse_matiere.quantite_rappatriements,
        stocks_externes_par_magasin: apiData.analyse_matiere.stocks_externes,
        nom_matiere: apiData.analyse_matiere.nom_matiere,
        taux_couverture: apiData.analyse_matiere.taux_couverture,
        quantite_totale_disponible: apiData.analyse_matiere.quantite_totale_disponible,
        stock_manquant: apiData.analyse_matiere.stock_manquant,
        couverture_par_besoin: apiData.couverture_par_besoin,
        analyse_chronologique: apiData.analyse_chronologique
      };
      
      // console.log(`📊 [ANALYSE-SERVICE] Résultats pour ${codeMp}:`, result);
      return result;
      
    } catch (error) {
      console.error(`❌ [ANALYSE-SERVICE] Erreur lors du calcul des quantités pour ${codeMp}:`, error);
      return {
        besoin: 0,
        stocks_internes: 0,
        receptions: 0,
        rappatriements: 0,
        stocks_externes_par_magasin: {}
      };
    }
  }
  
  /**
   * Génère les données pour le graphique
   */
  static async genererDonneesGraphique(codeMp: string, horizonDays: number = 5, dateInitiale?: string): Promise<AnalyseData[]> {
    const quantites = await this.calculerQuantites(codeMp, horizonDays, dateInitiale);
    
    // Créer l'objet de données avec les stocks externes par magasin
    const stockData: AnalyseData = {
      comparaison: "stock",
      besoin: 0,
      stocks_internes: quantites.stocks_internes,
      receptions: quantites.receptions,
      rappatriements: quantites.rappatriements,
      ...quantites.stocks_externes_par_magasin
    };
    
    return [
      {
        comparaison: "besoin",
        besoin: quantites.besoin,
        stocks_internes: 0,
        receptions: 0,
        commandes: 0,
        rappatriements: 0
      },
      stockData
    ];
  }
} 