import { MatiereModel, Matiere } from "@/model/matiere";

/**
 * Service pour gérer les opérations liées aux matières
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

// Fonction pour récupérer toutes les matières
export async function fetchAllMatiereData(): Promise<MatiereModel[]> {
  // Suppression du log d'appel superflu
  // console.log("📡 [MATIERE-SERVICE] fetchAllMatiereData appelé");
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.MATIERES}`);
    const data = await handleApiResponse(response);
    
    // Suppression du log de données récupérées
    // console.log("✅ [MATIERE-SERVICE] Données récupérées:", data);
    
    // Gérer le format de réponse de l'API
    let matieresData: Record<string, unknown>[] = [];
    if (data.matieres) {
      matieresData = data.matieres;
    } else if (Array.isArray(data.data)) {
      matieresData = data.data;
    } else if (Array.isArray(data)) {
      matieresData = data;
    }
    
    // Validation et nettoyage des données
    if (!Array.isArray(matieresData)) {
      // Suppression du log d'avertissement
      // console.warn("⚠️ [MATIERE-SERVICE] Données non valides ou réponse vide, retour d'une liste vide");
      return [];
    }
    
    // Filtrer les objets vides ou invalides
    const validMatieresData = matieresData.filter((item: Record<string, unknown>) => {
      if (!item || typeof item !== 'object') {
        // Suppression du log d'item invalide
        // console.warn("⚠️ [MATIERE-SERVICE] Item invalide ignoré:", item);
        return false;
      }
      return true;
    });
    
    const matiereModels = validMatieresData.map((item: Record<string, unknown>) => {
      // Suppression du log de traitement d'item
      // console.log("🔍 [MATIERE-SERVICE] Traitement item:", item);
      
      return MatiereModel.fromData(item);
    });
    
    // Suppression du log de succès
    // console.log(`✅ [MATIERE-SERVICE] ${matiereModels.length} matières traitées avec succès`);
    return matiereModels;
    
  } catch (error) {
    console.error("❌ [MATIERE-SERVICE] Erreur lors de la récupération des matières:", error);
    // En cas d'erreur, retourner une liste vide plutôt que de faire planter l'application
    return [];
  }
}

// Fonction pour récupérer une matière par code
export async function fetchMatiereByCode(code_mp: string): Promise<MatiereModel | undefined> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [MATIERE-SERVICE] fetchMatiereByCode appelé pour code: ${code_mp}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.MATIERES}/${code_mp}`);
    const data = await handleApiResponse(response);
    
    const item = data.data || data;
    
    if (!item) {
      return undefined;
    }
    
    return MatiereModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [MATIERE-SERVICE] Erreur lors de la récupération de la matière ${code_mp}:`, error);
    return undefined;
  }
}

// Fonction pour créer une nouvelle matière
export async function createMatiere(newMatiere: Omit<Matiere, 'id'>): Promise<MatiereModel> {
  // Suppression du log d'appel superflu
  // console.log("📡 [MATIERE-SERVICE] createMatiere appelé");
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.MATIERES}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code_mp: newMatiere.code_mp,
        nom_matiere: newMatiere.nom
      })
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return MatiereModel.fromData(item);
    
  } catch (error) {
    console.error("❌ [MATIERE-SERVICE] Erreur lors de la création de la matière:", error);
    throw error;
  }
}

// Fonction pour mettre à jour une matière
export async function updateMatiere(code_mp: string, matiereData: Partial<Matiere>): Promise<MatiereModel | null> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [MATIERE-SERVICE] updateMatiere appelé pour code: ${code_mp}`);
  
  try {
    const updateData: Record<string, unknown> = {};
    
    if (matiereData.code_mp !== undefined) {
      updateData.code_mp = matiereData.code_mp;
    }
    
    if (matiereData.nom !== undefined) {
      updateData.nom_matiere = matiereData.nom;
    }
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.MATIERES}/${encodeURIComponent(code_mp)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData)
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return MatiereModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [MATIERE-SERVICE] Erreur lors de la mise à jour de la matière ${code_mp}:`, error);
    return null;
  }
}

// Fonction pour supprimer une matière
export async function deleteMatiere(code_mp: string): Promise<boolean> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [MATIERE-SERVICE] deleteMatiere appelé pour code: ${code_mp}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.MATIERES}/${encodeURIComponent(code_mp)}`, {
      method: 'DELETE'
    });
    
    await handleApiResponse(response);
    // Suppression du log de succès
    // console.log(`✅ [MATIERE-SERVICE] Matière ${code_mp} supprimée avec succès`);
    return true;
    
  } catch (error) {
    console.error(`❌ [MATIERE-SERVICE] Erreur lors de la suppression de la matière ${code_mp}:`, error);
    return false;
  }
}

// Fonction pour vider toutes les matières
export async function flushMatieres(): Promise<void> {
  // Suppression du log d'appel superflu
  // console.log("📡 [MATIERE-SERVICE] flushMatieres appelé");
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.MATIERES}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });
    await handleApiResponse(response);
  } catch (error) {
    console.error("❌ [MATIERE-SERVICE] Erreur lors du vidage des matières:", error);
    throw error;
  }
}

// Fonction pour rechercher des matières par nom
export async function searchMatieresByNom(nom: string): Promise<MatiereModel[]> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [MATIERE-SERVICE] searchMatieresByNom appelé pour nom: ${nom}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.MATIERES}/search?nom=${encodeURIComponent(nom)}`);
    const data = await handleApiResponse(response);
    
    const matieresData = data.matieres || data.data || [];
    if (!Array.isArray(matieresData)) {
      throw new Error("Format de données invalide");
    }
    
    return matieresData.map((item: Record<string, unknown>) => MatiereModel.fromData(item));
    
  } catch (error) {
    console.error(`❌ [MATIERE-SERVICE] Erreur lors de la recherche des matières par nom ${nom}:`, error);
    throw error;
  }
}

// Fonction pour récupérer seulement les matières SEVESO
export async function fetchMatieresSevesoOnly(): Promise<MatiereModel[]> {
  // Suppression du log d'appel superflu
  // console.log("📡 [MATIERE-SERVICE] fetchMatieresSevesoOnly appelé");
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.MATIERES}/seveso`);
    const data = await handleApiResponse(response);
    
    const matieresData = data.matieres || data.data || [];
    if (!Array.isArray(matieresData)) {
      throw new Error("Format de données invalide");
    }
    
    return matieresData.map((item: Record<string, unknown>) => MatiereModel.fromData(item));
    
  } catch (error) {
    console.error("❌ [MATIERE-SERVICE] Erreur lors de la récupération des matières SEVESO:", error);
    throw error;
  }
}

// Fonction pour récupérer les matières par type
export async function fetchMatieresByType(type: 'acide' | 'base' | 'solvant' | 'oxydant' | 'sel'): Promise<MatiereModel[]> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [MATIERE-SERVICE] fetchMatieresByType appelé pour type: ${type}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.MATIERES}/type/${type}`);
    const data = await handleApiResponse(response);
    
    const matieresData = data.matieres || data.data || [];
    if (!Array.isArray(matieresData)) {
      throw new Error("Format de données invalide");
    }
    
    return matieresData.map((item: Record<string, unknown>) => MatiereModel.fromData(item));
    
  } catch (error) {
    console.error(`❌ [MATIERE-SERVICE] Erreur lors de la récupération des matières par type ${type}:`, error);
    throw error;
  }
}

// Import du service d'import généralisé
import { importMatieresFromFile as importMatieresFromFileGeneric, detectFileType } from './import-service';

// Fonction pour importer des matières depuis un fichier CSV ou XLSX
export async function importMatieresFromFile(file: File): Promise<void> {
  // Suppression du log d'appel superflu
  // console.log("📡 [MATIERE-SERVICE] importMatieresFromFile appelé");
  
  try {
    const importType = detectFileType(file);
    const result = await importMatieresFromFileGeneric(file, importType);
    
    if (!result.success) {
      throw new Error(result.message);
    }
    
    // Suppression du log de succès
    // console.log("✅ [MATIERE-SERVICE] Import réussi");
    
  } catch (error) {
    console.error("❌ [MATIERE-SERVICE] Erreur lors de l'import:", error);
    throw error;
  }
}

// Fonction pour télécharger la FDS d'une matière
export async function downloadFDS(code_mp: string): Promise<string> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [MATIERE-SERVICE] downloadFDS appelé pour code: ${code_mp}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.MATIERES}/${encodeURIComponent(code_mp)}/fds`);
    
    if (!response.ok) {
      throw new Error(`Erreur HTTP: ${response.status}`);
    }
    
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    
    // Suppression du log de succès
    // console.log(`✅ [MATIERE-SERVICE] FDS téléchargée avec succès pour ${code_mp}`);
    return url;
    
  } catch (error) {
    console.error(`❌ [MATIERE-SERVICE] Erreur lors du téléchargement de la FDS pour ${code_mp}:`, error);
    throw error;
  }
} 