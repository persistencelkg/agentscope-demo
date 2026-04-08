/** Insurance Agent TypeScript Types */

export type IntentType = 'product_compare' | 'product_intro' | 'surrender' | 'unknown';

export type ExtractMethod = 'exact' | 'fuzzy' | 'vector';

export type CardType = 'product_compare' | 'product_intro' | 'surrender' | 'text';

export interface IntentAnalysis {
  intent: IntentType;
  confidence: number;
  extract_method: ExtractMethod;
  products: string[];
  entities: Record<string, unknown>;
  raw_query: string;
}

export interface ProductInfo {
  id: string;
  name: string;
  category: string;
  premium: number;
  coverage: string[];
  features: string[];
  exclusions: string[];
  waiting_period: string;
  term: string;
}

export interface CompareResult {
  products: ProductInfo[];
  comparison_table: Record<string, string[]>;
  recommendation: string;
}

export interface IntroResult {
  product: ProductInfo;
  highlights: string[];
  target_audience: string;
  scenarios: string[];
}

export interface SurrenderResult {
  policy_id: string;
  policy_name: string;
  premium_paid: number;
  surrender_value: number;
  loss_amount: number;
  loss_percentage: number;
  notes: string[];
}

export interface CardPayload {
  card_type: CardType;
  data: CompareResult | IntroResult | SurrenderResult | Record<string, unknown>;
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  cards: CardPayload[];
  timestamp: Date;
  intent?: IntentAnalysis;
}

export interface ChatRequest {
  message: string;
  session_id: string;
}

export interface ChatResponse {
  message: string;
  cards: CardPayload[];
  intent: IntentAnalysis | null;
  session_id: string;
}

export interface StreamMessage {
  type: 'status' | 'intent' | 'card' | 'message' | 'error';
  message?: string;
  data?: unknown;
  content?: string;
}
