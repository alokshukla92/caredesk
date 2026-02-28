const KEY = 'caredesk_patient';

export function savePatientInfo({ name, phone, email }) {
  try {
    const data = {};
    if (name) data.name = name;
    if (phone) data.phone = phone;
    if (email) data.email = email;
    localStorage.setItem(KEY, JSON.stringify(data));
  } catch (_) { /* storage full or blocked */ }
}

export function getPatientInfo() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || {};
  } catch (_) {
    return {};
  }
}
