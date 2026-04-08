/** Chat Message Component */

import type { ChatMessage as ChatMessageType, CardPayload, CompareResult, IntroResult, SurrenderResult } from '../../types';
import { ProductCompareCard } from '../Cards/ProductCompareCard';
import { ProductIntroCard } from '../Cards/ProductIntroCard';
import { SurrenderCard } from '../Cards/SurrenderCard';

interface ChatMessageProps {
  message: ChatMessageType;
}

function renderCard(card: CardPayload, idx: number) {
  switch (card.card_type) {
    case 'product_compare':
      return <ProductCompareCard key={idx} data={card.data as CompareResult} />;
    case 'product_intro':
      return <ProductIntroCard key={idx} data={card.data as IntroResult} />;
    case 'surrender':
      return <SurrenderCard key={idx} data={card.data as SurrenderResult} />;
    default:
      return null;
  }
}

function getIntentBadge(intent?: ChatMessageType['intent']) {
  if (!intent) return null;

  const badges: Record<string, { label: string; color: string }> = {
    product_compare: { label: '产品对比', color: 'bg-blue-100 text-blue-700' },
    product_intro: { label: '产品介绍', color: 'bg-emerald-100 text-emerald-700' },
    surrender: { label: '退保咨询', color: 'bg-rose-100 text-rose-700' },
    unknown: { label: '未知', color: 'bg-gray-100 text-gray-700' },
  };

  const badge = badges[intent.intent] || badges.unknown;

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${badge.color}`}>
      {badge.label}
      <span className="ml-1 opacity-60">({(intent.confidence * 100).toFixed(0)}%)</span>
    </span>
  );
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar and name */}
        <div className={`flex items-center gap-2 mb-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          {!isUser && (
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
          )}
          <span className="text-xs text-gray-500">
            {isUser ? '您' : '保险助手'}
          </span>
          {!isUser && message.intent && getIntentBadge(message.intent)}
        </div>

        {/* Message content */}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white rounded-br-md'
              : 'bg-white border border-gray-200 text-gray-800 rounded-bl-md shadow-sm'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Cards */}
        {!isUser && message.cards.length > 0 && (
          <div className="mt-3 space-y-3">
            {message.cards.map((card, idx) => renderCard(card, idx))}
          </div>
        )}

        {/* Timestamp */}
        <p className={`text-xs text-gray-400 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {message.timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
}
