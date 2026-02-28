import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { fetchPublicAPI } from '../../api';
import LoadingSpinner from '../../components/LoadingSpinner';
import ConvoKraftBot from '../../components/ConvoKraftBot';
import { CalendarDays, CheckCircle, ListOrdered, CalendarSearch, Clock, MessageSquare } from 'lucide-react';
import { useToast } from '../../components/Toast';
import { GENDERS, getLocalToday } from '../../utils/constants';
import { savePatientInfo, getPatientInfo } from '../../utils/patientStore';

function generateTimeSlots(from, to, intervalMinutes = 30) {
  if (!from || !to) return [];
  const slots = [];
  const [fh, fm] = from.split(':').map(Number);
  const [th, tm] = to.split(':').map(Number);
  let current = fh * 60 + fm;
  const end = th * 60 + tm;
  while (current < end) {
    const h = Math.floor(current / 60);
    const m = current % 60;
    const val = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
    const hour12 = h % 12 || 12;
    const ampm = h < 12 ? 'AM' : 'PM';
    const label = `${hour12}:${String(m).padStart(2, '0')} ${ampm}`;
    slots.push({ value: val, label });
    current += intervalMinutes;
  }
  return slots;
}

export default function BookingPage() {
  const { slug } = useParams();
  const [clinic, setClinic] = useState(null);
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [booked, setBooked] = useState(null);
  const today = getLocalToday();
  const saved = getPatientInfo();
  const [form, setForm] = useState({ doctor_id: '', patient_name: saved.name || '', patient_phone: saved.phone || '', patient_email: saved.email || '', age: '', gender: '', appointment_date: today, appointment_time: '', notes: '' });
  const [submitting, setSubmitting] = useState(false);
  const toast = useToast();

  const selectedDoctor = doctors.find((d) => d.id === form.doctor_id);

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

    // Frontend validations
    if (form.appointment_date < today) {
      toast.error('Cannot book appointment for a past date.');
      return;
    }
    if (!form.appointment_time) {
      toast.error('Please select a time slot.');
      return;
    }

    setSubmitting(true);
    const res = await fetchPublicAPI('/api/public/book', {
      method: 'POST',
      body: JSON.stringify({ clinic_slug: slug, ...form }),
    });
    setSubmitting(false);
    if (res.status === 'success') {
      savePatientInfo({ name: form.patient_name, phone: form.patient_phone, email: form.patient_email });
      setBooked(res.data);
    } else {
      toast.error(res.message || 'Booking failed');
    }
  };

  if (loading) return <LoadingSpinner />;

  if (!clinic) {
    return (
      <div className="flex items-center justify-center px-4 py-20">
        <p className="text-lg text-gray-500">Clinic not found.</p>
      </div>
    );
  }

  if (booked) {
    return (
      <div className="flex items-center justify-center px-4 py-12">
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

          {/* Demo SMS Preview */}
          <div className="mt-5 rounded-xl border border-green-200 bg-green-50 p-4 text-left">
            <div className="mb-2 flex items-center gap-1.5">
              <MessageSquare size={14} className="text-green-600" />
              <span className="text-xs font-semibold text-green-700">SMS Confirmation Preview</span>
            </div>
            <p className="whitespace-pre-line text-xs leading-relaxed text-green-800">
{`Hi ${form.patient_name}! Your appointment is confirmed.

Token: ${booked.token_number}
Doctor: Dr. ${doctors.find(d => d.id === form.doctor_id)?.name || ''}
Date: ${booked.appointment_date}${booked.appointment_time ? `\nTime: ${booked.appointment_time}` : ''}
Clinic: ${booked.clinic_name}

Please arrive 10 mins early. - CareDesk`}
            </p>
            <p className="mt-2 text-[10px] italic text-amber-600">
              * Twilio trial account — SMS is sent only to verified numbers. With a premium account, all patients would receive this SMS automatically.
            </p>
          </div>

          <div className="mt-5 flex flex-col gap-2">
            <a
              href={`${import.meta.env.BASE_URL}queue-display/${slug}`}
              className="flex items-center justify-center gap-2 rounded-lg bg-yellow-50 px-4 py-2.5 text-sm font-medium text-yellow-700 hover:bg-yellow-100"
            >
              <ListOrdered size={16} /> Check Live Queue
            </a>
            <a
              href={`${import.meta.env.BASE_URL}my-appointments`}
              className="flex items-center justify-center gap-2 rounded-lg bg-teal-50 px-4 py-2.5 text-sm font-medium text-teal-700 hover:bg-teal-100"
            >
              <CalendarSearch size={16} /> Track My Appointments
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6">
      <div className="mx-auto max-w-lg">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-gray-900">{clinic.name}</h1>
          <p className="text-sm text-gray-500">{clinic.address}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl bg-white p-6 shadow-lg">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900">
            <CalendarDays size={20} className="text-teal-600" /> Book Appointment
          </h2>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Select Doctor *</label>
            <select required value={form.doctor_id} onChange={(e) => setForm({ ...form, doctor_id: e.target.value, appointment_time: '' })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500">
              <option value="">Choose a doctor</option>
              {doctors.map((d) => (
                <option key={d.id} value={d.id}>Dr. {d.name} — {d.specialty} (Rs. {d.consultation_fee})</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Your Name *</label>
              <input required value={form.patient_name} onChange={(e) => setForm({ ...form, patient_name: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Phone *</label>
              <input required value={form.patient_phone} onChange={(e) => setForm({ ...form, patient_phone: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Email *</label>
              <input type="email" required value={form.patient_email} onChange={(e) => setForm({ ...form, patient_email: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
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
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Appointment Date *</label>
            <input type="date" required min={today} value={form.appointment_date} onChange={(e) => setForm({ ...form, appointment_date: e.target.value, appointment_time: '' })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
          </div>

          {/* Time Slots */}
          <div>
            <label className="mb-2 flex items-center gap-1.5 text-sm font-medium text-gray-700">
              <Clock size={14} className="text-teal-600" /> Select Time Slot *
            </label>
            {!selectedDoctor ? (
              <p className="rounded-lg border border-dashed border-gray-200 px-3 py-4 text-center text-xs text-gray-400">
                Please select a doctor first to see available time slots
              </p>
            ) : (() => {
              const slots = generateTimeSlots(selectedDoctor.available_from, selectedDoctor.available_to);
              if (slots.length === 0) return (
                <p className="rounded-lg border border-dashed border-gray-200 px-3 py-4 text-center text-xs text-gray-400">
                  No time slots available for this doctor
                </p>
              );
              const now = new Date();
              const nowStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
              const isToday = form.appointment_date === today;
              return (
                <div className="flex flex-wrap gap-2">
                  {slots.map((slot) => {
                    const isPast = isToday && slot.value <= nowStr;
                    const isSelected = form.appointment_time === slot.value;
                    return (
                      <button
                        key={slot.value}
                        type="button"
                        disabled={isPast}
                        onClick={() => setForm({ ...form, appointment_time: slot.value })}
                        className={`rounded-lg border px-3 py-2 text-xs font-medium transition-all ${
                          isPast
                            ? 'cursor-not-allowed border-gray-100 bg-gray-50 text-gray-300 line-through'
                            : isSelected
                              ? 'border-teal-500 bg-teal-50 text-teal-700 ring-1 ring-teal-500'
                              : 'border-gray-200 bg-white text-gray-600 hover:border-teal-300 hover:bg-teal-50'
                        }`}
                      >
                        {slot.label}
                      </button>
                    );
                  })}
                </div>
              );
            })()}
            {selectedDoctor?.available_from && selectedDoctor?.available_to && (
              <p className="mt-1.5 text-xs text-gray-400">Dr. {selectedDoctor.name} — {selectedDoctor.available_from} to {selectedDoctor.available_to}</p>
            )}
          </div>

          <button type="submit" disabled={submitting} className="w-full rounded-lg bg-teal-600 py-3 text-sm font-medium text-white hover:bg-teal-700 disabled:opacity-50">
            {submitting ? 'Booking...' : 'Book Appointment'}
          </button>
        </form>
      </div>
      <ConvoKraftBot />
    </div>
  );
}
