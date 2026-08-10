import { ChevronLeft, ChevronRight } from 'lucide-react';

const MonthSelector = ({ currentYear, currentMonth, onPreviousMonth, onNextMonth }) => {
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const monthName = monthNames[currentMonth - 1];

  return (
    <div className="flex items-center justify-between bg-white rounded-lg shadow p-4">
      <button
        onClick={onPreviousMonth}
        className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <ChevronLeft className="w-5 h-5" />
        Previous
      </button>
      
      <div className="text-lg font-semibold text-gray-900">
        {monthName} {currentYear}
      </div>
      
      <button
        onClick={onNextMonth}
        className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
      >
        Next
        <ChevronRight className="w-5 h-5" />
      </button>
    </div>
  );
};

export default MonthSelector;
