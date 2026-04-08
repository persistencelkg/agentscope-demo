/** Product Comparison Card Component */

import type { CompareResult } from '../../types';

interface ProductCompareCardProps {
  data: CompareResult;
}

export function ProductCompareCard({ data }: ProductCompareCardProps) {
  const aspects = Object.keys(data.comparison_table);

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
        <div className="flex items-center gap-2">
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 className="text-lg font-semibold text-white">产品对比</h3>
        </div>
      </div>

      {/* Product Names */}
      <div className="px-6 py-3 bg-gray-50 border-b">
        <div className="flex gap-4">
          {data.products.map((product, idx) => (
            <div key={idx} className="flex-1">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                {product.name}
              </span>
              <span className="ml-2 text-xs text-gray-500">{product.category}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Comparison Table */}
      <div className="px-6 py-4">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-2 text-sm font-medium text-gray-500 w-24">对比项</th>
              {data.products.map((_, idx) => (
                <th key={idx} className="text-left py-2 text-sm font-medium text-gray-500">
                  产品 {idx + 1}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {aspects.map((aspect, rowIdx) => (
              <tr key={rowIdx} className="border-b border-gray-100">
                <td className="py-3 text-sm font-medium text-gray-700">{aspect}</td>
                {data.comparison_table[aspect].map((value, colIdx) => (
                  <td key={colIdx} className="py-3 text-sm text-gray-600">
                    {value}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Recommendation */}
      <div className="px-6 py-4 bg-amber-50 border-t border-amber-100">
        <div className="flex items-start gap-2">
          <svg className="w-5 h-5 text-amber-500 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <div>
            <p className="text-sm font-medium text-amber-800">智能推荐</p>
            <p className="text-sm text-amber-700 mt-1">{data.recommendation}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
