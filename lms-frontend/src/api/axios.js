import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const getStoredToken = () => {
  let raw = localStorage.getItem('token');
  if (raw) {
    if ((raw.startsWith('"') && raw.endsWith('"')) ||
        (raw.startsWith("'") && raw.endsWith("'"))) {
      raw = raw.slice(1, -1);
    }
    raw = raw.trim();
    if (raw && raw !== 'undefined' && raw !== 'null') return raw;
  }

  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const t = user?.token || user?.access || user?.access_token;
    if (t) {
      const cleaned = String(t).trim();
      if (cleaned && cleaned !== 'undefined' && cleaned !== 'null') return cleaned;
    }
  } catch {
    // corrupt JSON
  }
  return null;
};

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ── Request interceptor — attach token ────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = getStoredToken();
    if (token) {
      config.headers = {
        ...(config.headers || {}),
        Authorization: `Token ${token}`,
      };
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor — handle 401 ─────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const requestUrl = error.config?.url || '';
    const status     = error.response?.status;

    // Routes that should NEVER trigger a logout redirect on 401
    const skipLogoutRoutes = [
      '/user/login/',
      '/user/',
      '/user/verification/',
      '/user/send_otp_forgot_password/',
      '/user/update_forgot_password/',
      '/user/detail/',           // ← ADD THIS — profile fetch after login
    ];

    const shouldSkip    = skipLogoutRoutes.some((r) => requestUrl.includes(r));
    const isUnauthorized = status === 401;

    if (isUnauthorized && !shouldSkip) {
      localStorage.clear();
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

export default api;