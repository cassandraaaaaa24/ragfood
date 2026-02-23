import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  try {
    const status = {
      status: 'healthy',
      environment: process.env.NODE_ENV,
      timestamp: new Date().toISOString(),
      checks: {
        groq_api_key: !!process.env.GROQ_API_KEY ? '✓' : '✗',
      },
    };

    return NextResponse.json(status, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      { status: 'error', message: 'Health check failed' },
      { status: 500 }
    );
  }
}
