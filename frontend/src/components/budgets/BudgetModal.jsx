import { useState, useEffect } from 'react';
import { X, AlertCircle } from 'lucide-react';

const STANDARD_CATEGORIES = [
  { value: '', label: 'Overall Monthly Budget' },
  { value: 'Food', label: 'Food & Dining' },
  { value: 'Housing', label: 'Housing / Rent' },
  { value: 'Utilities', label: 'Utilities & Bills' },
  { value: 'Transportation', label: 'Transportation' },
  { value: 'Entertainment', label: 'Entertainment' },
  { value: 'Healthcare', label: 'Healthcare' },
  { value: 'Shopping', label: 'Shopping' },
  { value: 'Education', label: 'Education' },
  { value: 'Personal Care', label: 'Personal Care' },
  { value: 'Subscriptions', label: 'Subscriptions' },
  { value: 'Other', label: 'Other' },
];

const BudgetModal = ({ isOpen, onClose, onSave, initialData = null, activeYear, activeMonth }) => {
  const [category, setCategory] = useState('');
  const [amount, setAmount] = useState('');
  const [year, setYear] = useState(activeYear || new Date().getFullYear());
  const [month, setMonth] = useState(activeMonth || new Date().getMonth() + 1);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isEditing = Boolean(initialData && initialData.budget_id);

  useEffect(() => {
    if (initialData) {
      setCategory(initialData.category || '');
      setAmount(initialData.budget_amount || initialData.amount || '');
      setYear(initialData.year || activeYear || new Date().getFullYear());
      setMonth(initialData.month || activeMonth || new Date().getMonth() + 1);
    } else {
      setCategory('');
      setAmount('');
      setYear(activeYear || new Date().getFullYear());
      setMonth(activeMonth || new Date().getMonth() + 1);
    }
    setError(null);
  }, [initialData, isOpen, activeYear, activeMonth]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const numericAmount = parseFloat(amount);
    if (isNaN(numericAmount) || numericAmount <= 0) {
      setError('Please enter a valid budget amount greater than 0.');
      return;
    }

    setIsSubmitting(true);
    try {
      if (isEditing) {
        await onSave({
          id: initialData.budget_id || initialData.id,
          amount: numericAmount,
        });
      } else {
        await onSave({
          category: category === '' ? null : category,
          amount: numericAmount,
          year: parseInt(year, 10),
          month: parseInt(month, 10),
        });
      }
      onClose();
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Failed to save budget. Please try again.';
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50/50">
          <h3 className="text-lg font-bold text-gray-900">
            {isEditing ? 'Edit Budget' : 'Create New Budget'}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-gray-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="flex items-start gap-3 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Category Selection */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-1">
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              disabled={isEditing}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none text-sm ${
                isEditing ? 'bg-gray-100 text-gray-500 cursor-not-allowed border-gray-200' : 'border-gray-300'
              }`}
            >
              {STANDARD_CATEGORIES.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          {/* Amount Field */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-1">
              Budget Amount (₹)
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-500 font-semibold">
                ₹
              </span>
              <input
                type="number"
                step="0.01"
                min="1"
                placeholder="5000"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
                className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none text-sm font-medium text-gray-900"
              />
            </div>
          </div>

          {/* Month & Year Selectors (only when creating) */}
          {!isEditing && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-1">
                  Month
                </label>
                <select
                  value={month}
                  onChange={(e) => setMonth(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none text-sm"
                >
                  {monthNames.map((m, idx) => (
                    <option key={idx + 1} value={idx + 1}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-1">
                  Year
                </label>
                <input
                  type="number"
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                  min="2020"
                  max="2100"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none text-sm"
                />
              </div>
            </div>
          )}

          {/* Footer Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors shadow-sm disabled:opacity-50"
            >
              {isSubmitting ? 'Saving...' : isEditing ? 'Save Changes' : 'Create Budget'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BudgetModal;
