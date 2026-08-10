import React from 'react';
import { TrendingUp, AlertTriangle, Clock, ShieldAlert, Zap, Calendar } from 'lucide-react';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount || 0);
};

const ForecastCard = ({ forecastSummary, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 animate-pulse h-48" />
    );
  }

  if (!forecastSummary) return null;

  const {
    overall_current_spending = 0,
    overall_projected_spending = 0,
    daily_burn_rate = 0,
    days_elapsed = 1,
    days_in_month = 30,
    days_remaining = 0,
    confidence_level = 'high',
    high_risk_count = 0,
    moderate_risk_count = 0,
    total_predicted_overspend = 0
  } = forecastSummary;

  const isLowConfidence = confidence_level === 'low' || days_elapsed <= 2;

  return (
    <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white rounded-2xl p-6 shadow-xl border border-indigo-900/50 space-y-5">
      {/* Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/20 backdrop-blur-md rounded-xl border border-indigo-400/30 text-indigo-300">
            <Zap className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-extrabold tracking-tight">Phase 7 Spending Forecast</h3>
            <p className="text-xs text-slate-300">
              Rule-based spending projection based on current daily burn rate
            </p>
          </div>
        </div>

        {/* Confidence Badge */}
        <div className="flex items-center gap-2">
          {isLowConfidence ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-500/20 border border-amber-400/30 text-amber-300 text-xs font-semibold rounded-full">
              <AlertTriangle className="w-3.5 h-3.5" />
              Low Confidence (Early Month)
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 text-xs font-semibold rounded-full">
              <ShieldAlert className="w-3.5 h-3.5" />
              High Confidence Forecast
            </span>
          )}
        </div>
      </div>

      {/* Main KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white/5 backdrop-blur-sm p-4 rounded-xl border border-white/10">
          <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Spent So Far</span>
          <div className="text-2xl font-black text-white mt-1">
            {formatCurrency(overall_current_spending)}
          </div>
          <span className="text-xs text-slate-400 mt-1 block">
            Over {days_elapsed} days
          </span>
        </div>

        <div className="bg-white/5 backdrop-blur-sm p-4 rounded-xl border border-white/10">
          <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Projected Month-End</span>
          <div className="text-2xl font-black text-amber-300 mt-1">
            {formatCurrency(overall_projected_spending)}
          </div>
          <span className="text-xs text-slate-400 mt-1 block">
            Expected total
          </span>
        </div>

        <div className="bg-white/5 backdrop-blur-sm p-4 rounded-xl border border-white/10">
          <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Daily Pace</span>
          <div className="text-2xl font-black text-indigo-300 mt-1">
            {formatCurrency(daily_burn_rate)}<span className="text-xs text-slate-400 font-normal">/day</span>
          </div>
          <span className="text-xs text-slate-400 mt-1 block">
            {days_remaining} days remaining
          </span>
        </div>

        <div className="bg-white/5 backdrop-blur-sm p-4 rounded-xl border border-white/10">
          <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Predicted Overspend</span>
          <div className={`text-2xl font-black mt-1 ${total_predicted_overspend > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
            {formatCurrency(total_predicted_overspend)}
          </div>
          <span className="text-xs text-slate-400 mt-1 block">
            {high_risk_count > 0 ? `${high_risk_count} high risk categories` : 'Within safe limits'}
          </span>
        </div>
      </div>

      {/* Progress timeline */}
      <div className="space-y-1.5 pt-1">
        <div className="flex justify-between text-xs text-slate-300">
          <span>Day {days_elapsed} of {days_in_month}</span>
          <span>{((days_elapsed / days_in_month) * 100).toFixed(0)}% of month completed</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden border border-white/10">
          <div
            className="bg-gradient-to-r from-indigo-500 to-amber-400 h-2.5 rounded-full transition-all duration-500"
            style={{ width: `${Math.min((days_elapsed / days_in_month) * 100, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default ForecastCard;
