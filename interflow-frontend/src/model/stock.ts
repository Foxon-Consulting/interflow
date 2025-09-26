import { Matiere, MatiereModel } from './matiere';

export interface Stock {
  id?: string;
  article: string; // Clé primaire
  libelle_article: string;
  du: string;
  quantite: number;
  udm: string;
  statut_lot: string;
  division: string;
  magasin: string; // Clé primaire
  emplacement: string; // Clé primaire
  contenant: string; // Clé primaire
  statut_proprete: string;
  reutilisable: string;
  statut_contenant: string;
  classification?: string | null;
  restriction?: string | null;
  lot_fournisseur?: string | null;
  capacite?: string | null;
  commentaire?: string | null;
  date_creation?: Date | null;
  dluo?: Date | null;
  matiere?: Matiere | null;
}

export class StockModel implements Stock {
  id?: string;
  article: string;
  libelle_article: string;
  du: string;
  quantite: number;
  udm: string;
  statut_lot: string;
  division: string;
  magasin: string;
  emplacement: string;
  contenant: string;
  statut_proprete: string;
  reutilisable: string;
  statut_contenant: string;
  classification?: string | null;
  restriction?: string | null;
  lot_fournisseur?: string | null;
  capacite?: string | null;
  commentaire?: string | null;
  date_creation?: Date | null;
  dluo?: Date | null;
  matiere?: Matiere | null;

  constructor(data: Partial<Stock>) {
    this.article = data.article || "";
    this.libelle_article = data.libelle_article || "";
    this.du = data.du || "";
    this.quantite = data.quantite || 0;
    this.udm = data.udm || "";
    this.statut_lot = data.statut_lot || "";
    this.division = data.division || "";
    this.magasin = data.magasin || "";
    this.emplacement = data.emplacement || "";
    this.contenant = data.contenant || "";
    this.statut_proprete = data.statut_proprete || "";
    this.reutilisable = data.reutilisable || "";
    this.statut_contenant = data.statut_contenant || "";
    this.classification = data.classification || null;
    this.restriction = data.restriction || null;
    this.lot_fournisseur = data.lot_fournisseur || null;
    this.capacite = data.capacite || null;
    this.commentaire = data.commentaire || null;
    this.date_creation = data.date_creation || null;
    this.dluo = data.dluo || null;
    
    // La matière sera initialisée si nécessaire
    if (!data.matiere) {
      // Créer une matière temporaire avec le libellé
      this.matiere = new MatiereModel({ code_mp: "TOBEDEFINED", nom: this.libelle_article });
    } else {
      this.matiere = data.matiere;
    }
    
    // Générer une clé primaire composite basée sur le tuple unique
    this.id = `${this.article}_${this.magasin}_${this.emplacement}_${this.contenant}`;
  }

  static fromData(data: Record<string, unknown>): StockModel {
    const processedData = { ...data };
    
    // Gestion des dates
    if (processedData.date_creation && typeof processedData.date_creation === 'string') {
      try {
        processedData.date_creation = new Date(processedData.date_creation);
      } catch {
        processedData.date_creation = null;
      }
    }
    
    if (processedData.dluo && typeof processedData.dluo === 'string') {
      try {
        processedData.dluo = new Date(processedData.dluo);
      } catch {
        processedData.dluo = null;
      }
    }
    
    // Gestion de la matière
    if (processedData.matiere && typeof processedData.matiere === 'object') {
      processedData.matiere = MatiereModel.fromData(processedData.matiere as Record<string, unknown>);
    }
    
    return new StockModel(processedData);
  }

  toData(): Record<string, unknown> {
    return {
      id: this.id,
      article: this.article,
      libelle_article: this.libelle_article,
      du: this.du,
      quantite: this.quantite,
      udm: this.udm,
      statut_lot: this.statut_lot,
      division: this.division,
      magasin: this.magasin,
      emplacement: this.emplacement,
      contenant: this.contenant,
      statut_proprete: this.statut_proprete,
      reutilisable: this.reutilisable,
      statut_contenant: this.statut_contenant,
      classification: this.classification,
      restriction: this.restriction,
      lot_fournisseur: this.lot_fournisseur,
      capacite: this.capacite,
      commentaire: this.commentaire,
      date_creation: this.date_creation?.toISOString() || null,
      dluo: this.dluo?.toISOString() || null,
      matiere: this.matiere instanceof MatiereModel ? this.matiere.toData() : this.matiere
    };
  }
} 