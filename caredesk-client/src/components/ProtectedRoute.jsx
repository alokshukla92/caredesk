import { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';

const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

export default function ProtectedRoute({ children }) {
  const [checking, setChecking] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    if (isDev) {
      setAuthenticated(true);
      setChecking(false);
      return;
    }

    try {
      if (window.catalyst && window.catalyst.auth) {
        const res = await window.catalyst.auth.isUserAuthenticated();
        setAuthenticated(!!res);
      } else {
        // On serverless domain, Catalyst handles auth at server level
        // If we got here, user is authenticated
        setAuthenticated(true);
      }
    } catch {
      // Redirect to Catalyst login
      window.location.href = '/__catalyst/auth/login';
      return;
    }
    setChecking(false);
  };

  if (checking) return <LoadingSpinner />;
  if (!authenticated) {
    window.location.href = '/__catalyst/auth/login';
    return <LoadingSpinner />;
  }

  return children;
}
