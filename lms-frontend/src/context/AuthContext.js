import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../api/auth';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  // ── Load user from a valid stored token on app start / refresh ──────────
  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('token');

    // No token → not logged in, nothing to load
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      // Always fetch fresh data from the server as source of truth
      const res = await authAPI.getUserDetail();

      // Merge: fresh API data takes priority over stale cached data
      const cached = JSON.parse(localStorage.getItem('user') || '{}');
      const merged = { ...cached, ...res.data };

      // Keep localStorage in sync with latest server data
      localStorage.setItem('user', JSON.stringify(merged));
      setUser(merged);
    } catch (err) {
      // Only clear session on a real auth failure (401 Unauthorized)
      // Do NOT clear on network errors, 500s, etc.
      if (err.response?.status === 401) {
        localStorage.clear();
      }
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Run once on mount to restore session
  useEffect(() => {
    loadUser();
  }, [loadUser]);

  // ── Login: store token, fetch full profile ───────────────────────────────
  const login = async (credentials) => {
    // Step 1: authenticate and get the token
    const res = await authAPI.login(credentials);
    const { token, ...userData } = res.data;

    // Step 2: persist the token immediately so the interceptor can use it
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));

    // Step 3: fetch the full user profile (same as loadUser does)
    try {
      const profileRes = await authAPI.getUserDetail();
      const fullUser   = { ...userData, ...profileRes.data };
      localStorage.setItem('user', JSON.stringify(fullUser));
      setUser(fullUser);
      return fullUser;
    } catch {
      // Fallback: use login response data if profile fetch fails
      setUser(userData);
      return userData;
    }
  };

  // ── Logout: wipe all session data ────────────────────────────────────────
  const logout = () => {
    localStorage.clear();
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};