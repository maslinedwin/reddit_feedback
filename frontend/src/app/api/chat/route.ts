import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

// IMPORTANT! Set the runtime to edge
export const runtime = 'edge';

export async function POST(req: Request) {
  try {
    // Extract the `messages` from the body of the request
    const { messages } = await req.json();
    
    if (!messages || messages.length === 0) {
      return new Response(
        JSON.stringify({ error: 'No messages provided' }), 
        { 
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    const currentMessageContent = messages[messages.length - 1].content;

    // Get the context from the Python backend using fetch (Edge Runtime compatible)
    const response = await fetch('http://127.0.0.1:8000/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: currentMessageContent }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error:', errorText);
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    const context = data.context;

    console.log('Context received from backend:', context);

    // Check if OpenAI API key is configured
    if (!process.env.OPENAI_API_KEY) {
      console.error('OPENAI_API_KEY is not configured');
      throw new Error('OpenAI API key is not configured. Please set OPENAI_API_KEY in your environment variables.');
    }

    // Stream the AI response
    const result = await streamText({
      model: openai('gpt-4'), // Using GPT-4 for better analytical capabilities
      messages: [
        {
          role: 'system',
          content: `You are an expert analyst specializing in Reddit community feedback about Patreon and creator monetization platforms. Your job is to extract specific, actionable insights from real Reddit discussions.

IMPORTANT: You have access to the following Reddit posts and comments with relevance scores:

${context}

ANALYSIS INSTRUCTIONS:
1. ALWAYS quote specific Reddit users' experiences and opinions verbatim when relevant
2. Look for patterns, trends, and specific details in the feedback
3. Prioritize high-scoring documents (0.7+) but also check lower scores for unique insights
4. When discussing tips, strategies, or problems, cite EXACT examples from the Reddit data
5. If multiple users mention similar things, note this as a trend
6. For questions about money/revenue/NSFW content, provide specific details mentioned by users
7. Never give generic advice - ONLY share what Reddit users actually said
8. If the data doesn't contain specific information, acknowledge this and share the closest relevant insights

RESPONSE FORMAT & MARKDOWN FEATURES:

**Structure Guidelines:**
- Lead with a brief summary or key finding
- Use clear headings (##, ###) to organize sections
- Add line breaks between major points for readability
- End with actionable insights or summary

**Text Formatting:**
- **Bold** for usernames, key terms, and important points
- *Italics* for emphasis or secondary information
- \`inline code\` for specific values, percentages, or technical terms
- > Blockquotes for direct Reddit quotes
- --- (horizontal rule) to separate major sections

**Lists & Organization:**
1. Use numbered lists for strategies, steps, or ranked items
   - Use sub-bullets for details
   - Can nest multiple levels
2. Use bullet points for non-sequential items
   - Keep related points together
   - Add spacing between different topics

**Special Elements:**
- Tables for comparing options or data
- Links when referencing sources
- Code blocks for longer technical content
- Mark important warnings with **⚠️ Warning:** or **💡 Tip:**

**Formatting Examples:**

### Strategy Name
**u/username** (Score: 0.8) suggests:
> "Direct quote from the Reddit user here..."

Key points:
- First insight
- Second insight with \`specific value\`
- Third point with **emphasis**

---

**Contrasting Opinion:** Another user **u/different_user** disagrees...

Remember: You're analyzing REAL Reddit feedback. Make responses scannable and visually organized.`,
        },
        {
          role: 'user',
          content: currentMessageContent,
        },
      ],
      temperature: 0.3, // Lower temperature for more focused, analytical responses
      maxTokens: 1500, // More tokens for detailed analysis
      topP: 0.9, // Slightly focused sampling
      frequencyPenalty: 0.2, // Reduce repetition
      presencePenalty: 0.1, // Encourage diverse vocabulary
    });

    console.log('Streaming response created successfully');
    
    // Return the streaming response directly
    return result.toDataStreamResponse();
  } catch (error) {
    console.error('Error in /api/chat:', error);
    console.error('Error stack:', error.stack);
    
    // Return a proper error response to the frontend
    return new Response(
      JSON.stringify({ 
        error: 'Internal Server Error', 
        details: error.message,
        type: error.constructor.name 
      }), 
      { 
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        }
      }
    );
  }
}