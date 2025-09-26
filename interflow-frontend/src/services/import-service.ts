import { API_BASE_URL } from '@/config/api';

/**
 * Service généralisé pour l'import de fichiers CSV et XLSX
 * Supporte tous les types de données de l'application
 */

export type ImportType = 'csv' | 'xlsx';
export type EntityType = 'stocks' | 'matieres' | 'receptions' | 'besoins' | 'rappatriements';

interface ImportResponse<T = unknown> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: boolean;
  stocks?: unknown[];
  matieres?: unknown[];
  receptions?: unknown[];
  besoins?: unknown[];
  rapatriements?: unknown[];
}

// Fonction utilitaire pour gérer les erreurs API
async function handleApiResponse(response: Response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: "Erreur réseau" }));
    throw new Error(errorData.message || `Erreur HTTP: ${response.status}`);
  }
  return response.json();
}

/**
 * Fonction générique pour importer des données depuis un fichier CSV ou XLSX
 * @param file - Le fichier à importer
 * @param entityType - Le type d'entité (stocks, matieres, commandes, besoins, rapatriements)
 * @param importType - Le type d'import (csv ou xlsx)
 * @returns Promise avec les données importées
 */
export async function importDataFromFile<T = unknown>(
  file: File, 
  entityType: EntityType, 
  importType: ImportType = 'csv'
): Promise<ImportResponse<T>> {
  try {
    // Validation du fichier
    if (!file) {
      throw new Error("Aucun fichier fourni");
    }

    // Validation de l'extension du fichier
    const fileName = file.name.toLowerCase();
    const expectedExtension = importType === 'csv' ? '.csv' : '.xlsx';
    if (!fileName.endsWith(expectedExtension)) {
      throw new Error(`Le fichier doit être au format ${importType.toUpperCase()}`);
    }

    const formData = new FormData();
    formData.append('file', file);
    
    // Construire l'URL en fonction du type d'entité
    // Les rapatriements utilisent /append, les autres utilisent /import
    const endpoint = entityType === 'rappatriements' 
      ? `${API_BASE_URL}/${entityType}/append`
      : `${API_BASE_URL}/${entityType}/import`;
    
    const response = await fetch(endpoint, {
      method: 'POST',
      body: formData
    });
    
    const data: ApiResponse<T> = await handleApiResponse(response);
    
    return {
      success: true,
      message: `Import ${importType.toUpperCase()} réussi pour ${entityType}`,
      data: data.data as T || data as T
    };
    
  } catch (error) {
    console.error(`❌ [IMPORT-SERVICE] Erreur lors de l'import ${importType} pour ${entityType}:`, error);
    return {
      success: false,
      message: error instanceof Error ? error.message : `Erreur lors de l'import ${importType}`,
      error: error instanceof Error ? error.message : "Erreur inconnue"
    };
  }
}

/**
 * Fonction spécialisée pour importer des stocks
 */
export async function importStocksFromFile(
  file: File, 
  importType?: ImportType
): Promise<ImportResponse> {
  const detectedType = importType || detectFileType(file);
  return importDataFromFile(file, 'stocks', detectedType);
}

/**
 * Fonction spécialisée pour importer des matières
 */
export async function importMatieresFromFile(
  file: File, 
  importType?: ImportType
): Promise<ImportResponse> {
  const detectedType = importType || detectFileType(file);
  return importDataFromFile(file, 'matieres', detectedType);
}

/**
 * Fonction spécialisée pour importer des réceptions
 */
export async function importReceptionsFromFile(
  file: File, 
  importType?: ImportType
): Promise<ImportResponse> {
  const detectedType = importType || detectFileType(file);
  return importDataFromFile(file, 'receptions', detectedType);
}

/**
 * Fonction spécialisée pour importer des besoins
 */
export async function importBesoinsFromFile(
  file: File, 
  importType?: ImportType
): Promise<ImportResponse> {
  const detectedType = importType || detectFileType(file);
  return importDataFromFile(file, 'besoins', detectedType);
}

/**
 * Fonction spécialisée pour importer des rapatriements
 */
export async function importRappatriementsFromFile(
  file: File, 
  importType?: ImportType
): Promise<ImportResponse> {
  const detectedType = importType || detectFileType(file);
  return importDataFromFile(file, 'rappatriements', detectedType);
}

/**
 * Fonction utilitaire pour détecter automatiquement le type de fichier
 */
export function detectFileType(file: File): ImportType {
  const fileName = file.name.toLowerCase();
  if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
    return 'xlsx';
  }
  return 'csv';
}

/**
 * Fonction utilitaire pour valider le type de fichier
 */
export function validateFileType(file: File, allowedTypes: ImportType[] = ['csv', 'xlsx']): boolean {
  const fileType = detectFileType(file);
  return allowedTypes.includes(fileType);
} 