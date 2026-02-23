import { NextRequest, NextResponse } from 'next/server';
import * as fs from 'fs';
import * as path from 'path';

let foodsData: any[] = [];

// Load foods data
async function loadFoodsData() {
  if (foodsData.length === 0) {
    try {
      // Try to load from the web-app data directory
      // In Vercel and local dev, process.cwd() is the project root
      const foodsPath = path.join(process.cwd(), 'data', 'foods.json');
      const data = fs.readFileSync(foodsPath, 'utf-8');
      foodsData = JSON.parse(data);
      console.log(`✅ Loaded ${foodsData.length} foods from foods.json`);
    } catch (err) {
      console.error('⚠️ Could not load foods.json:', err);
      console.log('⚠️ Will use LLM knowledge only');
    }
  }
  return foodsData;
}

// Initialize Groq client
function getGroqClient() {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) {
    throw new Error('GROQ_API_KEY not set in environment variables');
  }
  return fetch('https://api.groq.com/openai/v1/chat/completions', {
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
  });
}

function extractContextFromFoods(query: string): { foods: string[]; sources: string[] } {
  const foods = foodsData;
  const queryLower = query.toLowerCase();
  const relevantFoods: string[] = [];

  foods.forEach((food: any) => {
    const foodStr = JSON.stringify(food).toLowerCase();
    if (
      foodStr.includes(queryLower) ||
      query.split(' ').some(word => word.length > 2 && foodStr.includes(word.toLowerCase()))
    ) {
      relevantFoods.push(JSON.stringify(food, null, 2));
    }
  });

  return {
    foods: relevantFoods.slice(0, 3),
    sources: relevantFoods.length > 0 ? ['Local Food Dataset'] : [],
  };
}

async function callGroqAPI(systemPrompt: string, userQuery: string): Promise<string> {
  const apiKey = process.env.GROQ_API_KEY;

  if (!apiKey) {
    throw new Error('GROQ_API_KEY not configured');
  }

  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'llama-3.1-8b-instant',
      max_tokens: 1024,
      messages: [
        {
          role: 'system',
          content: systemPrompt,
        },
        {
          role: 'user',
          content: userQuery,
        },
      ],
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    console.error('Groq API error:', errorData);
    throw new Error(`Groq API error: ${response.status} - ${JSON.stringify(errorData)}`);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

export async function POST(request: NextRequest) {
  try {
    const { query } = await request.json();

    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Invalid query' },
        { status: 400 }
      );
    }

    // Load foods data
    await loadFoodsData();

    // Search local food data
    const { foods, sources } = extractContextFromFoods(query);
    const context = foods.join('\n\n');

    // Prepare system prompt
    const systemPrompt = `You are a helpful food expert who answers questions about various cuisines and dishes from around the world.
${
  context
    ? `Use the following food information to answer the question:\n\n${context}`
    : 'Use your knowledge to answer the question.'
}
Be concise but informative. If you don't know, say so.`;

    // Call Groq API
    const answer = await callGroqAPI(systemPrompt, query);

    return NextResponse.json({
      answer,
      context: context.substring(0, 400) || 'No specific food data found',
      sources: sources.length > 0 ? sources : ['LLM Knowledge'],
    });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      {
        error: 'Failed to process request',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
