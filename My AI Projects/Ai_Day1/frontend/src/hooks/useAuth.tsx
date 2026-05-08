"use client";
/* eslint-disable react-refresh/only-export-components */

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

import { authService } from '../services/authService';
import type { User } from '../types';

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  startGoogleLogin: () => Promise<void>;
  loginWithPassword: (email: string, password: string) => Promise<void>;
  registerWithPassword: (email: string, password: string) => Promise<string>;
  clearSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    if (typeof window === 'undefined') return null;
    const params = new URLSearchParams(window.location.search);
    const oauthUserId = params.get('oauth_user_id');
    const oauthEmail = params.get('oauth_email');
    if (!oauthUserId || !oauthEmail) return null;
    return { id: oauthUserId, email: oauthEmail };
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const oauthUserId = params.get('oauth_user_id');
    const oauthEmail = params.get('oauth_email');
    if (!oauthUserId || !oauthEmail) return;

    params.delete('oauth_user_id');
    params.delete('oauth_email');
    const next = params.toString();
    const nextUrl = `${window.location.pathname}${next ? `?${next}` : ''}`;
    window.history.replaceState({}, '', nextUrl);
  }, []);

  async function startGoogleLogin() {
    setIsLoading(true);
    try {
      await authService.startGoogleLogin();
    } finally {
      setIsLoading(false);
    }
  }

  async function loginWithPassword(email: string, password: string) {
    setIsLoading(true);
    try {
      const result = await authService.loginWithPassword(email, password);
      if (result.user) setUser(result.user);
    } finally {
      setIsLoading(false);
    }
  }

  async function registerWithPassword(email: string, password: string) {
    setIsLoading(true);
    try {
      const result = await authService.registerWithPassword(email, password);
      return result.message;
    } finally {
      setIsLoading(false);
    }
  }

  async function clearSession() {
    await authService.logout();
    setUser(null);
  }

  const value = useMemo<AuthContextValue>(
    () => ({ user, isLoading, startGoogleLogin, loginWithPassword, registerWithPassword, clearSession }),
    [user, isLoading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return ctx;
}
