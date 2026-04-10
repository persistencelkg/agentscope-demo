/** API Service for Insurance Agent */

import type { ChatRequest, ChatResponse, StreamMessage } from '../types';

const API_BASE = '/api';

// Request deduplication cache
const pendingRequests = new Map<string, Promise<ChatResponse>>();

// Response cache for GET requests
const responseCache = new Map<string, { data: unknown; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  // Deduplicate by message content
  const cacheKey = `${request.session_id}:${request.message}`;
  
  if (pendingRequests.has(cacheKey)) {
    return pendingRequests.get(cacheKey)!;
  }

  const promise = fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  }).then(async (response) => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }).finally(() => {
    pendingRequests.delete(cacheKey);
  });

  pendingRequests.set(cacheKey, promise);
  return promise;
}

export async function* sendMessageStream(
  request: ChatRequest
): AsyncGenerator<StreamMessage> {
  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.trim()) {
          try {
            const data = JSON.parse(line) as StreamMessage;
            yield data;
          } catch {
            console.warn('Failed to parse line:', line);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export async function getIntents(): Promise<{ intents: Array<{ type: string; name: string; description: string; example: string }> }> {
  const cacheKey = 'intents';
  const cached = responseCache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data as ReturnType<typeof getIntents>;
  }

  const response = await fetch(`${API_BASE}/intents`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const data = await response.json();
  responseCache.set(cacheKey, { data, timestamp: Date.now() });
  return data;
}

export async function getProducts(): Promise<{ products: string[] }> {
  const cacheKey = 'products';
  const cached = responseCache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data as ReturnType<typeof getProducts>;
  }

  const response = await fetch(`${API_BASE}/products`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const data = await response.json();
  responseCache.set(cacheKey, { data, timestamp: Date.now() });
  return data;
}
