import { NextRequest, NextResponse } from 'next/server';
import { proxyToBackend } from '@/lib/backend-proxy';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await proxyToBackend('/receptions/generer-bon', {
      method: 'POST',
      body
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('❌ [API-ROUTE] /api/receptions/generer-bon POST error:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la génération du bon de réception' }, 
      { status: 500 }
    );
  }
}
