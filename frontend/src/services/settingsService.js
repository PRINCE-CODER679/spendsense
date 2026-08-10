const SETTINGS_KEY = 'spendsense_user_settings';

const DEFAULT_SETTINGS = {
  currency: '₹', // '₹' | '$' | '€' | '£'
  currencyCode: 'INR',
  theme: 'light', // 'light' | 'dark'
  warningThreshold: 70, // % for budget warning
  limitThreshold: 90, // % for budget near limit
  enableAlerts: true
};

export const settingsService = {
  /**
   * Fetch current stored settings with defaults
   */
  getSettings: () => {
    try {
      const stored = localStorage.getItem(SETTINGS_KEY);
      if (!stored) return { ...DEFAULT_SETTINGS };
      return { ...DEFAULT_SETTINGS, ...JSON.parse(stored) };
    } catch (err) {
      console.error('Failed to load settings from localStorage:', err);
      return { ...DEFAULT_SETTINGS };
    }
  },

  /**
   * Save updated settings and dispatch change event
   */
  saveSettings: (newSettings) => {
    try {
      const current = settingsService.getSettings();
      const updated = { ...current, ...newSettings };
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(updated));

      // Apply theme to HTML document
      if (updated.theme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }

      // Broadcast event for UI reactivity
      window.dispatchEvent(new Event('spendsense_settings_updated'));
      return updated;
    } catch (err) {
      console.error('Failed to save settings:', err);
      return null;
    }
  },

  /**
   * Reset settings to default values
   */
  resetSettings: () => {
    try {
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(DEFAULT_SETTINGS));
      document.documentElement.classList.remove('dark');
      window.dispatchEvent(new Event('spendsense_settings_updated'));
      return { ...DEFAULT_SETTINGS };
    } catch (err) {
      console.error('Failed to reset settings:', err);
      return null;
    }
  },

  /**
   * Currency symbol helper
   */
  getCurrencySymbol: () => {
    return settingsService.getSettings().currency || '₹';
  }
};

export default settingsService;
