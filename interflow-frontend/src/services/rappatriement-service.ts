import { RappatriementModel, ProduitRappatriementModel, Rappatriement } from "@/model/rappatriement";

/**
 * Service pour gérer les opérations liées aux rapatriements
 * Utilise les API Routes Next.js pour la communication interne
 */

import { API_BASE_URL, API_ENDPOINTS } from '@/config/api';

// Fonction utilitaire pour gérer les erreurs API
async function handleApiResponse(response: Response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: "Erreur réseau" }));
    throw new Error(errorData.message || `Erreur HTTP: ${response.status}`);
  }
  return response.json();
}

// Fonction pour récupérer tous les rapatriements
export async function fetchAllRappatriementData(): Promise<RappatriementModel[]> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RAPPATRIEMENTS}`);
    const data = await handleApiResponse(response);
    
    // Gérer le format de réponse de l'API
    let rapatriementsData: Record<string, unknown>[] = [];
    if (data.rappatriements) {
      rapatriementsData = data.rappatriements;
    } else if (Array.isArray(data.data)) {
      rapatriementsData = data.data;
    } else if (Array.isArray(data)) {
      rapatriementsData = data;
    }
    
    // Validation et nettoyage des données
    if (!Array.isArray(rapatriementsData)) {
      return [];
    }
    
    // Filtrer les objets vides ou invalides
    const validRappatriementsData = rapatriementsData.filter((item: Record<string, unknown>) => {
      if (!item || typeof item !== 'object') {
        return false;
      }
      return true;
    });
    
    const rapatriementModels = validRappatriementsData.map((item: Record<string, unknown>) => {
      return RappatriementModel.fromData(item);
    });
    
    return rapatriementModels;
    
  } catch (error) {
    console.error("❌ [RAPPATRIEMENT-SERVICE] Erreur lors de la récupération des rapatriements:", error);
    // En cas d'erreur, retourner une liste vide plutôt que de faire planter l'application
    return [];
  }
}

// Fonction pour récupérer un rapatriement par numéro de transfert
export async function fetchRappatriementByNumero(numero_transfert: string): Promise<RappatriementModel | undefined> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RAPPATRIEMENTS}/${numero_transfert}`);
    const data = await handleApiResponse(response);
    
    const item = data.data || data;
    
    if (!item) {
      return undefined;
    }
    
    return RappatriementModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [RAPPATRIEMENT-SERVICE] Erreur lors de la récupération du rapatriement ${numero_transfert}:`, error);
    return undefined;
  }
}

// Fonction pour créer un nouveau rapatriement
export async function createRappatriement(newRappatriement: Omit<Rappatriement, 'numero_transfert'>): Promise<RappatriementModel> {
  try {
    const requestBody = {
      responsable_diffusion: newRappatriement.responsable_diffusion,
      date_demande: newRappatriement.date_demande?.toISOString() || null,
      date_reception_souhaitee: newRappatriement.date_reception_souhaitee?.toISOString() || null,
      contacts: newRappatriement.contacts,
      adresse_destinataire: newRappatriement.adresse_destinataire,
      adresse_enlevement: newRappatriement.adresse_enlevement,
      produits: newRappatriement.produits.map(produit => 
        produit instanceof ProduitRappatriementModel ? produit.toData() : produit
      ),
      remarques: newRappatriement.remarques
    };

    // Log du JSON exact envoyé au backend
    console.log("🔍 [RAPPATRIEMENT-SERVICE] JSON exact envoyé au backend:", JSON.stringify(requestBody, null, 2));

    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RAPPATRIEMENTS}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return RappatriementModel.fromData(item);
    
  } catch (error) {
    console.error("❌ [RAPPATRIEMENT-SERVICE] Erreur lors de la création du rapatriement:", error);
    throw error;
  }
}

// Fonction pour mettre à jour un rapatriement
export async function updateRappatriement(numero_transfert: string, updatedRappatriement: Partial<Rappatriement>): Promise<RappatriementModel> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [RAPPATRIEMENT-SERVICE] updateRappatriement appelé pour numéro: ${numero_transfert}`);
  
  try {
    const updateData: Record<string, unknown> = {};
    
    if (updatedRappatriement.responsable_diffusion !== undefined) {
      updateData.responsable_diffusion = updatedRappatriement.responsable_diffusion;
    }
    
    if (updatedRappatriement.date_demande !== undefined) {
      updateData.date_demande = updatedRappatriement.date_demande?.toISOString() || null;
    }
    
    if (updatedRappatriement.date_reception_souhaitee !== undefined) {
      updateData.date_reception_souhaitee = updatedRappatriement.date_reception_souhaitee?.toISOString() || null;
    }
    
    if (updatedRappatriement.contacts !== undefined) {
      updateData.contacts = updatedRappatriement.contacts;
    }
    
    if (updatedRappatriement.adresse_destinataire !== undefined) {
      updateData.adresse_destinataire = updatedRappatriement.adresse_destinataire;
    }
    
    if (updatedRappatriement.adresse_enlevement !== undefined) {
      updateData.adresse_enlevement = updatedRappatriement.adresse_enlevement;
    }
    
    if (updatedRappatriement.produits !== undefined) {
      updateData.produits = updatedRappatriement.produits.map(produit => 
        produit instanceof ProduitRappatriementModel ? produit.toData() : produit
      );
    }
    
    if (updatedRappatriement.remarques !== undefined) {
      updateData.remarques = updatedRappatriement.remarques;
    }
    
    updateData.date_derniere_maj = new Date().toISOString();
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RAPPATRIEMENTS}/${numero_transfert}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData)
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return RappatriementModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [RAPPATRIEMENT-SERVICE] Erreur lors de la mise à jour du rapatriement ${numero_transfert}:`, error);
    throw error;
  }
}

// Fonction pour supprimer un rapatriement
export async function deleteRappatriement(numero_transfert: string): Promise<void> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [RAPPATRIEMENT-SERVICE] deleteRappatriement appelé pour numéro: ${numero_transfert}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RAPPATRIEMENTS}/${numero_transfert}`, {
      method: 'DELETE'
    });
    
    await handleApiResponse(response);
    // Suppression du log de succès
    // console.log(`✅ [RAPPATRIEMENT-SERVICE] Rapatriement ${numero_transfert} supprimé avec succès`);
  } catch (error) {
    console.error(`❌ [RAPPATRIEMENT-SERVICE] Erreur lors de la suppression du rapatriement ${numero_transfert}:`, error);
    throw error;
  }
}

// Fonction pour vider tous les rapatriements
export async function flushRappatriements(): Promise<void> {
  // Suppression du log d'appel superflu
  // console.log("📡 [RAPPATRIEMENT-SERVICE] flushRappatriements appelé");
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RAPPATRIEMENTS}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });
    await handleApiResponse(response);
  } catch (error) {
    console.error("❌ [RAPPATRIEMENT-SERVICE] Erreur lors du vidage des rapatriements:", error);
    throw error;
  }
}

// Fonction pour récupérer les rapatriements en cours
export async function fetchRappatriementsEnCours(): Promise<RappatriementModel[]> {
  // Suppression du log d'appel superflu
  // console.log("📡 [RAPPATRIEMENT-SERVICE] fetchRappatriementsEnCours appelé");
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RAPPATRIEMENTS_EN_COURS}`);
    const data = await handleApiResponse(response);
    
    let rapatriementsData: Record<string, unknown>[] = [];
    if (data.rappatriements) {
      rapatriementsData = data.rappatriements;
    } else if (Array.isArray(data.data)) {
      rapatriementsData = data.data;
    } else if (Array.isArray(data)) {
      rapatriementsData = data;
    }
    
    if (!Array.isArray(rapatriementsData)) {
      // console.warn("⚠️ [RAPPATRIEMENT-SERVICE] Données non valides pour les rapatriements en cours");
      return [];
    }
    
    const rapatriementModels = rapatriementsData.map((item: Record<string, unknown>) => {
      return RappatriementModel.fromData(item);
    });
    
    // console.log(`✅ [RAPPATRIEMENT-SERVICE] ${rapatriementModels.length} rapatriements en cours traités avec succès`);
    return rapatriementModels;
    
  } catch (error) {
    console.error("❌ [RAPPATRIEMENT-SERVICE] Erreur lors de la récupération des rapatriements en cours:", error);
    return [];
  }
}

// Fonction pour ajouter un produit à un rapatriement
export async function ajouterProduitRappatriement(
  numero_transfert: string, 
  produit: Omit<ProduitRappatriementModel, 'prelevement'>
): Promise<RappatriementModel> {
      // console.log(`📡 [RAPPATRIEMENT-SERVICE] ajouterProduitRappatriement appelé pour numéro: ${numero_transfert}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RAPPATRIEMENTS}/${numero_transfert}/produits`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code_prdt: produit.code_prdt,
        designation_prdt: produit.designation_prdt,
        lot: produit.lot,
        poids_net: produit.poids_net,
        type_emballage: produit.type_emballage,
        stock_solde: produit.stock_solde,
        nb_contenants: produit.nb_contenants,
        nb_palettes: produit.nb_palettes,
        dimension_palettes: produit.dimension_palettes,
        code_onu: produit.code_onu,
        grp_emballage: produit.grp_emballage,
        po: produit.po
      })
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return RappatriementModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [RAPPATRIEMENT-SERVICE] Erreur lors de l'ajout du produit au rapatriement ${numero_transfert}:`, error);
    throw error;
  }
}

// Fonction pour supprimer un produit d'un rapatriement
export async function supprimerProduitRappatriement(
  numero_transfert: string, 
  code_prdt: string, 
  lot: string
): Promise<RappatriementModel> {
      // console.log(`📡 [RAPPATRIEMENT-SERVICE] supprimerProduitRappatriement appelé pour numéro: ${numero_transfert}, produit: ${code_prdt}, lot: ${lot}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RAPPATRIEMENTS}/${numero_transfert}/produits`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code_prdt: code_prdt,
        lot: lot
      })
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return RappatriementModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [RAPPATRIEMENT-SERVICE] Erreur lors de la suppression du produit du rapatriement ${numero_transfert}:`, error);
    throw error;
  }
}

// Fonction pour marquer un produit comme prélevé
export async function marquerProduitPreleve(
  numero_transfert: string, 
  code_prdt: string, 
  lot: string, 
  prelevement: boolean
): Promise<RappatriementModel> {
      // console.log(`📡 [RAPPATRIEMENT-SERVICE] marquerProduitPreleve appelé pour numéro: ${numero_transfert}, produit: ${code_prdt}, lot: ${lot}, prélevé: ${prelevement}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RAPPATRIEMENTS}/${numero_transfert}/produits/prelevement`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code_prdt: code_prdt,
        lot: lot,
        prelevement: prelevement
      })
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return RappatriementModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [RAPPATRIEMENT-SERVICE] Erreur lors du marquage du produit comme prélevé:`, error);
    throw error;
  }
}

// Fonction pour calculer les statistiques d'un rapatriement
export function calculerStatistiquesRappatriement(rapatriement: RappatriementModel): {
  poids_total: number;
  nb_palettes_total: number;
  nb_contenants_total: number;
  nb_produits_preleves: number;
  nb_produits_total: number;
} {
  const poids_total = rapatriement.calculerPoidsTotal();
  const nb_palettes_total = rapatriement.calculerNbPalettesTotal();
  const nb_contenants_total = rapatriement.calculerNbContenantsTotal();
  const nb_produits_preleves = rapatriement.produits.filter(p => p.prelevement).length;
  const nb_produits_total = rapatriement.produits.length;
  
  return {
    poids_total,
    nb_palettes_total,
    nb_contenants_total,
    nb_produits_preleves,
    nb_produits_total
  };
}

// Import du service d'import généralisé
import { importRappatriementsFromFile as importRappatriementsFromFileGeneric, detectFileType } from './import-service';

// Fonction pour importer des rapatriements depuis un fichier CSV ou XLSX
export async function importRappatriementsFromFile(file: File): Promise<void> {
      // console.log("📡 [RAPPATRIEMENT-SERVICE] importRappatriementsFromFile appelé");
  
  try {
    const importType = detectFileType(file);
    const result = await importRappatriementsFromFileGeneric(file, importType);
    
    if (!result.success) {
      throw new Error(result.message);
    }
    
    // L'API retourne des statistiques d'import, pas un tableau de rapatriements
    // console.log("✅ [RAPPATRIEMENT-SERVICE] Import réussi:", result.data);
    
    // Retourner void car l'import est traité par l'API
    // Les données seront disponibles via fetchAllRappatriementData() après l'import
  } catch (error) {
    console.error("❌ [RAPPATRIEMENT-SERVICE] Erreur lors de l'import:", error);
    throw error;
  }
}
