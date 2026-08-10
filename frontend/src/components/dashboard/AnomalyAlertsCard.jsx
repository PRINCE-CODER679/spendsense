import React, { useState } from 'react';
import { ShieldAlert, AlertTriangle, Info, Sparkles, Tag, Zap, ChevronRight } from 'lucide-react';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount || 0);
};

const getSeverityBadge = (severity) => {
  switch (severity) {
    case 'high':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 bg-rose-100 border border-rose-200 text-rose-800 text-xs font-extrabold rounded-full shadow-sm">
          <ShieldAlert className="w-3.5 h-3.5" />
          High Alert
        </span>
      );
    case 'medium':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 bg-amber-100 border border-amber-200 text-amber-800 text-xs font-bold rounded-full">
          <AlertTriangle className="w-3.5 h-3.5" />
          Medium
        </span>
      );
    case 'low':
    default:
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 bg-blue-100 border border-blue-200 text-blue-800 text-xs font-bold rounded-full">
          <Info className="w-3.5 h-3.5" />
          Notice
        </span>
      );
  }
};

const AnomalyAlertsCard = ({ anomalySummary, isLoading }) => {
  const [activeFilter, setActiveFilter] = useState('all');

  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 animate-pulse space-y-3">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="h-20 bg-gray-100 rounded-xl" />
      </div>
    );
  }

  if (!anomalySummary) return null;

  const {
    total_anomalies = 0,
    high_severity_count = 0,
    anomalies = []
  } = anomalySummary;

  const filteredAnomalies = anomalies.filter((item) => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'amount') return item.anomaly_type === 'unusual_amount';
    if (activeFilter === 'category') return item.anomaly_type === 'new_category';
    if (activeFilter === 'spike') return item.anomaly_type === 'daily_spike';
    return true;
  });

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-rose-100 space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-100 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-rose-50 border border-rose-200 text-rose-600 rounded-xl">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 tracking-tight">Phase 8 Anomaly Alerts</h3>
            <p className="text-xs text-gray-500">
              Statistical detection of unusual transactions & spending spikes
            </p>
          </div>
        </div>

        {total_anomalies > 0 ? (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-rose-50 text-rose-700 font-bold text-xs rounded-full border border-rose-200">
            {high_severity_count > 0 ? `${high_severity_count} High Severity` : `${total_anomalies} Anomalies Flagged`}
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-700 font-semibold text-xs rounded-full border border-emerald-200">
            No Anomalies Flagged
          </span>
        )}
      </div>

      {/* Filter Chips */}
      {total_anomalies > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <button
            onClick={() => setActiveFilter('all')}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-colors whitespace-nowrap ${
              activeFilter === 'all'
                ? 'bg-rose-600 text-white shadow-sm'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All ({total_anomalies})
          </button>
          <button
            onClick={() => setActiveFilter('amount')}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-colors whitespace-nowrap ${
              activeFilter === 'amount'
                ? 'bg-rose-600 text-white shadow-sm'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Unusual Amounts ({anomalySummary.unusual_amount_count || 0})
          </button>
          <button
            onClick={() => setActiveFilter('category')}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-colors whitespace-nowrap ${
              activeFilter === 'category'
                ? 'bg-rose-600 text-white shadow-sm'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            New Categories ({anomalySummary.new_category_count || 0})
          </button>
          <button
            onClick={() => setActiveFilter('spike')}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-colors whitespace-nowrap ${
              activeFilter === 'spike'
                ? 'bg-rose-600 text-white shadow-sm'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Daily Spikes ({anomalySummary.daily_spike_count || 0})
          </button>
        </div>
      )}

      {/* Anomaly List */}
      {filteredAnomalies.length === 0 ? (
        <div className="py-6 text-center text-gray-500 text-sm bg-gray-50/50 rounded-xl">
          {total_anomalies === 0
            ? 'All current transactions are within expected statistical ranges.'
            : 'No anomalies found matching the selected filter.'}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredAnomalies.map((item) => (
            <div
              key={item.id}
              className={`p-4 rounded-xl border transition-all ${
                item.severity === 'high'
                  ? 'bg-rose-50/60 border-rose-200'
                  : item.severity === 'medium'
                  ? 'bg-amber-50/50 border-amber-200'
                  : 'bg-blue-50/40 border-blue-200'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-2">
                  {getSeverityBadge(item.severity)}
                  <h4 className="font-bold text-gray-900 text-sm">{item.title}</h4>
                </div>
                <span className="text-xs font-medium text-gray-500">{item.date}</span>
              </div>

              <p className="text-xs text-gray-700 leading-relaxed mb-2">
                {item.description}
              </p>

              <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500 pt-1 border-t border-gray-200/50">
                <span>Category: <strong className="text-gray-800">{item.category}</strong></span>
                <span>Amount: <strong className="text-gray-800">{formatCurrency(item.amount)}</strong></span>
                {item.average_amount > 0 && (
                  <span>Avg: <strong className="text-gray-800">{formatCurrency(item.average_amount)}</strong></span>
                )}
                {item.z_score !== null && item.z_score !== undefined && (
                  <span>Z-Score: <strong className="text-rose-700">{item.z_score} σ</strong></span>
                )}
                {item.confidence_level === 'low' && (
                  <span className="text-amber-700 font-semibold">(Low confidence / small history)</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AnomalyAlertsCard;
