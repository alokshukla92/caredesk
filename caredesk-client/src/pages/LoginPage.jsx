import { useEffect } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';

export default function LoginPage() {
  useEffect(() => {
    // Redirect to Catalyst's built-in auth login
    window.location.href = '/__catalyst/auth/login';
  }, []);

  return <LoadingSpinner />;
}
