import { NextRequest, NextResponse } from 'next/server';
import { proxyToBackend } from '@/lib/backend-proxy';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    
    const response = await proxyToBackend('/stocks/import', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('❌ [API-ROUTE] /api/stocks/import POST error:', error);
    return NextResponse.json(
      { error: 'Erreur lors de l\'import des stocks' }, 
      { status: 500 }
    );
  }
}
