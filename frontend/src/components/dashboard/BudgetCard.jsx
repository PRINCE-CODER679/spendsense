import { useNavigate } from 'react-router-dom';
import { ArrowRight, AlertCircle, CheckCircle, TrendingUp, DollarSign } from 'lucide-react';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
};

const getStatusColor = (status) => {
  switch (status) {
    case 'safe':
      return 'text-green-600 bg-green-50 border-green-200';
    case 'warning':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'near_limit':
      return 'text-orange-600 bg-orange-50 border-orange-200';
    case 'exceeded':
      return 'text-red-600 bg-red-50 border-red-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

const getStatusIcon = (status) => {
  switch (status) {
    case 'safe':
      return CheckCircle;
    case 'warning':
      return TrendingUp;
    case 'near_limit':
      return AlertCircle;
    case 'exceeded':
      return AlertCircle;
    default:
      return DollarSign;
  }
};

const getProgressColor = (percentage) => {
  if (percentage >= 100) return 'bg-red-500';
  if (percentage >= 90) return 'bg-orange-500';
  if (percentage >= 70) return 'bg-yellow-500';
  return 'bg-green-500';
};

const BudgetItem = ({ budget }) => {
  const StatusIcon = getStatusIcon(budget.status);
  const statusColor = getStatusColor(budget.status);
  const progressColor = getProgressColor(budget.percentage_used);
  const isOverBudget = budget.is_over_budget;

  return (
    <div className={`p-4 rounded-lg border ${statusColor} mb-3`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <StatusIcon className="w-5 h-5" />
          <h4 className="font-semibold text-sm">
            {budget.category || 'Overall Budget'}
          </h4>
        </div>
        <span className="text-sm font-medium">
          {budget.percentage_used.toFixed(1)}%
        </span>
      </div>

      <div className="mb-2">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-600">
            Spent: {formatCurrency(budget.actual_spending)}
          </span>
          <span className="text-gray-600">
            Budget: {formatCurrency(budget.budget_amount)}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`${progressColor} h-2 rounded-full transition-all`}
            style={{ width: `${Math.min(budget.percentage_used, 100)}%` }}
          />
        </div>
      </div>

      <div className="text-xs">
        {isOverBudget ? (
          <span className="text-red-600 font-medium">
            Over budget by {formatCurrency(budget.over_budget_amount)}
          </span>
        ) : (
          <span className="text-green-600">
            {formatCurrency(budget.remaining)} remaining
          </span>
        )}
      </div>
    </div>
  );
};

const BudgetCard = ({ budgetAnalysis, isLoading }) => {
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="mb-3">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-2 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  const { overall_budget, category_budgets } = budgetAnalysis || {};
  const allBudgets = [...(overall_budget ? [overall_budget] : []), ...(category_budgets || [])];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Budget Overview</h3>
        <button
          onClick={() => navigate('/budgets')}
          className="text-xs font-semibold text-primary-600 hover:text-primary-700 flex items-center gap-1 transition-colors"
        >
          Manage Budgets
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {allBudgets.length === 0 ? (
        <div className="text-gray-500 text-sm py-4">
          No budgets set for this month.{' '}
          <button
            onClick={() => navigate('/budgets')}
            className="text-primary-600 font-medium underline ml-1"
          >
            Create one now
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {allBudgets.map((budget, index) => (
            <BudgetItem key={index} budget={budget} />
          ))}
        </div>
      )}
    </div>
  );
};

export default BudgetCard;
