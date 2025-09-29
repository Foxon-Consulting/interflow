import { NextRequest, NextResponse } from 'next/server';
import { proxyToBackend } from '@/lib/backend-proxy';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    const endpoint = queryString ? `/receptions/type?${queryString}` : '/receptions/type';
    
    const response = await proxyToBackend(endpoint);
    const data = await response.json();
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('❌ [API-ROUTE] /api/receptions/type GET error:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la récupération des réceptions par type' }, 
      { status: 500 }
    );
  }
}
