/**
 * SpendSense AI - Centralized API Configuration
 * Uses Vite syntax (import.meta.env.VITE_API_BASE_URL) with fallback to
 * "https://spendsense-production-a33e.up.railway.app" if unconfigured.
 */

const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  const fallback = 'https://spendsense-production-a33e.up.railway.app';

  const raw = envUrl && envUrl.trim() ? envUrl.trim() : fallback;
  const clean = raw.replace(/\/$/, '');

  // If the URL already ends with /api or is a relative /api route, return clean as is
  if (clean.endsWith('/api') || clean === '/api') {
    return clean;
  }

  return `${clean}/api`;
};

export const API_BASE_URL = getApiBaseUrl();

export default API_BASE_URL;
