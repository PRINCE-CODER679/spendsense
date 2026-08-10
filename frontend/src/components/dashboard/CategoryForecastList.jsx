import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount || 0);
};

const getRiskBadge = (riskLevel) => {
  switch (riskLevel) {
    case 'high_risk':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold rounded-full">
          <AlertCircle className="w-3.5 h-3.5" />
          High Risk
        </span>
      );
    case 'moderate_risk':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-50 border border-amber-200 text-amber-700 text-xs font-bold rounded-full">
          <AlertTriangle className="w-3.5 h-3.5" />
          Moderate Risk
        </span>
      );
    case 'safe':
    default:
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold rounded-full">
          <CheckCircle2 className="w-3.5 h-3.5" />
          Safe
        </span>
      );
  }
};

const CategoryForecastList = ({ forecasts, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 animate-pulse space-y-4">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-16 bg-gray-100 rounded-xl" />
        ))}
      </div>
    );
  }

  const items = forecasts || [];

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-gray-900 tracking-tight">Category Spending Forecasts</h3>
          <p className="text-xs text-gray-500 mt-0.5">
            Category risk matrix & predicted budget overspending
          </p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 bg-gray-100 text-gray-600 rounded-lg">
          {items.length} Categories
        </span>
      </div>

      {items.length === 0 ? (
        <div className="py-8 text-center text-gray-500 text-sm">
          No category forecasts available for this month yet.
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((forecast, index) => {
            const baseline = forecast.budget_amount || forecast.historical_average;
            const percentageUsed = baseline > 0 ? (forecast.projected_spending / baseline) * 100 : 0;

            return (
              <div
                key={index}
                className="p-4 rounded-xl border border-gray-100 hover:border-gray-200 transition-all bg-gray-50/50 space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-gray-900 text-sm">{forecast.category}</span>
                    {getRiskBadge(forecast.risk_level)}
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-gray-500">Projected: </span>
                    <span className="font-extrabold text-sm text-gray-900">
                      {formatCurrency(forecast.projected_spending)}
                    </span>
                  </div>
                </div>

                {/* Progress bar comparing projected against budget/baseline */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Spent: {formatCurrency(forecast.current_spending)} ({forecast.daily_rate} ₹/day)</span>
                    <span>
                      {forecast.budget_amount
                        ? `Budget: ${formatCurrency(forecast.budget_amount)}`
                        : `Baseline: ${formatCurrency(forecast.historical_average)}`}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        forecast.risk_level === 'high_risk'
                          ? 'bg-rose-500'
                          : forecast.risk_level === 'moderate_risk'
                          ? 'bg-amber-500'
                          : 'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.min(percentageUsed, 100)}%` }}
                    />
                  </div>
                </div>

                {/* Overspend warning callout */}
                {forecast.projected_overspend > 0 && (
                  <div className="text-xs text-rose-600 font-semibold flex items-center gap-1.5 pt-1">
                    <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                    Predicted to exceed limit by {formatCurrency(forecast.projected_overspend)} (+{forecast.percentage_above_baseline}%)
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default CategoryForecastList;
