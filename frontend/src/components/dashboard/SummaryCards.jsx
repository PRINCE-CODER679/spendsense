const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
};

const SummaryCards = ({ summary, isLoading }) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Total Income */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-sm font-medium text-gray-600 mb-2">Total Income</div>
        <div className="text-2xl font-bold text-green-600">
          {formatCurrency(summary.total_income)}
        </div>
        <div className="text-xs text-gray-500 mt-1">Income this month</div>
      </div>

      {/* Total Expenses */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-sm font-medium text-gray-600 mb-2">Total Expenses</div>
        <div className="text-2xl font-bold text-red-600">
          {formatCurrency(summary.total_expenses)}
        </div>
        <div className="text-xs text-gray-500 mt-1">Expenses this month</div>
      </div>

      {/* Savings */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-sm font-medium text-gray-600 mb-2">Savings</div>
        <div className={`text-2xl font-bold ${summary.total_savings >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
          {formatCurrency(summary.total_savings)}
        </div>
        <div className="text-xs text-gray-500 mt-1">Available after expenses</div>
      </div>

      {/* Savings Rate */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-sm font-medium text-gray-600 mb-2">Savings Rate</div>
        <div className="text-2xl font-bold text-purple-600">
          {summary.savings_rate.toFixed(1)}%
        </div>
        <div className="text-xs text-gray-500 mt-1">Percentage of income saved</div>
      </div>
    </div>
  );
};

export default SummaryCards;
