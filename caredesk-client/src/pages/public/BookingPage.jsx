import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { fetchPublicAPI } from '../../api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { Activity, CalendarDays, CheckCircle } from 'lucide-react';
import { useToast } from '../../components/Toast';
import { GENDERS } from '../../utils/constants';

export default function BookingPage() {
  const { slug } = useParams();
  const [clinic, setClinic] = useState(null);
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [booked, setBooked] = useState(null);
  const [form, setForm] = useState({ doctor_id: '', patient_name: '', patient_phone: '', patient_email: '', age: '', gender: '', appointment_date: new Date().toISOString().split('T')[0], appointment_time: '', notes: '' });
  const toast = useToast();

  useEffect(() => { loadClinic(); }, [slug]);

  const loadClinic = async () => {
    const res = await fetchPublicAPI(`/api/public/clinic/${slug}`);
    if (res.status === 'success') {
      setClinic(res.data.clinic);
      setDoctors(res.data.doctors);
    }
    setLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetchPublicAPI('/api/public/book', {
      method: 'POST',
      body: JSON.stringify({ clinic_slug: slug, ...form }),
    });
    if (res.status === 'success') {
      setBooked(res.data);
    } else {
      toast.error(res.message || 'Booking failed');
    }
  };

  if (loading) return <LoadingSpinner />;

  if (!clinic) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <p className="text-lg text-gray-500">Clinic not found.</p>
      </div>
    );
  }

  if (booked) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-teal-50 to-blue-50 px-4">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-lg">
          <CheckCircle className="mx-auto mb-4 text-green-500" size={48} />
          <h2 className="text-xl font-bold text-gray-900">Appointment Booked!</h2>
          <p className="mt-2 text-gray-500">Your appointment at {booked.clinic_name} is confirmed.</p>
          <div className="mt-6 rounded-xl bg-teal-50 p-4">
            <p className="text-4xl font-bold text-teal-600">{booked.token_number}</p>
            <p className="mt-1 text-sm text-teal-700">Your Token Number</p>
          </div>
          <div className="mt-4 space-y-1 text-sm text-gray-600">
            <p>Date: {booked.appointment_date}</p>
            {booked.appointment_time && <p>Time: {booked.appointment_time}</p>}
          </div>
          <p className="mt-4 text-xs text-gray-400">Please arrive 10 minutes before your appointment.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-blue-50 px-4 py-8">
      <div className="mx-auto max-w-lg">
        <div className="mb-6 text-center">
          <Activity className="mx-auto mb-2 text-teal-600" size={32} />
          <h1 className="text-2xl font-bold text-gray-900">{clinic.name}</h1>
          <p className="text-sm text-gray-500">{clinic.address}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl bg-white p-6 shadow-lg">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900">
            <CalendarDays size={20} className="text-teal-600" /> Book Appointment
          </h2>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Select Doctor *</label>
            <select required value={form.doctor_id} onChange={(e) => setForm({ ...form, doctor_id: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500">
              <option value="">Choose a doctor</option>
              {doctors.map((d) => (
                <option key={d.id} value={d.id}>Dr. {d.name} — {d.specialty} (Rs. {d.consultation_fee})</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Your Name *</label>
              <input required value={form.patient_name} onChange={(e) => setForm({ ...form, patient_name: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Phone *</label>
              <input required value={form.patient_phone} onChange={(e) => setForm({ ...form, patient_phone: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
              <input type="email" value={form.patient_email} onChange={(e) => setForm({ ...form, patient_email: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Age *</label>
              <input required type="number" min="0" max="150" value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Gender</label>
              <select value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500">
                <option value="">Select</option>
                {GENDERS.map((g) => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Date *</label>
              <input type="date" required value={form.appointment_date} onChange={(e) => setForm({ ...form, appointment_date: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Preferred Time</label>
              <input type="time" value={form.appointment_time} onChange={(e) => setForm({ ...form, appointment_time: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
          </div>

          <button type="submit" className="w-full rounded-lg bg-teal-600 py-3 text-sm font-medium text-white hover:bg-teal-700">
            Book Appointment
          </button>
        </form>
      </div>
    </div>
  );
}
