import { NextRequest, NextResponse } from 'next/server';
import { proxyToBackend } from '@/lib/backend-proxy';

export async function POST(request: NextRequest) {
  try {
    const response = await proxyToBackend('/besoins/flush', {
      method: 'POST'
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('❌ [API-ROUTE] /api/besoins/flush POST error:', error);
    return NextResponse.json(
      { error: 'Erreur lors du vidage des besoins' }, 
      { status: 500 }
    );
  }
}
