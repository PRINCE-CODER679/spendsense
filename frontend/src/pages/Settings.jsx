import { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  DollarSign, 
  Moon, 
  Sun, 
  Sliders, 
  Download, 
  Trash2, 
  CheckCircle, 
  AlertTriangle,
  RefreshCw,
  Info,
  ShieldCheck
} from 'lucide-react';
import settingsService from '../services/settingsService';
import { transactionService } from '../services/transactionService';

const CURRENCY_OPTIONS = [
  { symbol: '₹', code: 'INR', label: 'Indian Rupee (₹)' },
  { symbol: '$', code: 'USD', label: 'US Dollar ($)' },
  { symbol: '€', code: 'EUR', label: 'Euro (€)' },
  { symbol: '£', code: 'GBP', label: 'British Pound (£)' },
];

const Settings = () => {
  const [settings, setSettings] = useState(settingsService.getSettings());
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [showResetModal, setShowResetModal] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);

  useEffect(() => {
    const handleUpdate = () => {
      setSettings(settingsService.getSettings());
    };
    window.addEventListener('spendsense_settings_updated', handleUpdate);
    return () => window.removeEventListener('spendsense_settings_updated', handleUpdate);
  }, []);

  const handleCurrencyChange = (curr) => {
    const updated = settingsService.saveSettings({ currency: curr.symbol, currencyCode: curr.code });
    if (updated) showNotification();
  };

  const handleThemeToggle = () => {
    const newTheme = settings.theme === 'dark' ? 'light' : 'dark';
    const updated = settingsService.saveSettings({ theme: newTheme });
    if (updated) showNotification();
  };

  const handleThresholdChange = (key, value) => {
    const val = parseInt(value, 10);
    const updated = settingsService.saveSettings({ [key]: val });
    if (updated) showNotification();
  };

  const showNotification = () => {
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const handleExportData = async () => {
    setIsExporting(true);
    try {
      let transactionsList = [];
      try {
        const transactionsData = await transactionService.getTransactions({ limit: 1000 });
        transactionsList = transactionsData?.transactions || [];
      } catch (netErr) {
        console.warn('Network fetch fallback during export:', netErr);
      }

      const exportObject = {
        app: 'SpendSense AI',
        version: '1.0.0',
        exportedAt: new Date().toISOString(),
        userContext: 'default_user',
        localSettings: settings,
        sessionTransactions: transactionsList
      };

      const jsonString = JSON.stringify(exportObject, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);

      const downloadAnchor = document.createElement('a');
      downloadAnchor.href = url;
      downloadAnchor.download = `spendsense_user_data_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();

      setTimeout(() => {
        URL.revokeObjectURL(url);
        downloadAnchor.remove();
      }, 100);
    } catch (err) {
      console.error('Failed to export user context data:', err);
    } finally {
      setIsExporting(false);
    }
  };


  const handleResetDefaults = () => {
    settingsService.resetSettings();
    setShowResetModal(false);
    setResetSuccess(true);
    setTimeout(() => setResetSuccess(false), 3000);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-gray-200 pb-4 gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-indigo-50 border border-indigo-100 rounded-xl text-indigo-600 shadow-sm">
            <SettingsIcon className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Application Settings</h1>
            <p className="text-xs text-gray-500">Configure display preferences, budget alerts, and session data backups</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {saveSuccess && (
            <div className="flex items-center px-3.5 py-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-xs font-semibold animate-fade-in shadow-sm">
              <CheckCircle className="w-4 h-4 mr-1.5 text-emerald-600" />
              Preferences Saved!
            </div>
          )}

          {resetSuccess && (
            <div className="flex items-center px-3.5 py-1.5 bg-amber-50 text-amber-700 border border-amber-200 rounded-xl text-xs font-semibold animate-fade-in shadow-sm">
              <RefreshCw className="w-4 h-4 mr-1.5 text-amber-600" />
              Reset to Defaults
            </div>
          )}
        </div>
      </div>

      {/* Demo Mode & Session Scope Banner */}
      <div className="flex items-center space-x-3 p-4 bg-indigo-50/70 border border-indigo-200/80 rounded-2xl shadow-sm text-indigo-950">
        <Info className="w-5 h-5 text-indigo-600 flex-shrink-0" />
        <div className="text-xs leading-relaxed">
          <span className="font-bold">Demo Mode:</span> Settings changes apply to your local browser session. Preference values are saved locally and do not alter global database schema or shared system configuration.
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Section 1: Currency Selection */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 border-b border-gray-100 pb-3">
            <DollarSign className="w-5 h-5 text-indigo-600" />
            <h2 className="text-base font-semibold text-gray-900">Currency Preference</h2>
          </div>
          <p className="text-xs text-gray-500">Select your preferred currency symbol for dashboard cards and summary reports.</p>
          
          <div className="grid grid-cols-2 gap-3">
            {CURRENCY_OPTIONS.map((c) => {
              const isSelected = settings.currency === c.symbol;
              return (
                <button
                  key={c.code}
                  onClick={() => handleCurrencyChange(c)}
                  className={`flex items-center justify-between p-3.5 rounded-xl border text-xs font-semibold transition-all ${
                    isSelected
                      ? 'bg-indigo-50/80 border-indigo-600 text-indigo-700 shadow-sm ring-1 ring-indigo-500'
                      : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <span>{c.label}</span>
                  <span className="text-base font-bold">{c.symbol}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Section 2: Appearance & Theme */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 border-b border-gray-100 pb-3">
            {settings.theme === 'dark' ? <Moon className="w-5 h-5 text-purple-600" /> : <Sun className="w-5 h-5 text-amber-500" />}
            <h2 className="text-base font-semibold text-gray-900">Appearance & Theme</h2>
          </div>
          <p className="text-xs text-gray-500">Switch between Light theme and Dark theme visual interfaces.</p>
          
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-200">
            <div className="flex items-center space-x-3">
              {settings.theme === 'dark' ? (
                <Moon className="w-5 h-5 text-purple-600" />
              ) : (
                <Sun className="w-5 h-5 text-amber-500" />
              )}
              <div>
                <p className="text-xs font-bold text-gray-900 capitalize">{settings.theme} Mode Active</p>
                <p className="text-[11px] text-gray-500">
                  {settings.theme === 'dark' ? 'Dark glassmorphism interface' : 'Clean light workspace'}
                </p>
              </div>
            </div>

            <button
              onClick={handleThemeToggle}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                settings.theme === 'dark' ? 'bg-indigo-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  settings.theme === 'dark' ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>

        {/* Section 3: Budget Alert Thresholds */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm space-y-5 md:col-span-2">
          <div className="flex items-center space-x-2 border-b border-gray-100 pb-3">
            <Sliders className="w-5 h-5 text-indigo-600" />
            <h2 className="text-base font-semibold text-gray-900">Budget Alert Thresholds</h2>
          </div>
          <p className="text-xs text-gray-500">Customize percentage levels that trigger Warning and Near Limit badges on your budget cards.</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Warning Slider */}
            <div className="space-y-2 p-4 bg-amber-50/50 border border-amber-200/60 rounded-xl">
              <div className="flex items-center justify-between text-xs font-bold text-amber-900">
                <span className="flex items-center">
                  <AlertTriangle className="w-4 h-4 mr-1 text-amber-600" />
                  Warning Threshold
                </span>
                <span className="px-2 py-0.5 bg-amber-200/80 rounded-md text-amber-900">{settings.warningThreshold}%</span>
              </div>
              <input
                type="range"
                min="50"
                max="85"
                step="5"
                value={settings.warningThreshold}
                onChange={(e) => handleThresholdChange('warningThreshold', e.target.value)}
                className="w-full h-2 bg-amber-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
              />
              <p className="text-[11px] text-amber-700">Displays amber alert badge when category spending reaches this percentage.</p>
            </div>

            {/* Near Limit Slider */}
            <div className="space-y-2 p-4 bg-rose-50/50 border border-rose-200/60 rounded-xl">
              <div className="flex items-center justify-between text-xs font-bold text-rose-900">
                <span className="flex items-center">
                  <AlertTriangle className="w-4 h-4 mr-1 text-rose-600" />
                  Near Limit Threshold
                </span>
                <span className="px-2 py-0.5 bg-rose-200/80 rounded-md text-rose-900">{settings.limitThreshold}%</span>
              </div>
              <input
                type="range"
                min="85"
                max="100"
                step="5"
                value={settings.limitThreshold}
                onChange={(e) => handleThresholdChange('limitThreshold', e.target.value)}
                className="w-full h-2 bg-rose-200 rounded-lg appearance-none cursor-pointer accent-rose-600"
              />
              <p className="text-[11px] text-rose-700">Displays rose near-limit badge when category spending reaches this percentage.</p>
            </div>
          </div>
        </div>

        {/* Section 4: Data Management & Backup */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm space-y-4 md:col-span-2">
          <div className="flex items-center space-x-2 border-b border-gray-100 pb-3">
            <Download className="w-5 h-5 text-indigo-600" />
            <h2 className="text-base font-semibold text-gray-900">Session Data & Local Preferences</h2>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
            <div>
              <h3 className="text-xs font-bold text-gray-900">Export User Session Backup</h3>
              <p className="text-[11px] text-gray-500 mt-0.5">
                Downloads your current session's transactions and local preferences in a clean JSON format.
              </p>
            </div>

            <button
              onClick={handleExportData}
              disabled={isExporting}
              className="flex items-center px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all disabled:opacity-50 flex-shrink-0"
            >
              <Download className="w-4 h-4 mr-2" />
              {isExporting ? 'Exporting...' : 'Export Session Backup (JSON)'}
            </button>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 bg-rose-50/50 rounded-xl border border-rose-200">
            <div>
              <h3 className="text-xs font-bold text-rose-900 flex items-center">
                <ShieldCheck className="w-4 h-4 mr-1 text-rose-600" />
                Reset Local Session Preferences
              </h3>
              <p className="text-[11px] text-rose-700 mt-0.5">
                Resets currency, theme, and alert sliders back to defaults in your local browser storage.
              </p>
            </div>

            <button
              onClick={() => setShowResetModal(true)}
              className="flex items-center px-4 py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all flex-shrink-0"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Reset Local Preferences
            </button>
          </div>
        </div>

      </div>

      {/* Reset Confirmation Modal */}
      {showResetModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full border border-gray-200 shadow-xl space-y-4">
            <div className="flex items-center space-x-3 text-rose-600">
              <AlertTriangle className="w-6 h-6 flex-shrink-0" />
              <h3 className="text-lg font-bold text-gray-900">Reset Local Preferences?</h3>
            </div>

            <div className="p-3 bg-gray-50 border border-gray-200 rounded-xl text-xs text-gray-600 space-y-2">
              <p className="font-semibold text-gray-800">
                This action only resets local browser preferences (<code className="bg-gray-200 px-1 py-0.5 rounded text-gray-900">localStorage</code>):
              </p>
              <ul className="list-disc list-inside space-y-1 text-[11px] text-gray-600">
                <li>Resets currency to ₹ (INR)</li>
                <li>Resets theme to Light mode</li>
                <li>Resets budget alert thresholds (70% / 90%)</li>
              </ul>
              <p className="text-[11px] text-emerald-700 font-semibold pt-1 border-t border-gray-200">
                ✓ Global database records and transactions are NOT affected.
              </p>
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setShowResetModal(false)}
                className="px-4 py-2 text-xs font-semibold text-gray-600 hover:text-gray-900 bg-gray-100 rounded-xl transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleResetDefaults}
                className="px-4 py-2 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 rounded-xl shadow-sm transition-all"
              >
                Confirm Reset
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;
