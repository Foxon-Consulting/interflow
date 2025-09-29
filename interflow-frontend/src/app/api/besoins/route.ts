import { NextRequest, NextResponse } from 'next/server';
import { proxyToBackend } from '@/lib/backend-proxy';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    const endpoint = queryString ? `/besoins?${queryString}` : '/besoins';
    
    const response = await proxyToBackend(endpoint);
    const data = await response.json();
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('❌ [API-ROUTE] /api/besoins GET error:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la récupération des besoins' }, 
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await proxyToBackend('/besoins', {
      method: 'POST',
      body
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('❌ [API-ROUTE] /api/besoins POST error:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la création du besoin' }, 
      { status: 500 }
    );
  }
}
