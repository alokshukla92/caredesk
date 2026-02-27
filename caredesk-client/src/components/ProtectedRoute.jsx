import { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';
import { API_BASE } from '../utils/constants';

export default function ProtectedRoute({ children }) {
  const [checking, setChecking] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    // Method 1: Try Catalyst client SDK
    try {
      if (window.catalyst?.auth?.isUserAuthenticated) {
        const res = await window.catalyst.auth.isUserAuthenticated();
        if (res) {
          setAuthenticated(true);
          setChecking(false);
          return;
        }
      }
    } catch {
      // SDK method failed, try backend check
    }

    // Method 2: Verify via backend API (cookies handle auth on same-origin)
    try {
      const res = await fetch(`${API_BASE}/api/debug/whoami`, {
        credentials: 'same-origin',
      });
      if (res.ok) {
        const data = await res.json();
        if (data.user_id) {
          setAuthenticated(true);
          setChecking(false);
          return;
        }
      }
    } catch {
      // Backend check failed
    }

    // Not authenticated — redirect to login (with loop guard)
    const lastRedirect = parseInt(sessionStorage.getItem('auth_redirect_ts') || '0');
    const now = Date.now();
    if (now - lastRedirect > 5000) {
      sessionStorage.setItem('auth_redirect_ts', String(now));
      window.location.href = '/__catalyst/auth/login';
    } else {
      setChecking(false);
      setAuthenticated(false);
    }
  };

  if (checking) return <LoadingSpinner />;

  if (!authenticated) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-700">Authentication Required</h2>
          <p className="mt-2 text-gray-500">Unable to verify your session.</p>
          <button
            onClick={() => {
              sessionStorage.removeItem('auth_redirect_ts');
              window.location.href = '/__catalyst/auth/login';
            }}
            className="mt-4 rounded-lg bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700"
          >
            Sign In
          </button>
        </div>
      </div>
    );
  }

  sessionStorage.removeItem('auth_redirect_ts');
  return children;
}
