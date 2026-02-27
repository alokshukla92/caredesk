import { useState, useEffect } from 'react';
import { fetchAPI } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';
import { Save, Building2, Link } from 'lucide-react';
import { useToast } from '../components/Toast';

export default function SettingsPage() {
  const [clinic, setClinic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [form, setForm] = useState({ name: '', slug: '', address: '', phone: '', email: '' });
  const toast = useToast();

  useEffect(() => { loadClinic(); }, []);

  const loadClinic = async () => {
    const res = await fetchAPI('/api/clinics/me');
    if (res.status === 'success' && res.data) {
      setClinic(res.data);
      setForm({ name: res.data.name, slug: res.data.slug, address: res.data.address, phone: res.data.phone, email: res.data.email });
    } else {
      setShowRegister(true);
    }
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setSaving(true);
    const res = await fetchAPI('/api/clinics', { method: 'POST', body: JSON.stringify(form) });
    setSaving(false);
    if (res.status === 'success') {
      setShowRegister(false);
      loadClinic();
    } else {
      toast.error(res.message || 'Registration failed');
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setSaving(true);
    await fetchAPI('/api/clinics/me', { method: 'PUT', body: JSON.stringify(form) });
    setSaving(false);
    loadClinic();
  };

  if (loading) return <LoadingSpinner />;

  if (showRegister) {
    return (
      <div className="mx-auto max-w-lg">
        <div className="mb-6 text-center">
          <Building2 className="mx-auto mb-3 text-teal-600" size={40} />
          <h1 className="text-2xl font-bold text-gray-900">Register Your Clinic</h1>
          <p className="text-sm text-gray-500">Set up your clinic to get started</p>
        </div>
        <form onSubmit={handleRegister} className="space-y-4 rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Clinic Name *</label>
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">URL Slug * <span className="text-xs text-gray-400">(e.g., "apollo-delhi")</span></label>
            <input required value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" placeholder="my-clinic" />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Address</label>
            <textarea value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} rows={2} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Phone</label>
              <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
              <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
          </div>
          <button type="submit" disabled={saving} className="w-full rounded-lg bg-teal-600 py-2.5 text-sm font-medium text-white hover:bg-teal-700 disabled:opacity-50">
            {saving ? 'Registering...' : 'Register Clinic'}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Clinic Settings</h1>
        <p className="text-sm text-gray-500">Manage your clinic details</p>
      </div>

      <form onSubmit={handleUpdate} className="space-y-4 rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Clinic Name</label>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">URL Slug</label>
          <input disabled value={form.slug} className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-500" />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Address</label>
          <textarea value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} rows={2} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Phone</label>
            <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
          </div>
        </div>
        <button type="submit" disabled={saving} className="flex w-full items-center justify-center gap-2 rounded-lg bg-teal-600 py-2.5 text-sm font-medium text-white hover:bg-teal-700 disabled:opacity-50">
          <Save size={16} /> {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </form>

      {clinic && (
        <div className="mt-6 rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-700">
            <Link size={16} /> Public Pages
          </h3>
          <div className="space-y-2 text-sm">
            <p><span className="text-gray-500">Booking:</span> <a href={`${import.meta.env.BASE_URL}book/${clinic.slug}`} target="_blank" rel="noreferrer" className="rounded bg-gray-100 px-2 py-0.5 text-teal-700 hover:underline">{`${import.meta.env.BASE_URL}book/${clinic.slug}`}</a></p>
            <p><span className="text-gray-500">Queue Display:</span> <a href={`${import.meta.env.BASE_URL}queue-display/${clinic.slug}`} target="_blank" rel="noreferrer" className="rounded bg-gray-100 px-2 py-0.5 text-teal-700 hover:underline">{`${import.meta.env.BASE_URL}queue-display/${clinic.slug}`}</a></p>
          </div>
        </div>
      )}
    </div>
  );
}
