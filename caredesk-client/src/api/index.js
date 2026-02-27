import { API_BASE } from '../utils/constants';

const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

export async function fetchAPI(path, options = {}) {
  try {
    let headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // In production only, attach Catalyst auth token
    if (!isDev && window.catalyst?.auth?.generateAuthToken) {
      try {
        const response = await window.catalyst.auth.generateAuthToken();
        if (response?.access_token) {
          headers['Authorization'] = response.access_token;
        }
      } catch (e) {
        console.warn('Auth token generation failed:', e);
      }
    }

    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    const data = await res.json();
    return data;
  } catch (err) {
    console.error('API Error:', err);
    return { status: 'error', message: err.message };
  }
}

export async function fetchPublicAPI(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    const data = await res.json();
    return data;
  } catch (err) {
    console.error('Public API Error:', err);
    return { status: 'error', message: err.message };
  }
}
