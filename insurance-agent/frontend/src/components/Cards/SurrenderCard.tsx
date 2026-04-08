/** Surrender Calculation Card Component */

import type { SurrenderResult } from '../../types';

interface SurrenderCardProps {
  data: SurrenderResult;
}

export function SurrenderCard({ data }: SurrenderCardProps) {
  const lossColor = data.loss_percentage > 50 ? 'text-red-600' : data.loss_percentage > 30 ? 'text-amber-600' : 'text-green-600';

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-rose-500 to-rose-600 px-6 py-4">
        <div className="flex items-center gap-2">
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-semibold text-white">退保计算</h3>
        </div>
      </div>

      {/* Policy Info */}
      <div className="px-6 py-4 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-lg font-bold text-gray-900">{data.policy_name}</h4>
            <p className="text-sm text-gray-500 mt-1">保单号: {data.policy_id}</p>
          </div>
        </div>
      </div>

      {/* Financial Summary */}
      <div className="px-6 py-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500">已缴保费</p>
            <p className="text-xl font-bold text-gray-900 mt-1">
              ¥{data.premium_paid.toLocaleString()}
            </p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-sm text-gray-500">退保金额</p>
            <p className="text-xl font-bold text-green-600 mt-1">
              ¥{data.surrender_value.toLocaleString()}
            </p>
          </div>
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <p className="text-sm text-gray-500">损失金额</p>
            <p className={`text-xl font-bold ${lossColor} mt-1`}>
              ¥{data.loss_amount.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Loss Percentage */}
      <div className="px-6 py-4 border-t border-b">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">损失率</span>
          <span className={`text-lg font-bold ${lossColor}`}>{data.loss_percentage.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className={`h-2.5 rounded-full ${data.loss_percentage > 50 ? 'bg-red-500' : data.loss_percentage > 30 ? 'bg-amber-500' : 'bg-green-500'}`}
            style={{ width: `${data.loss_percentage}%` }}
          />
        </div>
      </div>

      {/* Notes */}
      <div className="px-6 py-4 bg-amber-50">
        <h5 className="text-sm font-medium text-amber-800 mb-3">温馨提示</h5>
        <ul className="space-y-2">
          {data.notes.map((note, idx) => (
            <li key={idx} className="flex items-start gap-2 text-sm text-amber-700">
              <svg className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{note}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
