import { useState, useEffect } from 'react';
import { 
  Lightbulb, 
  TrendingUp, 
  Target, 
  PiggyBank, 
  Sparkles, 
  AlertCircle, 
  RefreshCw, 
  ChevronLeft, 
  ChevronRight,
  TrendingDown,
  Calendar,
  Wallet
} from 'lucide-react';
import insightsService from '../services/insightsService';
import forecastService from '../services/forecastService';
import anomalyService from '../services/anomalyService';
import InsightCardItem from '../components/insights/InsightCardItem';
import ForecastCard from '../components/dashboard/ForecastCard';
import CategoryForecastList from '../components/dashboard/CategoryForecastList';
import AnomalyAlertsCard from '../components/dashboard/AnomalyAlertsCard';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount || 0);
};

const Insights = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [allInsightsData, setAllInsightsData] = useState(null);
  const [forecastSummary, setForecastSummary] = useState(null);
  const [anomalySummary, setAnomalySummary] = useState(null);
  const [activeTab, setActiveTab] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1;

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  useEffect(() => {
    fetchInsights();
  }, [currentYear, currentMonth]);

  const fetchInsights = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [insightsData, forecastData, anomalyData] = await Promise.all([
        insightsService.getAllInsights(currentYear, currentMonth),
        forecastService.getForecastSummary(currentYear, currentMonth).catch(() => null),
        anomalyService.getAnomalySummary(currentYear, currentMonth).catch(() => null)
      ]);
      setAllInsightsData(insightsData);
      setForecastSummary(forecastData);
      setAnomalySummary(anomalyData);
    } catch (err) {
      console.error('Failed to load insights:', err);
      setError('Failed to fetch spending insights. Please try again later.');
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

  // Combine category, savings, and projection into unified list
  const categoryInsights = allInsightsData?.category_insights || [];
  const savingsInsights = allInsightsData?.savings_insights || [];
  const projectionInsight = allInsightsData?.projection ? [allInsightsData.projection] : [];
  const summary = allInsightsData?.summary;

  const allInsightsList = [
    ...projectionInsight,
    ...categoryInsights,
    ...savingsInsights,
  ];

  // Filter insights by active tab
  const filteredInsights = allInsightsList.filter((item) => {
    if (activeTab === 'all') return true;
    if (activeTab === 'projections') return item.type === 'projection' || item.type === 'budget_projection';
    if (activeTab === 'trends') return item.type === 'overspending' || item.type === 'trend';
    if (activeTab === 'savings') return item.type === 'savings' || item.type === 'opportunity';
    if (activeTab === 'budget') return item.type === 'budget' || item.type === 'budget_projection';
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header with Title & Month Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Spending Insights Engine</h1>
          <p className="text-sm text-gray-500 mt-1">
            Rule-based financial analytics, trends, savings opportunities, and spending projections.
          </p>
        </div>

        {/* Month/Year Navigation */}
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
      </div>

      {/* Financial Summary Top Cards */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Total Income</span>
            <div className="text-2xl font-black text-emerald-600 mt-1">
              {formatCurrency(summary.income)}
            </div>
            <span className="text-xs text-gray-400 mt-1 block">Earned this month</span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Total Expenses</span>
            <div className="text-2xl font-black text-gray-900 mt-1">
              {formatCurrency(summary.expenses)}
            </div>
            <span className="text-xs text-gray-400 mt-1 block">Spent this month</span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Net Savings</span>
            <div className={`text-2xl font-black mt-1 ${summary.savings >= 0 ? 'text-indigo-600' : 'text-rose-600'}`}>
              {formatCurrency(summary.savings)}
            </div>
            <span className="text-xs text-gray-400 mt-1 block">Income - Expenses</span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Savings Rate</span>
            <div className="text-2xl font-black text-primary-600 mt-1">
              {summary.savings_rate.toFixed(1)}%
            </div>
            <span className="text-xs text-gray-400 mt-1 block">Percentage of income saved</span>
          </div>
        </div>
      )}

      {/* Phase 7 Forecast Banner */}
      <ForecastCard forecastSummary={forecastSummary} isLoading={isLoading} />

      {/* Phase 8 Anomaly Alerts */}
      <AnomalyAlertsCard anomalySummary={anomalySummary} isLoading={isLoading} />

      {/* Category Risk Matrix Forecasts */}
      {forecastSummary?.category_forecasts?.length > 0 && (
        <CategoryForecastList forecasts={forecastSummary.category_forecasts} isLoading={isLoading} />
      )}

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-gray-200 pb-1 overflow-x-auto">
        <button
          onClick={() => setActiveTab('all')}
          className={`px-4 py-2 text-sm font-semibold rounded-lg transition-colors whitespace-nowrap ${
            activeTab === 'all'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
          }`}
        >
          All Insights ({allInsightsList.length})
        </button>

        <button
          onClick={() => setActiveTab('projections')}
          className={`px-4 py-2 text-sm font-semibold rounded-lg transition-colors whitespace-nowrap ${
            activeTab === 'projections'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
          }`}
        >
          Projections
        </button>

        <button
          onClick={() => setActiveTab('trends')}
          className={`px-4 py-2 text-sm font-semibold rounded-lg transition-colors whitespace-nowrap ${
            activeTab === 'trends'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
          }`}
        >
          Overspending & Trends
        </button>

        <button
          onClick={() => setActiveTab('savings')}
          className={`px-4 py-2 text-sm font-semibold rounded-lg transition-colors whitespace-nowrap ${
            activeTab === 'savings'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
          }`}
        >
          Savings & Opportunities
        </button>

        <button
          onClick={() => setActiveTab('budget')}
          className={`px-4 py-2 text-sm font-semibold rounded-lg transition-colors whitespace-nowrap ${
            activeTab === 'budget'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
          }`}
        >
          Budget Insights
        </button>
      </div>

      {/* Main Insights Content Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 animate-pulse h-48" />
          ))}
        </div>
      ) : error ? (
        <div className="bg-white rounded-2xl shadow-sm border border-red-100 p-8 text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-gray-900 mb-1">Failed to Load Insights</h3>
          <p className="text-sm text-gray-500 mb-4">{error}</p>
          <button
            onClick={fetchInsights}
            className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-semibold rounded-xl hover:bg-primary-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </div>
      ) : filteredInsights.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
          <div className="w-16 h-16 bg-amber-50 text-amber-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Lightbulb className="w-8 h-8" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">No Insights Available</h3>
          <p className="text-gray-500 text-sm max-w-md mx-auto">
            {activeTab === 'all'
              ? `There are no spending insights for ${monthNames[currentMonth - 1]} ${currentYear} yet. Add transactions or set budgets to generate rules-based financial analytics.`
              : `No insights matching the selected category for this period.`}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredInsights.map((insight, index) => (
            <InsightCardItem key={index} insight={insight} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Insights;
