import { Matiere, MatiereModel } from './matiere';

export enum Etat {
  INCONNU = "inconnu",
  PARTIEL = "partiel",
  COUVERT = "couvert",
  NON_COUVERT = "non_couvert"
}

export interface Besoin {
  id?: string;
  matiere: Matiere;
  quantite: number;
  echeance: Date;
  etat: Etat;
  lot: string;
}

export class BesoinModel implements Besoin {
  id?: string;
  matiere: Matiere;
  quantite: number;
  echeance: Date;
  etat: Etat;
  lot: string;

  constructor(data: Partial<Besoin>) {
    this.matiere = data.matiere || new MatiereModel({ code_mp: "UNKNOWN", nom: "Matière inconnue" });
    this.quantite = data.quantite || 0;
    this.echeance = data.echeance || new Date();
    this.etat = data.etat || Etat.INCONNU;
    this.lot = data.lot || "";
    
    // Générer l'id à partir du code_mp de la matière + échéance + lot si non fourni
    if (!data.id && this.matiere) {
      const dateStr = this.echeance.toISOString().split('T')[0].replace(/-/g, '');
      const lotStr = this.lot.trim();
      if (lotStr) {
        this.id = `${this.matiere.code_mp}_${dateStr}_${lotStr}`;
      } else {
        this.id = `${this.matiere.code_mp}_${dateStr}`;
      }
    } else {
      this.id = data.id;
    }
  }

  static fromData(data: Record<string, unknown>): BesoinModel {
    const processedData = { ...data };
    
    // Gestion des valeurs par défaut pour les champs obligatoires
    if (!processedData.etat) {
      processedData.etat = Etat.INCONNU;
    }
    
    if (!processedData.lot) {
      processedData.lot = "";
    }
    
    // Si etat est une string, la convertir en enum
    if (typeof processedData.etat === 'string') {
      try {
        processedData.etat = Object.values(Etat).find(e => e === processedData.etat) || Etat.INCONNU;
      } catch (error) {
        processedData.etat = Etat.INCONNU;
      }
    }
    
    // Gestion de la matière si c'est un objet
    if (processedData.matiere && typeof processedData.matiere === 'object') {
      processedData.matiere = MatiereModel.fromData(processedData.matiere as Record<string, unknown>);
    }
    
    // Gestion de l'échéance si c'est une string
    if (processedData.echeance && typeof processedData.echeance === 'string') {
      try {
        processedData.echeance = new Date(processedData.echeance);
      } catch (error) {
        processedData.echeance = new Date();
      }
    }
    
    // On ne passe jamais id, il sera généré automatiquement
    delete processedData.id;
    
    try {
      return new BesoinModel(processedData);
    } catch (error) {
      console.error("Erreur lors de la création du besoin:", error);
      // En dernier recours, créer un besoin avec des valeurs par défaut
      return new BesoinModel({
        matiere: new MatiereModel({ code_mp: "UNKNOWN", nom: "Matière inconnue" }),
        quantite: 0,
        echeance: new Date(),
        etat: Etat.INCONNU,
        lot: ""
      });
    }
  }

  toData(): Record<string, unknown> {
    return {
      id: this.id,
      matiere: this.matiere instanceof MatiereModel ? this.matiere.toData() : this.matiere,
      quantite: this.quantite,
      echeance: this.echeance.toISOString(),
      etat: this.etat,
      lot: this.lot
    };
  }
} 