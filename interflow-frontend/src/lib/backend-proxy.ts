/**
 * Service proxy générique pour communiquer avec le backend Python
 * Toutes les requêtes passent par ce service côté serveur Next.js
 */

const BACKEND_URL = 'http://127.0.0.1:5000';

export interface ProxyRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  body?: any;
  headers?: Record<string, string>;
}

/**
 * Fonction générique pour proxifier les requêtes vers le backend
 */
export async function proxyToBackend(
  endpoint: string, 
  options: ProxyRequestOptions = {}
): Promise<Response> {
  const { method = 'GET', body, headers = {} } = options;
  
  // Construire l'URL complète
  const url = `${BACKEND_URL}${endpoint}`;
  
  // Configuration de la requête
  const fetchOptions: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers
    }
  };
  
  // Ajouter le body si nécessaire
  if (body && method !== 'GET') {
    if (body instanceof FormData) {
      // Pour les uploads de fichiers, ne pas définir Content-Type (laissé auto)
      delete (fetchOptions.headers as any)['Content-Type'];
      fetchOptions.body = body;
    } else {
      fetchOptions.body = JSON.stringify(body);
    }
  }
  
  console.log(`🔄 [BACKEND-PROXY] ${method} ${url}`);
  
  try {
    const response = await fetch(url, fetchOptions);
    
    console.log(`✅ [BACKEND-PROXY] ${method} ${url} → ${response.status}`);
    
    return response;
    
  } catch (error) {
    console.error(`❌ [BACKEND-PROXY] Erreur lors de l'appel ${method} ${url}:`, error);
    throw error;
  }
}

/**
 * Fonction helper pour les requêtes JSON simples
 */
export async function proxyJsonRequest(
  endpoint: string, 
  options: ProxyRequestOptions = {}
): Promise<any> {
  const response = await proxyToBackend(endpoint, options);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: "Erreur réseau" }));
    throw new Error(errorData.message || `Erreur HTTP: ${response.status}`);
  }
  
  return response.json();
}
