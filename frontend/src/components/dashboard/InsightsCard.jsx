import { useNavigate } from 'react-router-dom';
import { ArrowRight, AlertTriangle, TrendingUp, TrendingDown, PiggyBank, Lightbulb, Info } from 'lucide-react';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
};

const getSeverityColor = (severity) => {
  switch (severity) {
    case 'warning':
      return 'text-amber-600 bg-amber-50 border-amber-200';
    case 'positive':
      return 'text-green-600 bg-green-50 border-green-200';
    case 'info':
    default:
      return 'text-blue-600 bg-blue-50 border-blue-200';
  }
};

const getTypeIcon = (type) => {
  switch (type) {
    case 'overspending':
      return AlertTriangle;
    case 'trend':
      return TrendingUp;
    case 'savings':
      return PiggyBank;
    case 'opportunity':
      return Lightbulb;
    case 'projection':
    default:
      return Info;
  }
};

const InsightCard = ({ insight }) => {
  const IconComponent = getTypeIcon(insight.type);
  const severityColor = getSeverityColor(insight.severity);

  return (
    <div className={`p-4 rounded-lg border ${severityColor} mb-3`}>
      <div className="flex items-start gap-3">
        <div className="mt-0.5">
          <IconComponent className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-sm mb-1">{insight.title}</h4>
          <p className="text-sm opacity-90">{insight.message}</p>
        </div>
      </div>
    </div>
  );
};

const InsightsCard = ({ insights, isLoading }) => {
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="mb-3">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  const items = insights || [];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Spending Insights</h3>
        <button
          onClick={() => navigate('/insights')}
          className="text-xs font-semibold text-primary-600 hover:text-primary-700 flex items-center gap-1 transition-colors"
        >
          View All Insights
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {items.length === 0 ? (
        <div className="text-gray-500 text-sm py-4">
          No insights available for this period.{' '}
          <button
            onClick={() => navigate('/insights')}
            className="text-primary-600 font-medium underline ml-1"
          >
            Explore Insights Engine
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {items.slice(0, 3).map((insight, index) => (
            <InsightCard key={index} insight={insight} />
          ))}
        </div>
      )}
    </div>
  );
};

export default InsightsCard;
