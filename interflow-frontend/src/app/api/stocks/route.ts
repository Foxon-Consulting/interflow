import { NextRequest, NextResponse } from 'next/server';
import { proxyToBackend } from '@/lib/backend-proxy';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    const endpoint = queryString ? `/stocks?${queryString}` : '/stocks';
    
    const response = await proxyToBackend(endpoint);
    const data = await response.json();
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('❌ [API-ROUTE] /api/stocks GET error:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la récupération des stocks' }, 
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const contentType = request.headers.get('content-type');
    
    let response;
    if (contentType?.includes('multipart/form-data')) {
      // Pour les uploads de fichiers
      const formData = await request.formData();
      response = await proxyToBackend('/stocks/import', {
        method: 'POST',
        body: formData
      });
    } else {
      // Pour les données JSON
      const body = await request.json();
      response = await proxyToBackend('/stocks', {
        method: 'POST',
        body
      });
    }
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('❌ [API-ROUTE] /api/stocks POST error:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la création/import des stocks' }, 
      { status: 500 }
    );
  }
}
