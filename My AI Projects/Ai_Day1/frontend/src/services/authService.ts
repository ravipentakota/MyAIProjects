import type { User } from '../types';

export interface AuthResponse {
  user: User | null;
  message: string;
}

interface AuthUserPayload {
  user: {
    id: string;
    email: string;
  };
  message: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8002';

async function extractErrorMessage(response: Response, fallbackMessage: string): Promise<string> {
  try {
    const payload = (await response.json()) as
      | { detail?: { message?: string } | Array<{ msg?: string }> }
      | undefined;
    if (Array.isArray(payload?.detail)) {
      const first = payload.detail[0]?.msg;
      if (first) return first;
    }
    if (payload?.detail && !Array.isArray(payload.detail) && payload.detail.message) {
      return payload.detail.message;
    }
  } catch {
    // Ignore non-JSON errors and use fallback.
  }
  return fallbackMessage;
}

export const authService = {
  async registerWithPassword(email: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/email/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error(await extractErrorMessage(response, 'Failed to register account'));
    }

    const data = (await response.json()) as AuthUserPayload;
    return {
      user: {
        id: data.user.id,
        email: data.user.email,
      },
      message: data.message,
    };
  },

  async loginWithPassword(email: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/email/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error(await extractErrorMessage(response, 'Invalid email or password'));
    }

    const data = (await response.json()) as AuthUserPayload;
    return {
      user: {
        id: data.user.id,
        email: data.user.email,
      },
      message: data.message,
    };
  },

  async logout(): Promise<void> {
    await fetch(`${API_BASE_URL}/api/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    });
  },

  async startGoogleLogin(): Promise<AuthResponse> {
    const redirectTo = window.location.origin;
    window.location.assign(`${API_BASE_URL}/api/auth/google/login?redirect_to=${encodeURIComponent(redirectTo)}`);
    return {
      user: null,
      message: 'Redirecting to Google...',
    };
  },
};
