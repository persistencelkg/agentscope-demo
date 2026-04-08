/** API Service for Insurance Agent */

import type { ChatRequest, ChatResponse, StreamMessage } from '../types';

const API_BASE = '/api';

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
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
  const response = await fetch(`${API_BASE}/intents`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function getProducts(): Promise<{ products: string[] }> {
  const response = await fetch(`${API_BASE}/products`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}
