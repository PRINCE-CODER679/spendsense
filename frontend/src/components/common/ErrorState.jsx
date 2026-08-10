import { AlertCircle, RefreshCw, WifiOff } from 'lucide-react';

export const ErrorState = ({ 
  title = "Failed to load financial data", 
  message = "Please check your network connection or server status and try again.", 
  onRetry 
}) => {
  const isOffline = typeof navigator !== 'undefined' && !navigator.onLine;

  return (
    <div className="bg-rose-50/70 border border-rose-200/80 rounded-2xl p-6 text-center shadow-sm max-w-xl mx-auto space-y-4 my-6">
      <div className="w-12 h-12 bg-rose-100 text-rose-600 rounded-2xl flex items-center justify-center mx-auto">
        {isOffline ? <WifiOff className="w-6 h-6" /> : <AlertCircle className="w-6 h-6" />}
      </div>

      <div>
        <h3 className="text-base font-bold text-gray-900">
          {isOffline ? "You are currently offline" : title}
        </h3>
        <p className="text-xs text-gray-600 mt-1 max-w-md mx-auto leading-relaxed">
          {isOffline ? "Network connection lost. Reconnect to sync with SpendSense AI backend." : message}
        </p>
      </div>

      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-2" />
          Try Again
        </button>
      )}
    </div>
  );
};

export default ErrorState;
