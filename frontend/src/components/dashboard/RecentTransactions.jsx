import { useNavigate } from 'react-router-dom';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
};

const RecentTransactions = ({ transactions, isLoading }) => {
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="mb-3">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!transactions || transactions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Transactions</h3>
        <div className="text-gray-500">No recent transactions</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Recent Transactions</h3>
        <button
          onClick={() => navigate('/transactions')}
          className="text-primary-600 hover:text-primary-900 text-sm font-medium"
        >
          View All
        </button>
      </div>
      <div className="space-y-3">
        {transactions.slice(0, 5).map((transaction) => (
          <div key={transaction.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
            <div className="flex-1">
              <div className="font-medium text-gray-900">{transaction.description}</div>
              <div className="text-sm text-gray-500">
                {transaction.merchant && <span>{transaction.merchant} • </span>}
                <span className="text-xs">{transaction.category}</span>
              </div>
            </div>
            <div className="text-right">
              <div className={`font-medium ${
                transaction.transaction_type === 'income' ? 'text-green-600' : 'text-red-600'
              }`}>
                {transaction.transaction_type === 'income' ? '+' : '-'}
                {formatCurrency(transaction.amount)}
              </div>
              <div className="text-xs text-gray-500">{formatDate(transaction.date)}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecentTransactions;
