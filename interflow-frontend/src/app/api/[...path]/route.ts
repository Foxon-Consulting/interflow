import { NextRequest, NextResponse } from 'next/server';
import { proxyToBackend } from '@/lib/backend-proxy';

/**
 * Route dynamique catch-all pour toutes les API
 * Gère automatiquement tous les endpoints en les proxifiant vers le backend
 */

interface RouteParams {
  params: Promise<{
    path: string[];
  }>;
}

export async function GET(request: NextRequest, { params }: RouteParams) {
  try {
    const { path } = await params;
    const { searchParams } = new URL(request.url);
    
    // Reconstruire le chemin complet
    const fullPath = `/${path.join('/')}`;
    const queryString = searchParams.toString();
    const endpoint = queryString ? `${fullPath}?${queryString}` : fullPath;
    
    console.log(`🔄 [API-CATCH-ALL] GET ${endpoint}`);
    
    const response = await proxyToBackend(endpoint);
    const data = await response.json();
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    const resolvedParams = await params;
    const errorPath = `/${resolvedParams.path.join('/')}`;
    console.error(`❌ [API-CATCH-ALL] GET ${errorPath} error:`, error);
    return NextResponse.json(
      { error: `Erreur lors de l'accès à ${errorPath}` }, 
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest, { params }: RouteParams) {
  try {
    const { path } = await params;
    const fullPath = `/${path.join('/')}`;
    const contentType = request.headers.get('content-type');
    
    console.log(`🔄 [API-CATCH-ALL] POST ${fullPath}`);
    
    let response;
    if (contentType?.includes('multipart/form-data')) {
      // Pour les uploads de fichiers
      const formData = await request.formData();
      response = await proxyToBackend(fullPath, {
        method: 'POST',
        body: formData
      });
    } else {
      // Pour les données JSON (ou body vide)
      let body = null;
      const text = await request.text();
      if (text) {
        try {
          body = JSON.parse(text);
        } catch {
          // Si ce n'est pas du JSON valide, utiliser le texte brut
          body = text;
        }
      }
      response = await proxyToBackend(fullPath, {
        method: 'POST',
        body
      });
    }
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    const resolvedParams = await params;
    const errorPath = `/${resolvedParams.path.join('/')}`;
    console.error(`❌ [API-CATCH-ALL] POST ${errorPath} error:`, error);
    return NextResponse.json(
      { error: `Erreur lors de la création sur ${errorPath}` }, 
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest, { params }: RouteParams) {
  try {
    const { path } = await params;
    const fullPath = `/${path.join('/')}`;
    const body = await request.json();
    
    console.log(`🔄 [API-CATCH-ALL] PUT ${fullPath}`);
    
    const response = await proxyToBackend(fullPath, {
      method: 'PUT',
      body
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    const resolvedParams = await params;
    const errorPath = `/${resolvedParams.path.join('/')}`;
    console.error(`❌ [API-CATCH-ALL] PUT ${errorPath} error:`, error);
    return NextResponse.json(
      { error: `Erreur lors de la mise à jour sur ${errorPath}` }, 
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest, { params }: RouteParams) {
  try {
    const { path } = await params;
    const fullPath = `/${path.join('/')}`;
    
    console.log(`🔄 [API-CATCH-ALL] DELETE ${fullPath}`);
    
    const response = await proxyToBackend(fullPath, {
      method: 'DELETE'
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    const resolvedParams = await params;
    const errorPath = `/${resolvedParams.path.join('/')}`;
    console.error(`❌ [API-CATCH-ALL] DELETE ${errorPath} error:`, error);
    return NextResponse.json(
      { error: `Erreur lors de la suppression sur ${errorPath}` }, 
      { status: 500 }
    );
  }
}
