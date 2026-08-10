import { useState } from 'react';
import { Edit, Check, X, Info } from 'lucide-react';

const StatementPreviewTable = ({ transactions, onEdit, onToggleDuplicate }) => {
  const [expandedRow, setExpandedRow] = useState(null);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
  };

  const formatAmount = (amount, type) => {
    const formatted = new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
    
    return formatted;
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Food': 'bg-orange-100 text-orange-800',
      'Groceries': 'bg-green-100 text-green-800',
      'Transport': 'bg-blue-100 text-blue-800',
      'Shopping': 'bg-purple-100 text-purple-800',
      'Entertainment': 'bg-pink-100 text-pink-800',
      'Utilities': 'bg-yellow-100 text-yellow-800',
      'Bills': 'bg-red-100 text-red-800',
      'Healthcare': 'bg-teal-100 text-teal-800',
      'Education': 'bg-indigo-100 text-indigo-800',
      'Rent': 'bg-gray-100 text-gray-800',
      'Travel': 'bg-cyan-100 text-cyan-800',
      'Salary': 'bg-emerald-100 text-emerald-800',
      'Investment': 'bg-amber-100 text-amber-800',
      'Other': 'bg-gray-100 text-gray-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  if (transactions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="text-gray-400 mb-4">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No transactions to preview</h3>
        <p className="text-gray-500">Upload a bank statement to see transactions here</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Merchant
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Duplicate
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {transactions.map((transaction, index) => (
              <>
                <tr 
                  key={index} 
                  className={`hover:bg-gray-50 transition-colors ${
                    transaction.is_duplicate ? 'bg-yellow-50' : ''
                  }`}
                >
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(transaction.date)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    <div className="font-medium">{transaction.description}</div>
                    {transaction.error && (
                      <div className="text-red-500 text-xs mt-1">{transaction.error}</div>
                    )}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                    {transaction.merchant || '-'}
                  </td>
                  <td className={`px-4 py-3 whitespace-nowrap text-sm font-medium ${
                    transaction.transaction_type === 'income' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {transaction.transaction_type === 'income' ? '+' : '-'}
                    {formatAmount(transaction.amount)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                      transaction.transaction_type === 'income'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {transaction.transaction_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(transaction.category)}`}>
                        {transaction.category}
                      </span>
                      {transaction.category_source && transaction.category_source !== 'default' && (
                        <button
                          onClick={() => setExpandedRow(expandedRow === index ? null : index)}
                          className="text-gray-400 hover:text-gray-600"
                          title="View categorization details"
                        >
                          <Info className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-center">
                    {transaction.is_duplicate ? (
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-yellow-700">
                        <X className="w-3 h-3" />
                        Yes
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-green-700">
                        <Check className="w-3 h-3" />
                        No
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => onEdit(index)}
                        className="text-primary-600 hover:text-primary-900 transition-colors p-1 hover:bg-primary-50 rounded"
                        title="Edit"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
                {expandedRow === index && transaction.category_source && transaction.category_source !== 'default' && (
                  <tr className="bg-gray-50">
                    <td colSpan="8" className="px-4 py-3">
                      <div className="text-sm">
                        <div className="font-medium text-gray-900 mb-2">Categorization Details</div>
                        <div className="grid grid-cols-2 gap-4 text-gray-600">
                          <div>
                            <span className="font-medium">Category:</span> {transaction.category}
                          </div>
                          <div>
                            <span className="font-medium">Confidence:</span> {transaction.category_confidence ? `${(transaction.category_confidence * 100).toFixed(0)}%` : 'N/A'}
                          </div>
                          <div>
                            <span className="font-medium">Source:</span> {transaction.category_source === 'rule' ? 'Automatic Rule' : transaction.category_source}
                          </div>
                          <div>
                            <span className="font-medium">Reason:</span> {transaction.category_reason || 'N/A'}
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StatementPreviewTable;
