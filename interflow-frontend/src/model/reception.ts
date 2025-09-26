import { Matiere, MatiereModel } from './matiere';

export enum EtatReception {
  EN_COURS = "en_cours",
  TERMINEE = "terminée",
  ANNULEE = "annulée",
  RELACHE = "relâché",
  EN_ATTENTE = "en_attente"
}

export enum TypeReception {
  EXTERNE = "externe",
  INTERNE = "interne"
}

export interface Reception {
  id?: string;
  type: TypeReception;
  matiere: Matiere;
  quantite: number;
  lot: string;
  qualification: boolean;
  date_creation: Date;
  date_modification?: Date | null;
  
  // Champs spécifiques aux réceptions internes
  ordre?: string | null;
  type_ordre?: string | null;
  statut_ordre?: string | null;
  poste?: string | null;
  statut_poste?: string | null;
  division?: string | null;
  magasin?: string | null;
  article?: string | null;
  libelle_article?: string | null;
  ref_externe?: string | null;
  description_externe?: string | null;
  quantite_ordre?: number | null;
  quantite_receptionnee?: number | null;
  udm?: string | null;
  fournisseur?: string | null;
  description_fournisseur?: string | null;
  date_reception?: Date | null;
  
  // État unifié (pour compatibilité)
  etat: EtatReception;
}

export class ReceptionModel implements Reception {
  id?: string;
  type: TypeReception;
  matiere: Matiere;
  quantite: number;
  lot: string;
  qualification: boolean;
  date_creation: Date;
  date_modification?: Date | null;
  
  // Champs spécifiques aux réceptions internes
  ordre?: string | null;
  type_ordre?: string | null;
  statut_ordre?: string | null;
  poste?: string | null;
  statut_poste?: string | null;
  division?: string | null;
  magasin?: string | null;
  article?: string | null;
  libelle_article?: string | null;
  ref_externe?: string | null;
  description_externe?: string | null;
  quantite_ordre?: number | null;
  quantite_receptionnee?: number | null;
  udm?: string | null;
  fournisseur?: string | null;
  description_fournisseur?: string | null;
  date_reception?: Date | null;
  
  // État unifié (pour compatibilité)
  etat: EtatReception;

  constructor(data: Partial<Reception>) {
    this.type = data.type || TypeReception.EXTERNE;
    this.matiere = data.matiere || new MatiereModel({ code_mp: "UNKNOWN", nom: "Matière inconnue" });
    this.quantite = data.quantite || 0;
    this.lot = data.lot || "";
    this.qualification = data.qualification || false;
    this.date_creation = data.date_creation || new Date();
    this.date_modification = data.date_modification || null;
    
    // Champs spécifiques aux réceptions internes
    this.ordre = data.ordre || null;
    this.type_ordre = data.type_ordre || null;
    this.statut_ordre = data.statut_ordre || null;
    this.poste = data.poste || null;
    this.statut_poste = data.statut_poste || null;
    this.division = data.division || null;
    this.magasin = data.magasin || null;
    this.article = data.article || null;
    this.libelle_article = data.libelle_article || null;
    this.ref_externe = data.ref_externe || null;
    this.description_externe = data.description_externe || null;
    this.quantite_ordre = data.quantite_ordre || null;
    this.quantite_receptionnee = data.quantite_receptionnee || null;
    this.udm = data.udm || null;
    this.fournisseur = data.fournisseur || null;
    this.description_fournisseur = data.description_fournisseur || null;
    this.date_reception = data.date_reception || null;
    
    this.etat = data.etat || EtatReception.EN_COURS;
    
    // Générer l'id si non fourni
    if (!data.id) {
      if (this.type === TypeReception.INTERNE && this.ordre && this.article) {
        // Utiliser ordre + article + date_reception + poste (sans heure)
        if (this.date_reception) {
          const dateStr = this.date_reception.toISOString().split('T')[0].replace(/-/g, '');
          const posteStr = this.poste || "NOPOSTE";
          this.id = `${this.ordre}_${this.article}_${dateStr}_${posteStr}`;
        } else {
          // Si pas de date de réception, utiliser la date de création
          const dateStr = this.date_creation.toISOString().split('T')[0].replace(/-/g, '');
          const posteStr = this.poste || "NOPOSTE";
          this.id = `${this.ordre}_${this.article}_${dateStr}_${posteStr}`;
        }
      } else {
        // Pour les réceptions prestataires, utiliser un id auto-généré
        this.id = crypto.randomUUID();
      }
    } else {
      this.id = data.id;
    }
    
    // Convertir les états de réceptions internes vers l'état unifié
    if (this.type === TypeReception.INTERNE && this.statut_ordre) {
      const statutUpper = this.statut_ordre.toUpperCase();
      if (statutUpper.includes("RELÂCHÉ") || statutUpper.includes("RELACHE")) {
        this.etat = EtatReception.RELACHE;
      } else if (statutUpper.includes("EN_ATTENTE") || statutUpper.includes("EN ATTENTE")) {
        this.etat = EtatReception.EN_ATTENTE;
      } else if (statutUpper.includes("TERMINÉ") || statutUpper.includes("TERMINE")) {
        this.etat = EtatReception.TERMINEE;
      } else if (statutUpper.includes("ANNULÉ") || statutUpper.includes("ANNULE")) {
        this.etat = EtatReception.ANNULEE;
      } else {
        this.etat = EtatReception.EN_COURS;
      }
    }
  }

  static fromData(data: Record<string, any>): ReceptionModel {
    const processedData = { ...data };
    
    // Valeurs par défaut pour les champs manquants
    if (!processedData.type) {
      processedData.type = TypeReception.EXTERNE;
    } else if (typeof processedData.type === 'string') {
      try {
        processedData.type = Object.values(TypeReception).find(t => t === processedData.type) || TypeReception.EXTERNE;
      } catch (error) {
        processedData.type = TypeReception.EXTERNE;
      }
    }
    
    if (!processedData.quantite) {
      processedData.quantite = 0;
    }
    
    if (!processedData.lot) {
      processedData.lot = "";
    }
    
    if (processedData.qualification === undefined) {
      processedData.qualification = false;
    }
    
    // Gestion des dates
    if (!processedData.date_creation) {
      processedData.date_creation = new Date();
    } else if (typeof processedData.date_creation === 'string') {
      try {
        processedData.date_creation = new Date(processedData.date_creation);
      } catch (error) {
        processedData.date_creation = new Date();
      }
    }
    
    if (processedData.date_modification && typeof processedData.date_modification === 'string') {
      try {
        processedData.date_modification = new Date(processedData.date_modification);
      } catch (error) {
        processedData.date_modification = null;
      }
    }
    
    if (processedData.date_reception && typeof processedData.date_reception === 'string') {
      try {
        processedData.date_reception = new Date(processedData.date_reception);
      } catch (error) {
        processedData.date_reception = null;
      }
    }
    
    // Gestion de l'état
    if (!processedData.etat) {
      processedData.etat = EtatReception.EN_COURS;
    } else if (typeof processedData.etat === 'string') {
      processedData.etat = Object.values(EtatReception).find(e => e === processedData.etat) || EtatReception.EN_COURS;
    }
    
    // Traitement de la matière
    if (!processedData.matiere) {
      processedData.matiere = new MatiereModel({ code_mp: "UNKNOWN", nom: "Matière inconnue" });
    } else if (typeof processedData.matiere === 'object') {
      try {
        processedData.matiere = MatiereModel.fromData(processedData.matiere);
      } catch (error) {
        processedData.matiere = new MatiereModel({ code_mp: "UNKNOWN", nom: "Matière inconnue" });
      }
    }
    
    try {
      return new ReceptionModel(processedData);
    } catch (error) {
      console.error("Erreur lors de la création de la réception:", error);
      // En dernier recours, créer une réception avec des valeurs par défaut
      return new ReceptionModel({
        type: TypeReception.EXTERNE,
        matiere: new MatiereModel({ code_mp: "UNKNOWN", nom: "Matière inconnue" }),
        quantite: 0,
        lot: "",
        qualification: false,
        date_creation: new Date(),
        etat: EtatReception.EN_COURS
      });
    }
  }

  toData(): Record<string, any> {
    return {
      id: this.id,
      type: this.type,
      matiere: this.matiere instanceof MatiereModel ? this.matiere.toData() : this.matiere,
      quantite: this.quantite,
      lot: this.lot,
      qualification: this.qualification,
      date_creation: this.date_creation.toISOString(),
      date_modification: this.date_modification?.toISOString() || null,
      etat: this.etat,
      // Champs spécifiques aux réceptions internes
      ordre: this.ordre,
      type_ordre: this.type_ordre,
      statut_ordre: this.statut_ordre,
      poste: this.poste,
      statut_poste: this.statut_poste,
      division: this.division,
      magasin: this.magasin,
      article: this.article,
      libelle_article: this.libelle_article,
      ref_externe: this.ref_externe,
      description_externe: this.description_externe,
      quantite_ordre: this.quantite_ordre,
      quantite_receptionnee: this.quantite_receptionnee,
      udm: this.udm,
      fournisseur: this.fournisseur,
      description_fournisseur: this.description_fournisseur,
      date_reception: this.date_reception?.toISOString() || null
    };
  }
} 