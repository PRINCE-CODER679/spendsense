import { Pencil, Trash2, CheckCircle2, AlertTriangle, AlertOctagon, TrendingUp } from 'lucide-react';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount || 0);
};

const getStatusBadge = (status) => {
  const normalized = (status || '').toLowerCase();
  switch (normalized) {
    case 'safe':
      return {
        label: 'SAFE',
        bgColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        barColor: 'bg-emerald-500',
        Icon: CheckCircle2,
      };
    case 'warning':
      return {
        label: 'WARNING',
        bgColor: 'bg-amber-50 text-amber-700 border-amber-200',
        barColor: 'bg-amber-500',
        Icon: TrendingUp,
      };
    case 'near_limit':
      return {
        label: 'NEAR LIMIT',
        bgColor: 'bg-orange-50 text-orange-700 border-orange-200',
        barColor: 'bg-orange-500',
        Icon: AlertTriangle,
      };
    case 'exceeded':
      return {
        label: 'EXCEEDED',
        bgColor: 'bg-rose-50 text-rose-700 border-rose-200',
        barColor: 'bg-rose-600',
        Icon: AlertOctagon,
      };
    default:
      return {
        label: 'UNKNOWN',
        bgColor: 'bg-gray-50 text-gray-700 border-gray-200',
        barColor: 'bg-gray-400',
        Icon: CheckCircle2,
      };
  }
};

const BudgetCardItem = ({ budget, onEdit, onDelete }) => {
  const {
    category,
    budget_amount,
    actual_spending,
    remaining,
    percentage_used,
    is_over_budget,
    over_budget_amount,
    status,
  } = budget;

  const badge = getStatusBadge(status);
  const StatusIcon = badge.Icon;
  const isOverall = !category;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow p-5 flex flex-col justify-between">
      <div>
        {/* Header: Title and Status Badge */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className={`p-2 rounded-lg ${isOverall ? 'bg-primary-50 text-primary-600' : 'bg-gray-100 text-gray-700'}`}>
              <StatusIcon className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-gray-900 text-base">
                {category || 'Overall Monthly Budget'}
              </h4>
              <span className="text-xs text-gray-500 font-medium">
                {isOverall ? 'Total Expense Limit' : 'Category Budget'}
              </span>
            </div>
          </div>

          <span
            className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold border ${badge.bgColor}`}
          >
            {badge.label}
          </span>
        </div>

        {/* Amount Stats */}
        <div className="grid grid-cols-2 gap-4 my-4 p-3 bg-gray-50/70 rounded-lg">
          <div>
            <span className="block text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Budget
            </span>
            <span className="text-lg font-extrabold text-gray-900">
              {formatCurrency(budget_amount)}
            </span>
          </div>
          <div>
            <span className="block text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Spent
            </span>
            <span className="text-lg font-extrabold text-gray-900">
              {formatCurrency(actual_spending)}
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-3">
          <div className="flex justify-between text-xs font-medium text-gray-600 mb-1.5">
            <span>Utilization</span>
            <span className={is_over_budget ? 'text-rose-600 font-bold' : 'text-gray-700 font-bold'}>
              {percentage_used.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
            <div
              className={`h-2.5 rounded-full transition-all duration-500 ${badge.barColor}`}
              style={{ width: `${Math.min(percentage_used, 100)}%` }}
            />
          </div>
        </div>

        {/* Remaining or Over-budget Notice */}
        <div className="text-xs font-semibold">
          {is_over_budget ? (
            <span className="text-rose-600 flex items-center gap-1">
              <AlertOctagon className="w-4 h-4 inline" /> Exceeded budget by {formatCurrency(over_budget_amount)}
            </span>
          ) : (
            <span className="text-emerald-600 flex items-center gap-1">
              <CheckCircle2 className="w-4 h-4 inline" /> {formatCurrency(remaining)} remaining
            </span>
          )}
        </div>
      </div>

      {/* Action Footer */}
      <div className="flex items-center justify-end gap-2 pt-4 mt-4 border-t border-gray-100">
        <button
          onClick={() => onEdit(budget)}
          className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <Pencil className="w-3.5 h-3.5" />
          Edit
        </button>
        <button
          onClick={() => onDelete(budget)}
          className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-rose-600 bg-rose-50 hover:bg-rose-100 rounded-lg transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Delete
        </button>
      </div>
    </div>
  );
};

export default BudgetCardItem;
