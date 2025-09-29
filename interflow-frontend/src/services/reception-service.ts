import { ReceptionModel, Reception, TypeReception, EtatReception } from "@/model/reception";

/**
 * Service pour gérer les opérations liées aux réceptions
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

// Fonction pour récupérer toutes les réceptions
export async function fetchAllReceptionData(): Promise<ReceptionModel[]> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RECEPTIONS}`);
    const data = await handleApiResponse(response);
    
    // Gérer le format de réponse de l'API
    let receptionsData: Record<string, unknown>[] = [];
    if (data.receptions) {
      receptionsData = data.receptions;
    } else if (Array.isArray(data.data)) {
      receptionsData = data.data;
    } else if (Array.isArray(data)) {
      receptionsData = data;
    }
    
    // Validation et nettoyage des données
    if (!Array.isArray(receptionsData)) {
      return [];
    }
    
    // Filtrer les objets vides ou invalides
    const validReceptionsData = receptionsData.filter((item: Record<string, unknown>) => {
      if (!item || typeof item !== 'object') {
        return false;
      }
      return true;
    });
    
    const receptionModels = validReceptionsData.map((item: Record<string, unknown>) => {
      return ReceptionModel.fromData(item);
    });
    
    return receptionModels;
    
  } catch (error) {
    console.error("❌ [RECEPTION-SERVICE] Erreur lors de la récupération des réceptions:", error);
    // En cas d'erreur, retourner une liste vide plutôt que de faire planter l'application
    return [];
  }
}

// Fonction pour récupérer une réception par ID
export async function fetchReceptionById(id: string): Promise<ReceptionModel | undefined> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RECEPTIONS}/${id}`);
    const data = await handleApiResponse(response);
    
    const item = data.data || data;
    
    if (!item) {
      return undefined;
    }
    
    return ReceptionModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [RECEPTION-SERVICE] Erreur lors de la récupération de la réception ${id}:`, error);
    return undefined;
  }
}

// Fonction pour créer une nouvelle réception
export async function createReception(newReception: Omit<Reception, 'id'>): Promise<ReceptionModel> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RECEPTIONS}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        matiere_code: newReception.matiere.code_mp,
        matiere_nom: newReception.matiere.nom,
        quantite: newReception.quantite,
        type: newReception.type,
        date_reception: newReception.date_creation.toISOString(),
        date_livraison_prevue: newReception.date_modification?.toISOString(),
        fournisseur: newReception.fournisseur || "FOURNISSEUR_DEFAUT",
        statut: newReception.etat
      })
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return ReceptionModel.fromData(item);
    
  } catch (error) {
    console.error("❌ [RECEPTION-SERVICE] Erreur lors de la création de la réception:", error);
    throw error;
  }
}

// Fonction pour mettre à jour une réception
export async function updateReception(id: string, receptionData: Partial<Reception>): Promise<ReceptionModel | null> {
  try {
    const updateData: Record<string, unknown> = {};
    
    if (receptionData.matiere) {
      updateData.matiere_code = receptionData.matiere.code_mp;
      updateData.matiere_nom = receptionData.matiere.nom;
    }
    
    if (receptionData.quantite !== undefined) {
      updateData.quantite = receptionData.quantite;
    }
    
    if (receptionData.type !== undefined) {
      updateData.type = receptionData.type;
    }
    
    if (receptionData.date_creation !== undefined) {
      updateData.date_reception = receptionData.date_creation.toISOString();
    }
    
    if (receptionData.date_modification !== undefined && receptionData.date_modification !== null) {
      updateData.date_livraison_prevue = receptionData.date_modification.toISOString();
    }
    
    if (receptionData.fournisseur !== undefined) {
      updateData.fournisseur = receptionData.fournisseur;
    }
    
    if (receptionData.etat !== undefined) {
      updateData.statut = receptionData.etat;
    }
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RECEPTIONS}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData)
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return ReceptionModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [RECEPTION-SERVICE] Erreur lors de la mise à jour de la réception ${id}:`, error);
    return null;
  }
}

// Fonction pour supprimer une réception
export async function deleteReception(id: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RECEPTIONS}/${id}`, {
      method: 'DELETE'
    });
    
    await handleApiResponse(response);
    return true;
    
  } catch (error) {
    console.error(`❌ [RECEPTION-SERVICE] Erreur lors de la suppression de la réception ${id}:`, error);
    return false;
  }
}

// Fonction pour vider toutes les réceptions
export async function flushReceptions(): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RECEPTIONS}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });
    await handleApiResponse(response);
  } catch (error) {
    console.error("❌ [RECEPTION-SERVICE] Erreur lors du vidage des réceptions:", error);
    throw error;
  }
}

// Fonction pour récupérer les réceptions par type
export async function fetchReceptionsByType(type: TypeReception): Promise<ReceptionModel[]> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RECEPTIONS_BY_TYPE}/${type}`);
    const data = await handleApiResponse(response);
    
    const receptionsData = data.receptions || data.data || [];
    if (!Array.isArray(receptionsData)) {
      throw new Error("Format de données invalide");
    }
    
    return receptionsData.map((item: Record<string, unknown>) => ReceptionModel.fromData(item));
    
  } catch (error) {
    console.error(`❌ [RECEPTION-SERVICE] Erreur lors de la récupération des réceptions par type ${type}:`, error);
    throw error;
  }
}

// Fonction pour récupérer les réceptions par état
export async function fetchReceptionsByEtat(etat: EtatReception): Promise<ReceptionModel[]> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RECEPTIONS_BY_ETAT}/${etat}`);
    const data = await handleApiResponse(response);
    
    const receptionsData = data.receptions || data.data || [];
    if (!Array.isArray(receptionsData)) {
      throw new Error("Format de données invalide");
    }
    
    return receptionsData.map((item: Record<string, unknown>) => ReceptionModel.fromData(item));
    
  } catch (error) {
    console.error(`❌ [RECEPTION-SERVICE] Erreur lors de la récupération des réceptions par état ${etat}:`, error);
    throw error;
  }
}

// Fonction pour récupérer les réceptions par matière
export async function fetchReceptionsByMatiere(codeMp: string): Promise<ReceptionModel[]> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.RECEPTIONS_BY_MATIERE}/${encodeURIComponent(codeMp)}`);
    const data = await handleApiResponse(response);
    
    const receptionsData = data.receptions || data.data || [];
    if (!Array.isArray(receptionsData)) {
      throw new Error("Format de données invalide");
    }
    
    return receptionsData.map((item: Record<string, unknown>) => ReceptionModel.fromData(item));
    
  } catch (error) {
    console.error(`❌ [RECEPTION-SERVICE] Erreur lors de la récupération des réceptions par matière ${codeMp}:`, error);
    throw error;
  }
}

// Fonction pour générer un bon de réception
export async function genererBonReception(receptionIds: string[]): Promise<string> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.GENERER_BON_RECEPTION}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reception_ids: receptionIds })
    });
    
    if (!response.ok) {
      throw new Error(`Erreur HTTP: ${response.status}`);
    }
    
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    
    return url;
    
  } catch (error) {
    console.error(`❌ [RECEPTION-SERVICE] Erreur lors de la génération du bon de réception:`, error);
    throw error;
  }
}

// Import du service d'import généralisé
import { importReceptionsFromFile as importReceptionsFromFileGeneric, detectFileType } from './import-service';

// Fonction pour importer des réceptions depuis un fichier CSV ou XLSX
export async function importReceptionsFromFile(file: File): Promise<void> {
  try {
    const importType = detectFileType(file);
    const result = await importReceptionsFromFileGeneric(file, importType);
    
    if (!result.success) {
      throw new Error(result.message);
    }
    
    // L'API retourne des statistiques d'import, pas un tableau de réceptions
    // Les données seront disponibles via fetchAllReceptionData() après l'import
  } catch (error) {
    console.error("❌ [RECEPTION-SERVICE] Erreur lors de l'import:", error);
    throw error;
  }
} 