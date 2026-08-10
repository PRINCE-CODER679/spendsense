import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Lightbulb, 
  Sparkles, 
  Target, 
  PieChart, 
  PiggyBank 
} from 'lucide-react';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount || 0);
};

const getInsightStyling = (type, severity, direction) => {
  // Severity colors
  if (severity === 'warning' || type === 'overspending') {
    return {
      cardBorder: 'border-rose-200 hover:border-rose-300',
      badgeBg: 'bg-rose-50 text-rose-700 border-rose-200',
      iconBg: 'bg-rose-100 text-rose-600',
      Icon: AlertTriangle,
    };
  }

  if (severity === 'positive' || direction === 'decreasing') {
    return {
      cardBorder: 'border-emerald-200 hover:border-emerald-300',
      badgeBg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      iconBg: 'bg-emerald-100 text-emerald-600',
      Icon: TrendingDown,
    };
  }

  if (type === 'savings') {
    return {
      cardBorder: 'border-indigo-200 hover:border-indigo-300',
      badgeBg: 'bg-indigo-50 text-indigo-700 border-indigo-200',
      iconBg: 'bg-indigo-100 text-indigo-600',
      Icon: PiggyBank,
    };
  }

  if (type === 'opportunity') {
    return {
      cardBorder: 'border-amber-200 hover:border-amber-300',
      badgeBg: 'bg-amber-50 text-amber-700 border-amber-200',
      iconBg: 'bg-amber-100 text-amber-600',
      Icon: Sparkles,
    };
  }

  if (type === 'projection' || type === 'budget_projection') {
    return {
      cardBorder: 'border-blue-200 hover:border-blue-300',
      badgeBg: 'bg-blue-50 text-blue-700 border-blue-200',
      iconBg: 'bg-blue-100 text-blue-600',
      Icon: Target,
    };
  }

  return {
    cardBorder: 'border-gray-200 hover:border-gray-300',
    badgeBg: 'bg-gray-50 text-gray-700 border-gray-200',
    iconBg: 'bg-gray-100 text-gray-600',
    Icon: Lightbulb,
  };
};

const InsightCardItem = ({ insight }) => {
  const {
    type,
    severity,
    category,
    title,
    message,
    value,
    projected_value,
    comparison_value,
    potential_savings,
    percentage_change,
    direction,
    savings_rate,
    budget_amount,
  } = insight;

  const style = getInsightStyling(type, severity, direction);
  const Icon = style.Icon;

  return (
    <div className={`bg-white rounded-xl shadow-sm border ${style.cardBorder} transition-all p-5 flex flex-col justify-between hover:shadow-md`}>
      <div>
        {/* Category & Badge Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5">
            <div className={`p-2 rounded-xl ${style.iconBg}`}>
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                {category || 'Overall'}
              </span>
              <h4 className="font-bold text-gray-900 text-base leading-tight">
                {title}
              </h4>
            </div>
          </div>
          <span className={`px-2.5 py-1 rounded-full text-xs font-bold border uppercase ${style.badgeBg}`}>
            {type.replace('_', ' ')}
          </span>
        </div>

        {/* Message */}
        <p className="text-sm text-gray-600 my-3 leading-relaxed">
          {message}
        </p>

        {/* Metric Highlights */}
        <div className="grid grid-cols-2 gap-3 mt-4 pt-3 border-t border-gray-100 text-xs">
          {value !== undefined && (
            <div>
              <span className="text-gray-400 block font-medium">Current Value</span>
              <span className="font-bold text-gray-900 text-sm">{formatCurrency(value)}</span>
            </div>
          )}

          {projected_value !== undefined && (
            <div>
              <span className="text-gray-400 block font-medium">Projected End of Month</span>
              <span className="font-bold text-blue-600 text-sm">{formatCurrency(projected_value)}</span>
            </div>
          )}

          {comparison_value !== undefined && (
            <div>
              <span className="text-gray-400 block font-medium">Historical Average</span>
              <span className="font-bold text-gray-700 text-sm">{formatCurrency(comparison_value)}</span>
            </div>
          )}

          {potential_savings !== undefined && (
            <div>
              <span className="text-gray-400 block font-medium">Potential Savings</span>
              <span className="font-bold text-amber-600 text-sm">{formatCurrency(potential_savings)}</span>
            </div>
          )}

          {savings_rate !== undefined && (
            <div>
              <span className="text-gray-400 block font-medium">Savings Rate</span>
              <span className="font-bold text-indigo-600 text-sm">{savings_rate.toFixed(1)}%</span>
            </div>
          )}

          {budget_amount !== undefined && (
            <div>
              <span className="text-gray-400 block font-medium">Budget Limit</span>
              <span className="font-bold text-gray-700 text-sm">{formatCurrency(budget_amount)}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InsightCardItem;
