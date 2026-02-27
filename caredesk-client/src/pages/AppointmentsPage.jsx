import { useState, useEffect } from 'react';
import { fetchAPI } from '../api';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { Plus, CalendarDays } from 'lucide-react';

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({ doctor_id: '', patient_id: '', appointment_date: new Date().toISOString().split('T')[0], appointment_time: '', notes: '' });

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    const [apptRes, docRes, patRes] = await Promise.all([
      fetchAPI('/api/appointments'),
      fetchAPI('/api/doctors'),
      fetchAPI('/api/patients'),
    ]);
    if (apptRes.status === 'success') setAppointments(apptRes.data);
    if (docRes.status === 'success') setDoctors(docRes.data);
    if (patRes.status === 'success') setPatients(patRes.data);
    setLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    await fetchAPI('/api/appointments', { method: 'POST', body: JSON.stringify(form) });
    setSubmitting(false);
    setShowModal(false);
    setForm({ doctor_id: '', patient_id: '', appointment_date: new Date().toISOString().split('T')[0], appointment_time: '', notes: '' });
    loadData();
  };

  const updateStatus = async (id, status) => {
    await fetchAPI(`/api/appointments/${id}`, { method: 'PUT', body: JSON.stringify({ status }) });
    loadData();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Appointments</h1>
          <p className="text-sm text-gray-500">{appointments.length} appointment(s) today</p>
        </div>
        <button onClick={() => setShowModal(true)} className="flex items-center gap-2 rounded-lg bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700">
          <Plus size={16} /> Book Appointment
        </button>
      </div>

      {appointments.length === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-gray-200 p-12 text-center">
          <CalendarDays className="mx-auto mb-3 text-gray-300" size={40} />
          <p className="text-gray-500">No appointments today.</p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Token</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Patient</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Doctor</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Time</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Status</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {appointments.map((a) => (
                <tr key={a.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-bold text-teal-600">{a.token_number}</td>
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-900">{a.patient_name}</p>
                    <p className="text-xs text-gray-400">{a.patient_phone}</p>
                  </td>
                  <td className="px-4 py-3 text-gray-600">Dr. {a.doctor_name}</td>
                  <td className="px-4 py-3 text-gray-600">{a.appointment_time || '—'}</td>
                  <td className="px-4 py-3"><StatusBadge status={a.status} /></td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1">
                      {a.status === 'booked' && (
                        <button onClick={() => updateStatus(a.id, 'in-queue')} className="rounded bg-yellow-100 px-2 py-1 text-xs font-medium text-yellow-700 hover:bg-yellow-200">
                          Add to Queue
                        </button>
                      )}
                      {a.status === 'in-queue' && (
                        <button onClick={() => updateStatus(a.id, 'in-consultation')} className="rounded bg-purple-100 px-2 py-1 text-xs font-medium text-purple-700 hover:bg-purple-200">
                          Start Consult
                        </button>
                      )}
                      {a.status === 'in-consultation' && (
                        <a href={`${import.meta.env.BASE_URL}consultation/${a.id}`} className="rounded bg-teal-100 px-2 py-1 text-xs font-medium text-teal-700 hover:bg-teal-200">
                          Write Rx
                        </a>
                      )}
                      {a.status === 'booked' && (
                        <button onClick={() => updateStatus(a.id, 'cancelled')} className="rounded bg-red-100 px-2 py-1 text-xs font-medium text-red-700 hover:bg-red-200">
                          Cancel
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Book Appointment">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Doctor *</label>
            <select required value={form.doctor_id} onChange={(e) => setForm({ ...form, doctor_id: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500">
              <option value="">Select doctor</option>
              {doctors.map((d) => <option key={d.id} value={d.id}>Dr. {d.name} — {d.specialty}</option>)}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Patient *</label>
            <select required value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500">
              <option value="">Select patient</option>
              {patients.map((p) => <option key={p.id} value={p.id}>{p.name} — {p.phone}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Date *</label>
              <input type="date" required value={form.appointment_date} onChange={(e) => setForm({ ...form, appointment_date: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Time</label>
              <input type="time" value={form.appointment_time} onChange={(e) => setForm({ ...form, appointment_time: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Notes</label>
            <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={2} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
          </div>
          <button type="submit" disabled={submitting} className="w-full rounded-lg bg-teal-600 py-2.5 text-sm font-medium text-white hover:bg-teal-700 disabled:opacity-50">
            {submitting ? 'Booking...' : 'Book Appointment'}
          </button>
        </form>
      </Modal>
    </div>
  );
}
