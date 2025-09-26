import { StockModel, Stock } from "@/model/stock";

/**
 * Service pour gérer les opérations liées aux stocks
 * Connecté au backend FastAPI sur localhost:5000
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

// Fonction pour récupérer tous les stocks
export async function fetchAllStockData(): Promise<StockModel[]> {
  // Suppression du log d'appel superflu
  // console.log("📡 [STOCK-SERVICE] fetchAllStockData appelé");
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.STOCKS}`);
    const data = await handleApiResponse(response);
    
    // Suppression du log de données récupérées
    // console.log("✅ [STOCK-SERVICE] Données récupérées:", data);
    
    // Gérer le format de réponse spécifique du backend
    let stocksData: Record<string, unknown>[] = [];
    if (data.stocks) {
      stocksData = data.stocks;
    } else if (Array.isArray(data.data)) {
      stocksData = data.data;
    } else if (Array.isArray(data)) {
      stocksData = data;
    }
    
    // Validation et nettoyage des données
    if (!Array.isArray(stocksData)) {
      // Suppression du log d'avertissement
      // console.warn("⚠️ [STOCK-SERVICE] Données non valides ou réponse vide, retour d'une liste vide");
      return [];
    }
    
    // Filtrer les objets vides ou invalides
    const validStocksData = stocksData.filter((item: Record<string, unknown>) => {
      if (!item || typeof item !== 'object') {
        // Suppression du log d'item invalide
        // console.warn("⚠️ [STOCK-SERVICE] Item invalide ignoré:", item);
        return false;
      }
      return true;
    });
    
    const stockModels = validStocksData.map((item: Record<string, unknown>) => {
      // Suppression du log de traitement d'item
      // console.log("🔍 [STOCK-SERVICE] Traitement item:", item);
      
      return StockModel.fromData(item);
    });
    
    // Suppression du log de succès
    // console.log(`✅ [STOCK-SERVICE] ${stockModels.length} stocks traités avec succès`);
    return stockModels;
    
  } catch (error) {
    console.error("❌ [STOCK-SERVICE] Erreur lors de la récupération des stocks:", error);
    // En cas d'erreur, retourner une liste vide plutôt que de faire planter l'application
    return [];
  }
}

// Fonction pour récupérer un stock par ID
export async function fetchStockById(id: string): Promise<StockModel | undefined> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [STOCK-SERVICE] fetchStockById appelé pour ID: ${id}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.STOCKS}/${id}`);
    const data = await handleApiResponse(response);
    
    const item = data.data || data;
    
    if (!item) {
      return undefined;
    }
    
    return StockModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [STOCK-SERVICE] Erreur lors de la récupération du stock ${id}:`, error);
    return undefined;
  }
}

// Fonction pour créer un nouveau stock
export async function createStock(newStock: Omit<Stock, 'id'>): Promise<StockModel> {
  // Suppression du log d'appel superflu
  // console.log("📡 [STOCK-SERVICE] createStock appelé");
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.STOCKS}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        article: newStock.emplacement,
        libelle_article: newStock.matiere?.nom || "Matière inconnue",
        du: newStock.du,
        quantite: newStock.quantite,
        udm: newStock.udm,
        statut_lot: newStock.statut_lot,
        division: newStock.division,
        magasin: newStock.magasin,
        emplacement: newStock.emplacement,
        contenant: newStock.contenant,
        statut_proprete: newStock.statut_proprete,
        reutilisable: newStock.reutilisable,
        statut_contenant: newStock.statut_contenant,
        classification: newStock.classification || "STANDARD",
        restriction: newStock.restriction || "AUCUNE",
        lot_fournisseur: newStock.lot_fournisseur || "LOT001",
        capacite: newStock.capacite || "100",
        commentaire: newStock.commentaire || `Stock ${newStock.emplacement}`,
        date_creation: newStock.date_creation ? new Date(newStock.date_creation).toISOString() : new Date().toISOString(),
        dluo: newStock.dluo ? new Date(newStock.dluo).toISOString() : null,
        matiere: newStock.matiere ? {
          code_mp: newStock.matiere.code_mp || "UNKNOWN",
          nom: newStock.matiere.nom || "Matière inconnue",
          description: newStock.matiere.description,
          seveso: newStock.matiere.seveso,
          fds: newStock.matiere.fds,
          internal_reference: newStock.matiere.internal_reference
        } : null
      })
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return StockModel.fromData(item);
    
  } catch (error) {
    console.error("❌ [STOCK-SERVICE] Erreur lors de la création du stock:", error);
    throw error;
  }
}

// Fonction pour mettre à jour un stock
export async function updateStock(id: string, updatedStock: Partial<Stock>): Promise<StockModel> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [STOCK-SERVICE] updateStock appelé pour ID: ${id}`);
  
  try {
    const updateData: Record<string, unknown> = {};
    
    if (updatedStock.matiere) {
      updateData.matiere_code = updatedStock.matiere.code_mp;
      updateData.matiere_nom = updatedStock.matiere.nom;
    }
    
    if (updatedStock.quantite !== undefined) {
      updateData.quantite = updatedStock.quantite;
    }
    
    if (updatedStock.emplacement !== undefined) {
      updateData.emplacement = updatedStock.emplacement;
      updateData.type = updatedStock.emplacement.includes("EXTERNE") ? "externe" : "interne";
    }
    
    updateData.derniere_maj = new Date().toISOString();
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.STOCKS}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData)
    });
    
    const data = await handleApiResponse(response);
    const item = data.data || data;
    
    return StockModel.fromData(item);
    
  } catch (error) {
    console.error(`❌ [STOCK-SERVICE] Erreur lors de la mise à jour du stock ${id}:`, error);
    throw error;
  }
}

// Fonction pour supprimer un stock
export async function deleteStock(id: string): Promise<void> {
  // Suppression du log d'appel superflu
  // console.log(`📡 [STOCK-SERVICE] deleteStock appelé pour ID: ${id}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.STOCKS}/${id}`, {
      method: 'DELETE'
    });
    
    await handleApiResponse(response);
    // Suppression du log de succès
    // console.log(`✅ [STOCK-SERVICE] Stock ${id} supprimé avec succès`);
  } catch (error) {
    console.error(`❌ [STOCK-SERVICE] Erreur lors de la suppression du stock ${id}:`, error);
    throw error;
  }
}

// Fonction pour vider tous les stocks
export async function flushStocks(): Promise<void> {
  // Suppression du log d'appel superflu
  // console.log("📡 [STOCK-SERVICE] flushStocks appelé");
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.STOCKS}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });
    await handleApiResponse(response);
  } catch (error) {
    console.error("❌ [STOCK-SERVICE] Erreur lors du vidage des stocks:", error);
    throw error;
  }
}

// Import du service d'import généralisé
import { importStocksFromFile as importStocksFromFileGeneric, detectFileType } from './import-service';

// Fonction pour importer des stocks depuis un fichier CSV ou XLSX
export async function importStocksFromFile(file: File): Promise<void> {
  // Suppression du log d'appel superflu
  // console.log("📡 [STOCK-SERVICE] importStocksFromFile appelé");
  
  try {
    const importType = detectFileType(file);
    const result = await importStocksFromFileGeneric(file, importType);
    
    if (!result.success) {
      throw new Error(result.message);
    }
    
    // L'API retourne des statistiques d'import, pas un tableau de stocks
    // Suppression du log de succès
    // console.log("✅ [STOCK-SERVICE] Import réussi:", result.data);
    
    // Retourner void car l'import est traité par l'API
    // Les données seront disponibles via fetchAllStockData() après l'import
  } catch (error) {
    console.error("❌ [STOCK-SERVICE] Erreur lors de l'import:", error);
    throw error;
  }
}

// Fonction pour récupérer les stocks internes
export async function fetchInternalStockData(): Promise<StockModel[]> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.STOCKS}/internal`);
    const data = await handleApiResponse(response);
    const stocksData = data.stocks || data.data || [];
    if (!Array.isArray(stocksData)) {
      throw new Error("Format de données invalide pour les stocks internes");
    }
    return stocksData.map((item: Record<string, unknown>) => StockModel.fromData(item));
  } catch (error) {
    console.error("❌ [STOCK-SERVICE] Erreur lors de la récupération des stocks internes:", error);
    return [];
  }
}

// Fonction pour récupérer les stocks externes
export async function fetchExternalStockData(): Promise<StockModel[]> {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.STOCKS}/external`);
    const data = await handleApiResponse(response);
    const stocksData = data.stocks || data.data || [];
    if (!Array.isArray(stocksData)) {
      throw new Error("Format de données invalide pour les stocks externes");
    }
    return stocksData.map((item: Record<string, unknown>) => StockModel.fromData(item));
  } catch (error) {
    console.error("❌ [STOCK-SERVICE] Erreur lors de la récupération des stocks externes:", error);
    return [];
  }
} 