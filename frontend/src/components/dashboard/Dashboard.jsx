import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Upload } from 'lucide-react';
import MonthSelector from './MonthSelector';
import SummaryCards from './SummaryCards';
import CategorySpendingChart from './CategorySpendingChart';
import IncomeExpenseChart from './IncomeExpenseChart';
import DailySpendingChart from './DailySpendingChart';
import TopCategories from './TopCategories';
import RecentTransactions from './RecentTransactions';
import InsightsCard from './InsightsCard';
import BudgetCard from './BudgetCard';
import DashboardSkeleton from './DashboardSkeleton';
import ForecastCard from './ForecastCard';
import CategoryForecastList from './CategoryForecastList';
import AnomalyAlertsCard from './AnomalyAlertsCard';
import { dashboardService } from '../../services/dashboardService';
import { transactionService } from '../../services/transactionService';
import insightsService from '../../services/insightsService';
import budgetService from '../../services/budgetService';
import forecastService from '../../services/forecastService';
import anomalyService from '../../services/anomalyService';

const Dashboard = () => {
  const navigate = useNavigate();
  
  const [currentDate, setCurrentDate] = useState(new Date());
  const [summary, setSummary] = useState(null);
  const [categorySpending, setCategorySpending] = useState(null);
  const [monthlyTrend, setMonthlyTrend] = useState(null);
  const [dailySpending, setDailySpending] = useState(null);
  const [topCategories, setTopCategories] = useState(null);
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [monthComparison, setMonthComparison] = useState(null);
  const [insights, setInsights] = useState(null);
  const [budgetAnalysis, setBudgetAnalysis] = useState(null);
  const [forecastSummary, setForecastSummary] = useState(null);
  const [anomalySummary, setAnomalySummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1;

  useEffect(() => {
    fetchDashboardData();
  }, [currentYear, currentMonth]);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const [summaryData, categoryData, trendData, dailyData, topCatData, comparisonData, transactionsData, insightsData, budgetData, forecastData, anomalyData] = await Promise.all([
        dashboardService.getDashboardSummary(currentYear, currentMonth),
        dashboardService.getCategorySpending(currentYear, currentMonth),
        dashboardService.getMonthlyTrend(6),
        dashboardService.getDailySpending(currentYear, currentMonth),
        dashboardService.getTopCategories(currentYear, currentMonth, 5),
        dashboardService.getMonthComparison(currentYear, currentMonth),
        transactionService.getTransactions({ limit: 5, sort_by: 'date', sort_order: 'desc' }),
        insightsService.getAllInsights(currentYear, currentMonth),
        budgetService.getBudgetAnalysis(currentYear, currentMonth),
        forecastService.getForecastSummary(currentYear, currentMonth).catch(() => null),
        anomalyService.getAnomalySummary(currentYear, currentMonth).catch(() => null)
      ]);

      setSummary(summaryData);
      setCategorySpending(categoryData);
      setMonthlyTrend(trendData);
      setDailySpending(dailyData);
      setTopCategories(topCatData);
      setMonthComparison(comparisonData);
      setRecentTransactions(transactionsData.transactions);
      setInsights(insightsData);
      setBudgetAnalysis(budgetData);
      setForecastSummary(forecastData);
      setAnomalySummary(anomalyData);
    } catch (err) {
      setError('Failed to load dashboard data. Please try again later.');
      console.error('Dashboard error:', err);
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
    const today = new Date();
    const nextMonth = new Date(currentYear, currentMonth - 1, 1);
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    
    // Don't allow going to future months
    if (nextMonth <= today) {
      setCurrentDate(nextMonth);
    }
  };

  const handleAddTransaction = () => {
    navigate('/transactions');
  };

  const handleUploadStatement = () => {
    navigate('/upload');
  };

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="text-red-500 mb-4">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Dashboard</h3>
        <p className="text-gray-500 mb-4">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  // Check if user has no transactions
  const hasNoData = !summary || summary.transaction_count === 0;

  if (hasNoData) {
    return (
      <div className="space-y-6">
        <MonthSelector
          currentYear={currentYear}
          currentMonth={currentMonth}
          onPreviousMonth={handlePreviousMonth}
          onNextMonth={handleNextMonth}
        />
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No financial data yet</h3>
          <p className="text-gray-500 mb-6">Add a transaction or upload a bank statement to start analyzing your spending.</p>
          <div className="flex justify-center gap-4">
            <button
              onClick={handleAddTransaction}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Plus className="w-5 h-5" />
              Add Transaction
            </button>
            <button
              onClick={handleUploadStatement}
              className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <Upload className="w-5 h-5" />
              Upload Statement
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Month Selector */}
      <MonthSelector
        currentYear={currentYear}
        currentMonth={currentMonth}
        onPreviousMonth={handlePreviousMonth}
        onNextMonth={handleNextMonth}
      />

      {/* Summary Cards */}
      <SummaryCards summary={summary} isLoading={isLoading} />

      {/* Phase 7 Forecast Banner */}
      <ForecastCard forecastSummary={forecastSummary} isLoading={isLoading} />

      {/* Phase 8 Anomaly Alerts */}
      <AnomalyAlertsCard anomalySummary={anomalySummary} isLoading={isLoading} />

      {/* Category Level Risk Forecasts */}
      {forecastSummary?.category_forecasts?.length > 0 && (
        <CategoryForecastList forecasts={forecastSummary.category_forecasts} isLoading={isLoading} />
      )}

      {/* Insights */}
      <InsightsCard 
        insights={insights?.category_insights || []} 
        isLoading={isLoading} 
      />

      {/* Budget */}
      <BudgetCard 
        budgetAnalysis={budgetAnalysis} 
        isLoading={isLoading} 
      />

      {/* Month Comparison */}
      {monthComparison && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Month Comparison</h3>
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-600">
              <span className="font-medium">Current month:</span> ₹{monthComparison.current_expenses.toLocaleString('en-IN')}
            </div>
            <div className="text-sm text-gray-600">
              <span className="font-medium">Previous month:</span> ₹{monthComparison.previous_expenses.toLocaleString('en-IN')}
            </div>
            <div className={`text-sm font-medium ${
              monthComparison.percentage_change >= 0 ? 'text-red-600' : 'text-green-600'
            }`}>
              {monthComparison.percentage_change >= 0 ? '+' : ''}
              {monthComparison.percentage_change.toFixed(1)}%
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Spending {monthComparison.percentage_change >= 0 ? 'increased' : 'decreased'} {Math.abs(monthComparison.percentage_change).toFixed(1)}% compared with {monthComparison.previous_month_name}
          </p>
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CategorySpendingChart categorySpending={categorySpending} isLoading={isLoading} />
        <IncomeExpenseChart monthlyTrend={monthlyTrend} isLoading={isLoading} />
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <DailySpendingChart dailySpending={dailySpending} isLoading={isLoading} />
        </div>
        <TopCategories topCategories={topCategories} isLoading={isLoading} />
      </div>

      {/* Recent Transactions */}
      <RecentTransactions transactions={recentTransactions} isLoading={isLoading} />
    </div>
  );
};

export default Dashboard;
