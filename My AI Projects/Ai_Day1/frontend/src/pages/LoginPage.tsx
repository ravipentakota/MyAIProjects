/** Login page with Google OAuth and basic username/password form UI. */
import { FormEvent, useState } from 'react';

import { useAuth } from '../hooks/useAuth';

export default function LoginPage() {
  const { isLoading, startGoogleLogin, loginWithPassword, registerWithPassword } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [isSignupOpen, setIsSignupOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [signupErrorMessage, setSignupErrorMessage] = useState('');
  const [signupMessage, setSignupMessage] = useState('');

  function normalizeIdentifier(value: string): string {
    const trimmed = value.trim().toLowerCase();
    if (!trimmed) return '';
    return trimmed.includes('@') ? trimmed : `${trimmed}@example.com`;
  }

  function isValidEmail(value: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  async function handlePasswordLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const email = normalizeIdentifier(username);
    if (!email || !password.trim()) {
      setErrorMessage('Email and password are required.');
      return;
    }

    setErrorMessage('');
    try {
      await loginWithPassword(email, password);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Failed to sign in');
    }
  }

  async function handleCreateAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const email = signupEmail.trim().toLowerCase();
    if (!email || !signupPassword.trim()) {
      setSignupErrorMessage('Email and password are required for signup.');
      setSignupMessage('');
      return;
    }

    if (!isValidEmail(email)) {
      setSignupErrorMessage('Please enter a valid email address.');
      setSignupMessage('');
      return;
    }

    setSignupErrorMessage('');
    try {
      const message = await registerWithPassword(email, signupPassword);
      setSignupMessage(message || 'Account created successfully. You can now sign in.');
      setSignupEmail('');
      setSignupPassword('');
    } catch (error) {
      setSignupMessage('');
      setSignupErrorMessage(error instanceof Error ? error.message : 'Failed to create account');
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-sm">
        <h1 className="text-2xl font-semibold text-gray-800 mb-1">Amzur AI Chat</h1>
        <p className="text-sm text-gray-500 mb-6">Continue with Google via Supabase</p>

        <button
          type="button"
          onClick={startGoogleLogin}
          disabled={isLoading}
          className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700"
        >
          {isLoading ? 'Redirecting...' : 'Continue with Google'}
        </button>

        <form onSubmit={handlePasswordLogin} className="mt-4 space-y-3">
          <input
            type="email"
            placeholder="Email"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white"
          >
            {isLoading ? 'Please wait...' : 'Sign In'}
          </button>
          <button
            type="button"
            className="w-full text-sm text-blue-700 underline underline-offset-2"
            onClick={() => {
              setErrorMessage('');
              setSignupErrorMessage('');
              setSignupMessage('');
              setIsSignupOpen(true);
            }}
          >
            Signup
          </button>
          {errorMessage ? <p className="text-xs text-red-600">{errorMessage}</p> : null}
        </form>
      </div>

      {isSignupOpen ? (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-black/30 px-4">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">Signup</h2>
              <button
                type="button"
                className="rounded border border-gray-300 px-2 py-1 text-xs text-gray-700"
                onClick={() => {
                  setSignupErrorMessage('');
                  setSignupMessage('');
                  setIsSignupOpen(false);
                }}
              >
                Close
              </button>
            </div>

            <form onSubmit={handleCreateAccount} className="space-y-3">
              <input
                type="email"
                placeholder="Email"
                value={signupEmail}
                onChange={(event) => setSignupEmail(event.target.value)}
                required
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500"
              />
              <input
                type="password"
                placeholder="Password"
                value={signupPassword}
                onChange={(event) => setSignupPassword(event.target.value)}
                required
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500"
              />
              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white"
              >
                {isLoading ? 'Please wait...' : 'Create Account'}
              </button>
              {signupErrorMessage ? <p className="text-xs text-red-600">{signupErrorMessage}</p> : null}
              {signupMessage ? <p className="text-xs text-green-700">{signupMessage}</p> : null}
            </form>
          </div>
        </div>
      ) : null}
    </div>
  );
}
