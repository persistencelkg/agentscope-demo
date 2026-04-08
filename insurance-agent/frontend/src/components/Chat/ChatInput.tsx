/** Chat Input Component */

import { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, disabled = false, placeholder = '请输入您的问题...' }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t bg-white px-4 py-3">
      {/* Quick Actions */}
      <div className="flex flex-wrap gap-2 mb-3">
        <button
          onClick={() => onSend('帮我对比平安福和国寿福')}
          disabled={disabled}
          className="px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 rounded-full hover:bg-blue-100 transition-colors disabled:opacity-50"
        >
          对比产品
        </button>
        <button
          onClick={() => onSend('介绍百万医疗险')}
          disabled={disabled}
          className="px-3 py-1.5 text-xs font-medium text-emerald-600 bg-emerald-50 rounded-full hover:bg-emerald-100 transition-colors disabled:opacity-50"
        >
          产品介绍
        </button>
        <button
          onClick={() => onSend('我要退保')}
          disabled={disabled}
          className="px-3 py-1.5 text-xs font-medium text-rose-600 bg-rose-50 rounded-full hover:bg-rose-100 transition-colors disabled:opacity-50"
        >
          退保咨询
        </button>
      </div>

      {/* Input Area */}
      <div className="flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="w-full px-4 py-3 pr-12 text-sm border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
          />
        </div>
        <button
          onClick={handleSubmit}
          disabled={disabled || !message.trim()}
          className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>

      {/* Tips */}
      <p className="text-xs text-gray-400 mt-2 text-center">
        按 Enter 发送，Shift + Enter 换行
      </p>
    </div>
  );
}
