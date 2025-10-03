export interface ProduitRappatriement {
  prelevement: boolean;
  code_prdt: string;
  designation_prdt: string;
  lot: string;
  poids_net: number;
  type_emballage: string;
  stock_solde: boolean;
  nb_contenants: number;
  nb_palettes: number;
  dimension_palettes: string;
  code_onu: string;
  grp_emballage: string;
  po: string; // Peut être une chaîne vide selon l'API
}

export class ProduitRappatriementModel implements ProduitRappatriement {
  prelevement: boolean;
  code_prdt: string;
  designation_prdt: string;
  lot: string;
  poids_net: number;
  type_emballage: string;
  stock_solde: boolean;
  nb_contenants: number;
  nb_palettes: number;
  dimension_palettes: string;
  code_onu: string;
  grp_emballage: string;
  po: string; // Peut être une chaîne vide selon l'API

  constructor(data: Partial<ProduitRappatriement>) {
    this.prelevement = data.prelevement || false;
    this.code_prdt = data.code_prdt || "";
    this.designation_prdt = data.designation_prdt || "";
    this.lot = data.lot || "";
    this.poids_net = data.poids_net || 0;
    this.type_emballage = data.type_emballage || "";
    this.stock_solde = data.stock_solde || false;
    this.nb_contenants = data.nb_contenants || 0;
    this.nb_palettes = data.nb_palettes || 0;
    this.dimension_palettes = data.dimension_palettes || "";
    this.code_onu = data.code_onu || "";
    this.grp_emballage = data.grp_emballage || "";
    this.po = data.po || "";
  }

  static fromData(data: Record<string, unknown>): ProduitRappatriementModel {
    return new ProduitRappatriementModel(data);
  }

  toData(): Record<string, unknown> {
    return {
      prelevement: this.prelevement,
      code_prdt: this.code_prdt,
      designation_prdt: this.designation_prdt,
      lot: this.lot,
      poids_net: this.poids_net,
      type_emballage: this.type_emballage,
      stock_solde: this.stock_solde,
      nb_contenants: this.nb_contenants,
      nb_palettes: this.nb_palettes,
      dimension_palettes: this.dimension_palettes,
      code_onu: this.code_onu,
      grp_emballage: this.grp_emballage,
      po: this.po
    };
  }
}

export interface Rappatriement {
  numero_transfert: string;
  date_derniere_maj?: Date | null;
  responsable_diffusion: string;
  date_demande?: Date | null;
  date_reception_souhaitee?: Date | null;
  contacts: string; // Peut être une chaîne vide selon l'API
  adresse_destinataire: string;
  adresse_enlevement: string;
  produits: ProduitRappatriement[];
  remarques?: string | null;
}

export class RappatriementModel implements Rappatriement {
  numero_transfert: string;
  date_derniere_maj?: Date | null;
  responsable_diffusion: string;
  date_demande?: Date | null;
  date_reception_souhaitee?: Date | null;
  contacts: string; // Peut être une chaîne vide selon l'API
  adresse_destinataire: string;
  adresse_enlevement: string;
  produits: ProduitRappatriement[];
  remarques?: string | null;

  constructor(data: Partial<Rappatriement>) {
    this.numero_transfert = data.numero_transfert || "";
    this.date_derniere_maj = data.date_derniere_maj || null;
    this.responsable_diffusion = data.responsable_diffusion || "";
    this.date_demande = data.date_demande || null;
    this.date_reception_souhaitee = data.date_reception_souhaitee || null;
    this.contacts = data.contacts || "";
    this.adresse_destinataire = data.adresse_destinataire || "";
    this.adresse_enlevement = data.adresse_enlevement || "";
    this.produits = data.produits || [];
    this.remarques = data.remarques || null;
  }

  static fromData(data: Record<string, unknown>): RappatriementModel {
    const processedData = { ...data };
    
    // Gestion des dates
    if (processedData.date_derniere_maj && typeof processedData.date_derniere_maj === 'string') {
      try {
        processedData.date_derniere_maj = new Date(processedData.date_derniere_maj);
      } catch {
        processedData.date_derniere_maj = null;
      }
    }
    
    if (processedData.date_demande && typeof processedData.date_demande === 'string') {
      try {
        processedData.date_demande = new Date(processedData.date_demande);
      } catch {
        processedData.date_demande = null;
      }
    }
    
    if (processedData.date_reception_souhaitee && typeof processedData.date_reception_souhaitee === 'string') {
      try {
        processedData.date_reception_souhaitee = new Date(processedData.date_reception_souhaitee);
      } catch {
        processedData.date_reception_souhaitee = null;
      }
    }
    
    // Gestion des produits
    if (processedData.produits && Array.isArray(processedData.produits)) {
      processedData.produits = processedData.produits.map(
        (produitData: unknown) => ProduitRappatriementModel.fromData(produitData as Record<string, unknown>)
      );
    }
    
    return new RappatriementModel(processedData);
  }

  toData(): Record<string, unknown> {
    return {
      numero_transfert: this.numero_transfert,
      date_derniere_maj: this.date_derniere_maj?.toISOString() || null,
      responsable_diffusion: this.responsable_diffusion,
      date_demande: this.date_demande?.toISOString() || null,
      date_reception_souhaitee: this.date_reception_souhaitee?.toISOString() || null,
      contacts: this.contacts,
      adresse_destinataire: this.adresse_destinataire,
      adresse_enlevement: this.adresse_enlevement,
      produits: this.produits.map(produit => 
        produit instanceof ProduitRappatriementModel ? produit.toData() : produit
      ),
      remarques: this.remarques
    };
  }

  // Méthodes utilitaires
  ajouterProduit(produit: ProduitRappatriement): void {
    this.produits.push(produit);
  }

  calculerPoidsTotal(): number {
    return this.produits.reduce((total, produit) => total + produit.poids_net, 0);
  }

  calculerNbPalettesTotal(): number {
    return this.produits.reduce((total, produit) => total + produit.nb_palettes, 0);
  }

  calculerNbContenantsTotal(): number {
    return this.produits.reduce((total, produit) => total + produit.nb_contenants, 0);
  }
} 