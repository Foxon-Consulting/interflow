import { BesoinModel, Besoin } from "@/model/besoin";
import { MatiereModel } from "@/model/matiere";

/**
 * Service pour gérer les opérations liées aux besoins
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

// Fonction pour récupérer tous les besoins
export async function fetchAllBesoinData(): Promise<BesoinModel[]> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.BESOINS}`);
    
    const data = await handleApiResponse(response);
    
    // Gérer le format de réponse de l'API
    let besoinsData: Record<string, unknown>[] = [];
    if (data.besoins) {
      besoinsData = data.besoins;
    } else {
    }
    
    // Validation et nettoyage des données
    if (!Array.isArray(besoinsData)) {
      return [];
    }
    
    // Filtrer les objets vides ou invalides
    const validBesoinsData = besoinsData.filter((item: Record<string, unknown>) => {
      if (!item || typeof item !== 'object') {
        return false;
      }
      return true;
    });
    
    const besoinModels = validBesoinsData.map((item: Record<string, unknown>) => {
      
      return BesoinModel.fromData(item);
    });
    
    return besoinModels;
    
  } catch (error) {
    console.error("❌ [BESOIN-SERVICE] Erreur lors de la récupération des besoins:", error);
    // En cas d'erreur, retourner une liste vide plutôt que de faire planter l'application
    return [];
  }
}

// Fonction pour récupérer un besoin par ID
export async function fetchBesoinById(id: string): Promise<BesoinModel | undefined> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.BESOINS}/${id}`);
    const data = await handleApiResponse(response);
    
    const item = data.data || data;
    
    if (!item) {
      return undefined;
    }
    
    return BesoinModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [BESOIN-SERVICE] Erreur lors de la récupération du besoin ${id}:`, error);
    return undefined;
  }
}

export async function flushBesoins(): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.BESOINS}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });
    await handleApiResponse(response);
  } catch (error) {
    console.error("❌ [BESOIN-SERVICE] Erreur lors du vidage des besoins:", error);
    throw error;
  }
}

// Fonction pour créer un nouveau besoin
export async function createBesoin(newBesoin: Omit<Besoin, 'id'>): Promise<BesoinModel> {
  // console.log("📡 [BESOIN-SERVICE] createBesoin appelé");
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.BESOINS}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        matiere: newBesoin.matiere instanceof MatiereModel ? newBesoin.matiere.toData() : newBesoin.matiere,
        quantite: newBesoin.quantite,
        echeance: newBesoin.echeance.toISOString(),
        etat: newBesoin.etat,
        lot: newBesoin.lot
      })
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return BesoinModel.fromData(item);
    
  } catch (error) {
    console.error("❌ [BESOIN-SERVICE] Erreur lors de la création du besoin:", error);
    throw error;
  }
}

// Fonction pour mettre à jour un besoin
export async function updateBesoin(id: string, updatedBesoin: Partial<Besoin>): Promise<BesoinModel> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [BESOIN-SERVICE] updateBesoin appelé pour ID: ${id}`);
  
  try {
    const updateData: Record<string, unknown> = {};
    
    if (updatedBesoin.matiere) {
      updateData.matiere = updatedBesoin.matiere instanceof MatiereModel ? updatedBesoin.matiere.toData() : updatedBesoin.matiere;
    }
    
    if (updatedBesoin.quantite !== undefined) {
      updateData.quantite = updatedBesoin.quantite;
    }
    
    if (updatedBesoin.echeance) {
      updateData.echeance = updatedBesoin.echeance.toISOString();
    }
    
    if (updatedBesoin.etat !== undefined) {
      updateData.etat = updatedBesoin.etat;
    }
    
    if (updatedBesoin.lot !== undefined) {
      updateData.lot = updatedBesoin.lot;
    }
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.BESOINS}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData)
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return BesoinModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [BESOIN-SERVICE] Erreur lors de la mise à jour du besoin ${id}:`, error);
    throw error;
  }
}

// Fonction pour supprimer un besoin
export async function deleteBesoin(id: string): Promise<void> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [BESOIN-SERVICE] deleteBesoin appelé pour ID: ${id}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.BESOINS}/${id}`, {
      method: 'DELETE'
    });
    
    await handleApiResponse(response);
    // Suppression du log de succès
    // console.log(`✅ [BESOIN-SERVICE] Besoin ${id} supprimé avec succès`);
  } catch (error) {
    console.error(`❌ [BESOIN-SERVICE] Erreur lors de la suppression du besoin ${id}:`, error);
    throw error;
  }
}

// Import du service d'import généralisé
import { importBesoinsFromFile as importBesoinsFromFileGeneric, detectFileType } from './import-service';

// Fonction pour importer des besoins depuis un fichier CSV ou XLSX
export async function importBesoinsFromFile(file: File): Promise<void> {
  // Suppression du log d'appel superflu
  // console.log("📡 [BESOIN-SERVICE] importBesoinsFromFile appelé");
  
  try {
    const importType = detectFileType(file);
    const result = await importBesoinsFromFileGeneric(file, importType);
    
    if (!result.success) {
      throw new Error(result.message);
     }
    
    // L'API retourne des statistiques d'import, pas un tableau de besoins
    // Suppression du log de succès
    // console.log("✅ [BESOIN-SERVICE] Import réussi:", result.data);
    
    // Retourner void car l'import est traité par l'API
    // Les données seront disponibles via fetchAllBesoinData() après l'import
  } catch (error) {
    console.error("❌ [BESOIN-SERVICE] Erreur lors de l'import:", error);
    throw error;
  }
} 

 