import { useState, useEffect } from 'react';
import { fetchAPI } from '../api';
import Modal from '../components/Modal';
import LoadingSpinner from '../components/LoadingSpinner';
import { Plus, Edit2, Trash2, Stethoscope } from 'lucide-react';
import { SPECIALTIES } from '../utils/constants';

export default function DoctorsPage() {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editDoctor, setEditDoctor] = useState(null);
  const [form, setForm] = useState({ name: '', specialty: '', email: '', phone: '', available_from: '09:00', available_to: '17:00', consultation_fee: '500' });

  useEffect(() => { loadDoctors(); }, []);

  const loadDoctors = async () => {
    const res = await fetchAPI('/api/doctors');
    if (res.status === 'success') setDoctors(res.data);
    setLoading(false);
  };

  const openAdd = () => {
    setEditDoctor(null);
    setForm({ name: '', specialty: '', email: '', phone: '', available_from: '09:00', available_to: '17:00', consultation_fee: '500' });
    setShowModal(true);
  };

  const openEdit = (doc) => {
    setEditDoctor(doc);
    setForm({ name: doc.name, specialty: doc.specialty, email: doc.email, phone: doc.phone, available_from: doc.available_from, available_to: doc.available_to, consultation_fee: doc.consultation_fee });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (editDoctor) {
      await fetchAPI(`/api/doctors/${editDoctor.id}`, { method: 'PUT', body: JSON.stringify(form) });
    } else {
      await fetchAPI('/api/doctors', { method: 'POST', body: JSON.stringify(form) });
    }
    setShowModal(false);
    loadDoctors();
  };

  const handleDelete = async (id) => {
    if (!confirm('Remove this doctor?')) return;
    await fetchAPI(`/api/doctors/${id}`, { method: 'DELETE' });
    loadDoctors();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Doctors</h1>
          <p className="text-sm text-gray-500">{doctors.length} doctor(s) registered</p>
        </div>
        <button onClick={openAdd} className="flex items-center gap-2 rounded-lg bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700">
          <Plus size={16} /> Add Doctor
        </button>
      </div>

      {doctors.length === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-gray-200 p-12 text-center">
          <Stethoscope className="mx-auto mb-3 text-gray-300" size={40} />
          <p className="text-gray-500">No doctors yet. Add your first doctor.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {doctors.map((doc) => (
            <div key={doc.id} className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
              <div className="mb-3 flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-teal-100 text-teal-600 font-semibold">
                    {doc.name.charAt(0)}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">Dr. {doc.name}</p>
                    <p className="text-xs text-gray-500">{doc.specialty}</p>
                  </div>
                </div>
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${doc.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                  {doc.status}
                </span>
              </div>
              <div className="mb-3 space-y-1 text-sm text-gray-500">
                <p>Hours: {doc.available_from} — {doc.available_to}</p>
                <p>Fee: Rs. {doc.consultation_fee}</p>
                {doc.phone && <p>Phone: {doc.phone}</p>}
              </div>
              <div className="flex gap-2">
                <button onClick={() => openEdit(doc)} className="flex items-center gap-1 rounded-lg border border-gray-200 px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-50">
                  <Edit2 size={12} /> Edit
                </button>
                <button onClick={() => handleDelete(doc.id)} className="flex items-center gap-1 rounded-lg border border-red-200 px-3 py-1.5 text-xs text-red-600 hover:bg-red-50">
                  <Trash2 size={12} /> Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title={editDoctor ? 'Edit Doctor' : 'Add Doctor'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Full Name *</label>
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Specialty *</label>
            <select required value={form.specialty} onChange={(e) => setForm({ ...form, specialty: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500">
              <option value="">Select specialty</option>
              {SPECIALTIES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
              <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Phone</label>
              <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">From</label>
              <input type="time" value={form.available_from} onChange={(e) => setForm({ ...form, available_from: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">To</label>
              <input type="time" value={form.available_to} onChange={(e) => setForm({ ...form, available_to: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Fee (Rs.)</label>
              <input value={form.consultation_fee} onChange={(e) => setForm({ ...form, consultation_fee: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
          </div>
          <button type="submit" className="w-full rounded-lg bg-teal-600 py-2.5 text-sm font-medium text-white hover:bg-teal-700">
            {editDoctor ? 'Update Doctor' : 'Add Doctor'}
          </button>
        </form>
      </Modal>
    </div>
  );
}
