import { useState, useEffect, useRef, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { fetchPublicAPI } from '../../api';
import LoadingSpinner from '../../components/LoadingSpinner';
import StatusBadge from '../../components/StatusBadge';
import { Phone, Search, Calendar, FileText, MessageSquare, MapPin, Filter, X } from 'lucide-react';
import { getPatientInfo } from '../../utils/patientStore';
import { getLocalToday } from '../../utils/constants';

export default function MyAppointmentsPage() {
  const saved = getPatientInfo();
  const [phone, setPhone] = useState(saved.phone || '');
  const [appointments, setAppointments] = useState(null);
  const [loading, setLoading] = useState(false);
  const autoSearched = useRef(false);

  // Tab state
  const [activeTab, setActiveTab] = useState('upcoming');

  // Filters
  const [filterDoctor, setFilterDoctor] = useState('');
  const [filterClinic, setFilterClinic] = useState('');
  const [filterDate, setFilterDate] = useState('');

  // Auto-search if phone was pre-filled from localStorage
  useEffect(() => {
    if (saved.phone && !autoSearched.current) {
      autoSearched.current = true;
      doLookup(saved.phone);
    }
  }, []);

  const doLookup = async (phoneNum) => {
    if (!phoneNum.trim()) return;
    setLoading(true);
    const res = await fetchPublicAPI('/api/public/my-appointments', {
      method: 'POST',
      body: JSON.stringify({ phone: phoneNum.trim() }),
    });
    if (res.status === 'success') {
      setAppointments(res.data);
    } else {
      setAppointments([]);
    }
    setLoading(false);
  };

  const handleLookup = async (e) => {
    e.preventDefault();
    doLookup(phone);
  };

  const today = getLocalToday();

  // Split into upcoming / past
  const upcoming = useMemo(() =>
    (appointments || []).filter(
      (a) => a.appointment_date >= today && a.status !== 'cancelled' && a.status !== 'completed'
    ), [appointments, today]);

  const past = useMemo(() =>
    (appointments || []).filter(
      (a) => a.appointment_date < today || a.status === 'completed' || a.status === 'cancelled'
    ), [appointments, today]);

  const currentList = activeTab === 'upcoming' ? upcoming : past;

  // Unique doctors & clinics for filters (from current tab)
  const doctors = useMemo(() => {
    const set = new Set();
    currentList.forEach((a) => { if (a.doctor_name) set.add(a.doctor_name); });
    return [...set].sort();
  }, [currentList]);

  const clinics = useMemo(() => {
    const set = new Set();
    currentList.forEach((a) => { if (a.clinic_name) set.add(a.clinic_name); });
    return [...set].sort();
  }, [currentList]);

  // Apply filters
  const filtered = useMemo(() => {
    return currentList.filter((a) => {
      if (filterDoctor && a.doctor_name !== filterDoctor) return false;
      if (filterClinic && a.clinic_name !== filterClinic) return false;
      if (filterDate && a.appointment_date !== filterDate) return false;
      return true;
    });
  }, [currentList, filterDoctor, filterClinic, filterDate]);

  const hasFilters = filterDoctor || filterClinic || filterDate;
  const clearFilters = () => { setFilterDoctor(''); setFilterClinic(''); setFilterDate(''); };

  // Show filters only when there are 2+ appointments in current tab
  const showFilters = currentList.length >= 2;

  return (
    <div className="px-4 py-6">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">My Appointments</h1>
          <p className="text-sm text-gray-500">Enter your phone number to view your appointments</p>
        </div>

        {/* Phone lookup form */}
        <form onSubmit={handleLookup} className="mb-6 flex gap-2">
          <div className="relative flex-1">
            <Phone className="absolute left-3 top-3 text-gray-400" size={16} />
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Enter your phone number"
              required
              className="w-full rounded-xl border border-gray-200 bg-white py-2.5 pl-10 pr-4 text-sm shadow-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 rounded-xl bg-teal-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-teal-700 disabled:opacity-50"
          >
            <Search size={14} /> {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        {loading && <LoadingSpinner />}

        {/* Results */}
        {appointments !== null && !loading && (
          <>
            {appointments.length === 0 ? (
              <div className="rounded-2xl bg-white p-8 text-center shadow-sm">
                <p className="text-gray-500">No appointments found for this phone number.</p>
                <Link to="/clinics" className="mt-3 inline-block text-sm font-medium text-teal-600 hover:text-teal-700">
                  Book an appointment
                </Link>
              </div>
            ) : (
              <>
                {/* Tabs */}
                <div className="mb-4 flex rounded-xl bg-gray-100 p-1">
                  <button
                    onClick={() => { setActiveTab('upcoming'); clearFilters(); }}
                    className={`flex-1 rounded-lg py-2 text-sm font-medium transition-colors ${
                      activeTab === 'upcoming'
                        ? 'bg-white text-teal-700 shadow-sm'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    Upcoming ({upcoming.length})
                  </button>
                  <button
                    onClick={() => { setActiveTab('past'); clearFilters(); }}
                    className={`flex-1 rounded-lg py-2 text-sm font-medium transition-colors ${
                      activeTab === 'past'
                        ? 'bg-white text-teal-700 shadow-sm'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    Past ({past.length})
                  </button>
                </div>

                {/* Filters */}
                {showFilters && (
                  <div className="mb-4 rounded-xl bg-white p-3 shadow-sm">
                    <div className="mb-2 flex items-center justify-between">
                      <div className="flex items-center gap-1.5 text-[10px] font-semibold uppercase text-gray-400">
                        <Filter size={11} /> Filters
                      </div>
                      {hasFilters && (
                        <button onClick={clearFilters} className="flex items-center gap-1 text-xs text-teal-600 hover:text-teal-800">
                          <X size={11} /> Clear
                        </button>
                      )}
                    </div>
                    <div className="grid gap-2 sm:grid-cols-3">
                      <select
                        value={filterDoctor}
                        onChange={(e) => setFilterDoctor(e.target.value)}
                        className="w-full rounded-lg border border-gray-200 px-2.5 py-1.5 text-xs text-gray-700 focus:border-teal-400 focus:outline-none"
                      >
                        <option value="">All Doctors</option>
                        {doctors.map((d) => <option key={d} value={d}>Dr. {d}</option>)}
                      </select>
                      <select
                        value={filterClinic}
                        onChange={(e) => setFilterClinic(e.target.value)}
                        className="w-full rounded-lg border border-gray-200 px-2.5 py-1.5 text-xs text-gray-700 focus:border-teal-400 focus:outline-none"
                      >
                        <option value="">All Clinics</option>
                        {clinics.map((c) => <option key={c} value={c}>{c}</option>)}
                      </select>
                      <input
                        type="date"
                        value={filterDate}
                        onChange={(e) => setFilterDate(e.target.value)}
                        className="w-full rounded-lg border border-gray-200 px-2.5 py-1.5 text-xs text-gray-700 focus:border-teal-400 focus:outline-none"
                      />
                    </div>
                  </div>
                )}

                {/* Appointment List */}
                {filtered.length === 0 ? (
                  <div className="rounded-2xl bg-white p-8 text-center shadow-sm">
                    {hasFilters ? (
                      <>
                        <p className="text-gray-500">No appointments match your filters.</p>
                        <button onClick={clearFilters} className="mt-2 text-sm text-teal-600 hover:text-teal-800 underline">Clear filters</button>
                      </>
                    ) : (
                      <p className="text-gray-500">
                        {activeTab === 'upcoming' ? 'No upcoming appointments.' : 'No past appointments.'}
                      </p>
                    )}
                  </div>
                ) : (
                  <div className="space-y-3">
                    {filtered.map((a) => (
                      <AppointmentCard key={a.id} appointment={a} isUpcoming={activeTab === 'upcoming'} />
                    ))}
                  </div>
                )}
              </>
            )}
          </>
        )}

      </div>
    </div>
  );
}

function AppointmentCard({ appointment: a, isUpcoming }) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-teal-600">{a.token_number}</span>
            <StatusBadge status={a.status} />
          </div>
          <p className="mt-1 text-sm text-gray-900">Dr. {a.doctor_name}</p>
          <p className="flex items-center gap-1 text-xs text-gray-500">
            <MapPin size={12} /> {a.clinic_name}
          </p>
          <p className="flex items-center gap-1 text-xs text-gray-500">
            <Calendar size={12} /> {a.appointment_date} {a.appointment_time && `at ${a.appointment_time}`}
          </p>
        </div>
      </div>

      {/* Action links */}
      <div className="mt-3 flex flex-wrap gap-2">
        {isUpcoming && a.clinic_slug && (
          <Link
            to={`/queue-display/${a.clinic_slug}`}
            className="rounded-lg bg-yellow-50 px-3 py-1.5 text-xs font-medium text-yellow-700 hover:bg-yellow-100"
          >
            View Queue
          </Link>
        )}
        {a.status === 'completed' && a.has_prescription && (
          <Link
            to={`/prescription/${a.prescription_id}`}
            className="flex items-center gap-1 rounded-lg bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700 hover:bg-blue-100"
          >
            <FileText size={12} /> View Prescription
          </Link>
        )}
        {a.status === 'completed' && !a.feedback_score && (
          <Link
            to={`/feedback/${a.id}`}
            className="flex items-center gap-1 rounded-lg bg-purple-50 px-3 py-1.5 text-xs font-medium text-purple-700 hover:bg-purple-100"
          >
            <MessageSquare size={12} /> Give Feedback
          </Link>
        )}
      </div>
    </div>
  );
}
