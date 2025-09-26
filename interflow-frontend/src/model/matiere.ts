export interface Matiere {
  code_mp: string;
  nom: string;
  description?: string | null;
  fds?: string | null;
  seveso?: boolean | null;
  internal_reference?: string | null;
}

export class MatiereModel implements Matiere {
  code_mp: string;
  nom: string;
  description?: string | null;
  fds?: string | null;
  seveso?: boolean | null;
  internal_reference?: string | null;

  constructor(data: Partial<Matiere>) {
    this.code_mp = data.code_mp || "UNKNOWN";
    this.nom = data.nom || "Matière inconnue";
    this.description = data.description || null;
    this.fds = data.fds || null;
    this.seveso = data.seveso || null;
    this.internal_reference = data.internal_reference || null;
  }

  static fromData(data: Record<string, unknown>): MatiereModel {
    const processedData = { ...data };
    
    // Valeurs par défaut pour les champs obligatoires manquants
    if (!processedData.code_mp) {
      processedData.code_mp = "UNKNOWN";
    }
    
    if (!processedData.nom) {
      processedData.nom = "Matière inconnue";
    }
    
    try {
      return new MatiereModel(processedData);
    } catch (error) {
      console.error("Erreur lors de la création de la matière:", error);
      // En dernier recours, créer une matière avec des valeurs par défaut
      return new MatiereModel({
        code_mp: "UNKNOWN",
        nom: "Matière inconnue"
      });
    }
  }

  toData(): Record<string, unknown> {
    return {
      code_mp: this.code_mp,
      nom: this.nom,
      description: this.description,
      fds: this.fds,
      seveso: this.seveso,
      internal_reference: this.internal_reference
    };
  }
} 