import { useState, useEffect } from 'react';
import { Plus, Wallet, AlertCircle, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import budgetService from '../services/budgetService';
import BudgetCardItem from '../components/budgets/BudgetCardItem';
import BudgetModal from '../components/budgets/BudgetModal';
import DeleteConfirmDialog from '../components/DeleteConfirmDialog';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount || 0);
};

const Budgets = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [budgetAnalysis, setBudgetAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingBudget, setEditingBudget] = useState(null);

  // Delete confirm states
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [deletingBudget, setDeletingBudget] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1;

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  useEffect(() => {
    fetchBudgets();
  }, [currentYear, currentMonth]);

  const fetchBudgets = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await budgetService.getBudgetAnalysis(currentYear, currentMonth);
      setBudgetAnalysis(data);
    } catch (err) {
      console.error('Failed to load budgets:', err);
      setError('Failed to fetch budget data. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreviousMonth = () => {
    if (currentMonth === 1) {
      setCurrentDate(new Date(currentYear - 1, 11, 1));
    } else {
      setCurrentDate(new Date(currentYear, currentMonth - 2, 1));
    }
  };

  const handleNextMonth = () => {
    const nextMonth = new Date(currentYear, currentMonth - 1, 1);
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    setCurrentDate(nextMonth);
  };

  const handleOpenCreateModal = () => {
    setEditingBudget(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (budget) => {
    setEditingBudget(budget);
    setIsModalOpen(true);
  };

  const handleSaveBudget = async (budgetData) => {
    if (editingBudget) {
      await budgetService.updateBudget(budgetData.id, { amount: budgetData.amount });
    } else {
      await budgetService.createBudget(budgetData);
    }
    fetchBudgets();
  };

  const handleOpenDeleteDialog = (budget) => {
    setDeletingBudget(budget);
    setIsDeleteOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!deletingBudget) return;
    setIsDeleting(true);
    try {
      await budgetService.deleteBudget(deletingBudget.budget_id || deletingBudget.id);
      setIsDeleteOpen(false);
      setDeletingBudget(null);
      fetchBudgets();
    } catch (err) {
      console.error('Failed to delete budget:', err);
      alert(err.response?.data?.detail || 'Failed to delete budget.');
    } finally {
      setIsDeleting(false);
    }
  };

  const overall = budgetAnalysis?.overall_budget;
  const categories = budgetAnalysis?.category_budgets || [];
  const allBudgetsList = [...(overall ? [overall] : []), ...categories];

  // Calculate totals across category budgets if no explicit overall budget is set
  const totalBudgeted = overall
    ? overall.budget_amount
    : categories.reduce((sum, b) => sum + b.budget_amount, 0);

  const totalSpent = overall
    ? overall.actual_spending
    : categories.reduce((sum, b) => sum + b.actual_spending, 0);

  const totalRemaining = totalBudgeted - totalSpent;
  const overallUtil = totalBudgeted > 0 ? (totalSpent / totalBudgeted) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Header with Title and Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Budget Management</h1>
          <p className="text-sm text-gray-500 mt-1">
            Set, monitor, and manage your monthly spending limits.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Month/Year selector */}
          <div className="flex items-center bg-white border border-gray-200 rounded-xl p-1 shadow-sm">
            <button
              onClick={handlePreviousMonth}
              className="p-2 hover:bg-gray-100 rounded-lg text-gray-600 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="px-3 font-semibold text-sm text-gray-800 min-w-[120px] text-center">
              {monthNames[currentMonth - 1]} {currentYear}
            </span>
            <button
              onClick={handleNextMonth}
              className="p-2 hover:bg-gray-100 rounded-lg text-gray-600 transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          <button
            onClick={handleOpenCreateModal}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold rounded-xl transition-all shadow-sm"
          >
            <Plus className="w-5 h-5" />
            Add Budget
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Total Monthly Budget</span>
          <div className="text-2xl font-black text-gray-900 mt-2">
            {formatCurrency(totalBudgeted)}
          </div>
          <span className="text-xs text-gray-400 mt-1">
            {overall ? 'Overall Limit Set' : `${categories.length} Category Budgets`}
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Total Spent</span>
          <div className="text-2xl font-black text-gray-900 mt-2">
            {formatCurrency(totalSpent)}
          </div>
          <span className="text-xs text-gray-400 mt-1">
            Actual Spending
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Remaining Budget</span>
          <div className={`text-2xl font-black mt-2 ${totalRemaining >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
            {formatCurrency(totalRemaining)}
          </div>
          <span className="text-xs text-gray-400 mt-1">
            {totalRemaining >= 0 ? 'Available to spend' : 'Over budget'}
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Overall Utilization</span>
          <div className="text-2xl font-black text-gray-900 mt-2">
            {overallUtil.toFixed(1)}%
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div
              className={`h-2 rounded-full transition-all ${
                overallUtil >= 100 ? 'bg-rose-500' : overallUtil >= 90 ? 'bg-orange-500' : overallUtil >= 70 ? 'bg-amber-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(overallUtil, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Main Budget Grid / List */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 animate-pulse h-48" />
          ))}
        </div>
      ) : error ? (
        <div className="bg-white rounded-2xl shadow-sm border border-red-100 p-8 text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-gray-900 mb-1">Failed to Load Budgets</h3>
          <p className="text-sm text-gray-500 mb-4">{error}</p>
          <button
            onClick={fetchBudgets}
            className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-semibold rounded-xl hover:bg-primary-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </div>
      ) : allBudgetsList.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
          <div className="w-16 h-16 bg-primary-50 text-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Wallet className="w-8 h-8" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">No Budgets Found</h3>
          <p className="text-gray-500 text-sm max-w-md mx-auto mb-6">
            You don't have any budgets set for {monthNames[currentMonth - 1]} {currentYear}. Create a category budget or an overall monthly limit to start tracking.
          </p>
          <button
            onClick={handleOpenCreateModal}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors shadow-sm"
          >
            <Plus className="w-5 h-5" />
            Create First Budget
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-gray-900">
            Active Budgets ({allBudgetsList.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {allBudgetsList.map((budget, index) => (
              <BudgetCardItem
                key={budget.budget_id || index}
                budget={budget}
                onEdit={handleOpenEditModal}
                onDelete={handleOpenDeleteDialog}
              />
            ))}
          </div>
        </div>
      )}

      {/* Create / Edit Modal */}
      <BudgetModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveBudget}
        initialData={editingBudget}
        activeYear={currentYear}
        activeMonth={currentMonth}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={handleConfirmDelete}
        title="Delete Budget"
        message={`Are you sure you want to delete the budget for "${
          deletingBudget?.category || 'Overall Monthly Budget'
        }"?`}
        isLoading={isDeleting}
      />
    </div>
  );
};

export default Budgets;
