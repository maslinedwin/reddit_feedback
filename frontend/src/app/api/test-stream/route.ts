import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

// IMPORTANT! Set the runtime to edge
export const runtime = 'edge';

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    
    // Test streaming without backend dependency
    const result = await streamText({
      model: openai('gpt-3.5-turbo'),
      messages: [
        {
          role: 'system',
          content: 'You are a helpful assistant. This is a test to verify streaming is working.',
        },
        ...messages,
      ],
    });

    return result.toTextStreamResponse();
  } catch (error) {
    console.error('Error in test stream:', error);
    return new Response(
      JSON.stringify({ error: 'Streaming test failed', details: error.message }), 
      { status: 500 }
    );
  }
}