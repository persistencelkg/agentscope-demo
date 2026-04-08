/** Product Introduction Card Component */

import type { IntroResult } from '../../types';

interface ProductIntroCardProps {
  data: IntroResult;
}

export function ProductIntroCard({ data }: ProductIntroCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 px-6 py-4">
        <div className="flex items-center gap-2">
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-lg font-semibold text-white">产品介绍</h3>
        </div>
      </div>

      {/* Product Info */}
      <div className="px-6 py-4 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-xl font-bold text-gray-900">{data.product.name}</h4>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 mt-1">
              {data.product.category}
            </span>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-emerald-600">
              ¥{data.product.premium.toLocaleString()}
            </p>
            <p className="text-sm text-gray-500">年保费</p>
          </div>
        </div>
      </div>

      {/* Highlights */}
      <div className="px-6 py-4 border-b">
        <h5 className="text-sm font-medium text-gray-700 mb-3">核心亮点</h5>
        <div className="space-y-2">
          {data.highlights.map((highlight, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <svg className="w-5 h-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-sm text-gray-600">{highlight}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Coverage */}
      <div className="px-6 py-4 border-b">
        <h5 className="text-sm font-medium text-gray-700 mb-3">保障范围</h5>
        <div className="flex flex-wrap gap-2">
          {data.product.coverage.map((item, idx) => (
            <span
              key={idx}
              className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700"
            >
              {item}
            </span>
          ))}
        </div>
      </div>

      {/* Target Audience */}
      <div className="px-6 py-4 border-b bg-gray-50">
        <h5 className="text-sm font-medium text-gray-700 mb-2">适合人群</h5>
        <p className="text-sm text-gray-600">{data.target_audience}</p>
      </div>

      {/* Scenarios */}
      <div className="px-6 py-4">
        <h5 className="text-sm font-medium text-gray-700 mb-3">适用场景</h5>
        <div className="space-y-2">
          {data.scenarios.map((scenario, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span className="flex-shrink-0 w-5 h-5 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-xs font-medium">
                {idx + 1}
              </span>
              <span className="text-sm text-gray-600">{scenario}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 py-3 bg-gray-50 border-t flex items-center justify-between text-xs text-gray-500">
        <span>等待期: {data.product.waiting_period}</span>
        <span>保障期限: {data.product.term}</span>
      </div>
    </div>
  );
}
