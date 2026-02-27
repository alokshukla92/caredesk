import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';

const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

export default function LoginPage() {
  const navigate = useNavigate();

  useEffect(() => {
    if (isDev) {
      navigate('/dashboard', { replace: true });
      return;
    }

    // On serverless domain, use Catalyst's built-in auth
    window.location.href = '/__catalyst/auth/login';
  }, []);

  return <LoadingSpinner />;
}
