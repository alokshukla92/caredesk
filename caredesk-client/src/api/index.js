import { API_BASE } from '../utils/constants';

export async function fetchAPI(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'same-origin',
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
