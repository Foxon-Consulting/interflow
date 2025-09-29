import { NextRequest, NextResponse } from 'next/server';
import { proxyToBackend } from '@/lib/backend-proxy';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    const endpoint = queryString ? `/rappatriements/en-cours?${queryString}` : '/rappatriements/en-cours';
    
    const response = await proxyToBackend(endpoint);
    const data = await response.json();
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('❌ [API-ROUTE] /api/rappatriements/en-cours GET error:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la récupération des rapatriements en cours' }, 
      { status: 500 }
    );
  }
}
