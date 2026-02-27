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

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token || token === 'undefined' || token === 'null') {
      setLoading(false);
      return;
    }

    try {
      const res = await authAPI.getUserDetail();
      const cached = JSON.parse(localStorage.getItem('user') || '{}');
      const merged = { ...cached, ...res.data };
      localStorage.setItem('user', JSON.stringify(merged));
      setUser(merged);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.clear();
      }
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  // ── Login ─────────────────────────────────────────────────────────────────
  const login = async (credentials) => {
    const res = await authAPI.login(credentials);
    const token = res.data?.token;

    if (!token) {
      throw new Error('No token received from server');
    }

    // Store token FIRST — plain string, no JSON.stringify
    localStorage.setItem('token', String(token).trim());

    // Store full user data (including token so fallback works)
    localStorage.setItem('user', JSON.stringify(res.data));

    // Set user state immediately from login response — DO NOT call
    // getUserDetail() here because the token was JUST stored and
    // the next request can fire before axios picks it up,
    // causing a 401 that wipes everything.
    setUser(res.data);
    return res.data;
  };

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