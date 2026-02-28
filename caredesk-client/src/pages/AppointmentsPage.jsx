import { useState, useEffect, useMemo } from 'react';
import { fetchAPI } from '../api';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { Plus, CalendarDays, RefreshCw, Clock, Filter, ArrowUpDown, Users, Stethoscope, ChevronDown, ChevronRight, Search } from 'lucide-react';
import { useToast } from '../components/Toast';
import { getLocalToday, STATUS_LABELS } from '../utils/constants';

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

const STATUS_ORDER = { 'in-consultation': 0, 'in-queue': 1, booked: 2, completed: 3, cancelled: 4, 'no-show': 5 };

const SORT_OPTIONS = [
  { value: 'time-asc', label: 'Time (earliest first)' },
  { value: 'time-desc', label: 'Time (latest first)' },
  { value: 'status', label: 'Status (active first)' },
  { value: 'token', label: 'Token number' },
  { value: 'patient', label: 'Patient name (A-Z)' },
];

const STATUS_TABS = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active', statuses: ['in-consultation', 'in-queue', 'booked'] },
  { value: 'in-consultation', label: 'With Doctor' },
  { value: 'in-queue', label: 'In Queue' },
  { value: 'booked', label: 'Booked' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'no-show', label: 'No Show' },
];

// Unified teal theme for all doctor sections
const DOC_THEME = { bg: 'bg-teal-50', border: 'border-teal-200', text: 'text-teal-700', dot: 'bg-teal-500', badge: 'bg-teal-100 text-teal-700' };

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [filterDate, setFilterDate] = useState(getLocalToday());
  const [filterDoctor, setFilterDoctor] = useState('all');
  const [statusTab, setStatusTab] = useState('all');
  const [sortBy, setSortBy] = useState('time-asc');
  const [viewMode, setViewMode] = useState('grouped'); // 'grouped' | 'flat'
  const [searchTerm, setSearchTerm] = useState('');
  const [collapsedDocs, setCollapsedDocs] = useState({});
  const [form, setForm] = useState({ doctor_id: '', patient_id: '', appointment_date: getLocalToday(), appointment_time: '', notes: '' });
  const toast = useToast();

  useEffect(() => { loadData(); }, [filterDate]);

  const loadData = async () => {
    const [apptRes, docRes, patRes] = await Promise.all([
      fetchAPI(`/api/appointments?date=${filterDate}`),
      fetchAPI('/api/doctors'),
      fetchAPI('/api/patients'),
    ]);
    if (apptRes.status === 'success') setAppointments(apptRes.data);
    if (docRes.status === 'success') setDoctors(docRes.data);
    if (patRes.status === 'success') setPatients(patRes.data);
    setLoading(false);
    setRefreshing(false);
  };

  const handleRefresh = () => { setRefreshing(true); loadData(); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    const res = await fetchAPI('/api/appointments', { method: 'POST', body: JSON.stringify(form) });
    setSubmitting(false);
    if (res.status === 'error') { toast.error(res.message || 'Failed to book appointment'); return; }
    toast.success('Appointment booked successfully');
    setShowModal(false);
    setForm({ doctor_id: '', patient_id: '', appointment_date: getLocalToday(), appointment_time: '', notes: '' });
    loadData();
  };

  const updateStatus = async (id, status) => {
    const res = await fetchAPI(`/api/appointments/${id}`, { method: 'PUT', body: JSON.stringify({ status }) });
    if (res.status === 'error') { toast.error(res.message || 'Failed to update status'); return; }
    toast.success(`Status updated to "${STATUS_LABELS[status] || status}"`);
    loadData();
  };

  // Pre-status filtered list (doctor + search applied, but NOT status tab)
  // Used for computing accurate status tab counts
  const preStatusFiltered = useMemo(() => {
    let list = [...appointments];

    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      list = list.filter(a =>
        a.patient_name?.toLowerCase().includes(q) ||
        a.doctor_name?.toLowerCase().includes(q) ||
        a.token_number?.toLowerCase().includes(q) ||
        a.patient_phone?.includes(q)
      );
    }

    if (filterDoctor !== 'all') {
      list = list.filter(a => a.doctor_id === filterDoctor);
    }

    return list;
  }, [appointments, filterDoctor, searchTerm]);

  // Final filtered + sorted list (status tab also applied)
  const filteredSorted = useMemo(() => {
    let list = [...preStatusFiltered];

    // Status filter
    if (statusTab === 'active') {
      list = list.filter(a => ['in-consultation', 'in-queue', 'booked'].includes(a.status));
    } else if (statusTab !== 'all') {
      list = list.filter(a => a.status === statusTab);
    }

    // Sort
    list.sort((a, b) => {
      switch (sortBy) {
        case 'time-asc': return (a.appointment_time || '').localeCompare(b.appointment_time || '');
        case 'time-desc': return (b.appointment_time || '').localeCompare(a.appointment_time || '');
        case 'status': return (STATUS_ORDER[a.status] ?? 9) - (STATUS_ORDER[b.status] ?? 9);
        case 'token': {
          const numA = parseInt((a.token_number || '').split('-')[1]) || 0;
          const numB = parseInt((b.token_number || '').split('-')[1]) || 0;
          return numA - numB;
        }
        case 'patient': return (a.patient_name || '').localeCompare(b.patient_name || '');
        default: return 0;
      }
    });

    return list;
  }, [preStatusFiltered, statusTab, sortBy]);

  // Group by doctor
  const groupedByDoctor = useMemo(() => {
    const groups = {};
    filteredSorted.forEach(a => {
      const key = a.doctor_id;
      if (!groups[key]) {
        groups[key] = { doctor_name: a.doctor_name, doctor_id: a.doctor_id, appointments: [] };
      }
      groups[key].appointments.push(a);
    });
    // Sort groups by doctor name
    return Object.values(groups).sort((a, b) => a.doctor_name.localeCompare(b.doctor_name));
  }, [filteredSorted]);

  // Status counts for tabs — based on pre-status filtered list so counts match current doctor/search filters
  const statusCounts = useMemo(() => {
    const counts = { all: preStatusFiltered.length, active: 0 };
    preStatusFiltered.forEach(a => {
      counts[a.status] = (counts[a.status] || 0) + 1;
      if (['in-consultation', 'in-queue', 'booked'].includes(a.status)) counts.active++;
    });
    return counts;
  }, [preStatusFiltered]);

  const toggleDocCollapse = (docId) => {
    setCollapsedDocs(prev => ({ ...prev, [docId]: !prev[docId] }));
  };

  if (loading) return <LoadingSpinner />;

  const renderActionButtons = (a) => (
    <div className="flex flex-wrap gap-1">
      {a.status === 'booked' && (
        <button onClick={() => updateStatus(a.id, 'in-queue')} className="rounded-md bg-yellow-100 px-2.5 py-1 text-xs font-medium text-yellow-700 hover:bg-yellow-200 transition-colors">
          Add to Queue
        </button>
      )}
      {a.status === 'in-queue' && (
        <button onClick={() => updateStatus(a.id, 'in-consultation')} className="rounded-md bg-purple-100 px-2.5 py-1 text-xs font-medium text-purple-700 hover:bg-purple-200 transition-colors">
          Start Consult
        </button>
      )}
      {a.status === 'in-consultation' && (
        <a href={`${import.meta.env.BASE_URL}consultation/${a.id}`} className="rounded-md bg-teal-100 px-2.5 py-1 text-xs font-medium text-teal-700 hover:bg-teal-200 transition-colors">
          Write Rx
        </a>
      )}
      {(a.status === 'booked' || a.status === 'in-queue') && (
        <button onClick={() => updateStatus(a.id, 'no-show')} className="rounded-md bg-orange-100 px-2.5 py-1 text-xs font-medium text-orange-700 hover:bg-orange-200 transition-colors">
          No Show
        </button>
      )}
      {a.status === 'booked' && (
        <button onClick={() => updateStatus(a.id, 'cancelled')} className="rounded-md bg-red-100 px-2.5 py-1 text-xs font-medium text-red-700 hover:bg-red-200 transition-colors">
          Cancel
        </button>
      )}
    </div>
  );

  const renderRow = (a, showDoctor = true) => (
    <tr key={a.id} className="hover:bg-gray-50/80 transition-colors">
      <td className="px-4 py-3">
        <span className="font-bold text-teal-600 text-sm">{a.token_number}</span>
      </td>
      <td className="px-4 py-3">
        <p className="font-medium text-gray-900 text-sm">{a.patient_name}</p>
        <p className="text-xs text-gray-400">{a.patient_phone}</p>
      </td>
      {showDoctor && <td className="px-4 py-3 text-sm text-gray-600">Dr. {a.doctor_name}</td>}
      <td className="px-4 py-3 text-sm text-gray-600">{a.appointment_time || '—'}</td>
      <td className="px-4 py-3"><StatusBadge status={a.status} /></td>
      <td className="px-4 py-3">{renderActionButtons(a)}</td>
    </tr>
  );

  const renderDoctorGroup = (group, idx) => {
    const colors = DOC_THEME;
    const isCollapsed = collapsedDocs[group.doctor_id];
    const activeCount = group.appointments.filter(a => ['in-consultation', 'in-queue'].includes(a.status)).length;
    const completedCount = group.appointments.filter(a => a.status === 'completed').length;
    const doc = doctors.find(d => d.id === group.doctor_id);

    return (
      <div key={group.doctor_id} className={`rounded-xl border ${colors.border} overflow-hidden mb-4`}>
        {/* Doctor header */}
        <button
          onClick={() => toggleDocCollapse(group.doctor_id)}
          className={`w-full flex items-center justify-between px-4 py-3 ${colors.bg} hover:opacity-90 transition-opacity`}
        >
          <div className="flex items-center gap-3">
            <div className={`w-2.5 h-2.5 rounded-full ${colors.dot}`} />
            <div className="text-left">
              <span className={`font-semibold ${colors.text}`}>Dr. {group.doctor_name}</span>
              {doc && <span className="text-xs text-gray-500 ml-2">{doc.specialty}</span>}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {activeCount > 0 && (
              <span className="rounded-full bg-yellow-100 text-yellow-700 px-2 py-0.5 text-xs font-medium">
                {activeCount} active
              </span>
            )}
            <span className="rounded-full bg-green-100 text-green-700 px-2 py-0.5 text-xs font-medium">
              {completedCount} done
            </span>
            <span className={`rounded-full ${colors.badge} px-2 py-0.5 text-xs font-bold`}>
              {group.appointments.length}
            </span>
            {isCollapsed ? <ChevronRight size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
          </div>
        </button>

        {/* Appointments table */}
        {!isCollapsed && (
          <div className="overflow-x-auto">
          <table className="w-full min-w-[600px] text-sm">
            <thead className="bg-gray-50/80">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Token</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Patient</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {group.appointments.map(a => renderRow(a, false))}
            </tbody>
          </table>
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Appointments</h1>
          <p className="text-sm text-gray-500">
            {filteredSorted.length} of {appointments.length} appointment(s)
            {filterDate === getLocalToday() ? ' for today' : ` on ${filterDate}`}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <input
            type="date"
            value={filterDate}
            onChange={(e) => setFilterDate(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
          />
          <button onClick={handleRefresh} disabled={refreshing} className="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50" title="Refresh">
            <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} />
          </button>
          <button onClick={() => setShowModal(true)} className="flex items-center gap-2 rounded-lg bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700 transition-colors">
            <Plus size={16} /> Book Appointment
          </button>
        </div>
      </div>

      {/* Status tabs */}
      <div className="mb-4 flex flex-wrap gap-1.5">
        {STATUS_TABS.map(tab => {
          const count = statusCounts[tab.value] || 0;
          const isActive = statusTab === tab.value;
          return (
            <button
              key={tab.value}
              onClick={() => setStatusTab(tab.value)}
              className={`rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-teal-600 text-white shadow-sm'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {tab.label}
              {count > 0 && (
                <span className={`ml-1.5 rounded-full px-1.5 py-0.5 text-[10px] font-bold ${
                  isActive ? 'bg-white/20 text-white' : 'bg-gray-200 text-gray-700'
                }`}>
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Filter bar */}
      <div className="mb-4 flex flex-wrap items-center gap-2 rounded-xl border border-gray-100 bg-white p-3 shadow-sm">
        {/* Search */}
        <div className="relative flex-1 min-w-[180px]">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search patient, doctor, token..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border border-gray-200 pl-8 pr-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
          />
        </div>

        {/* Doctor filter */}
        <div className="flex items-center gap-1.5">
          <Stethoscope size={14} className="text-gray-400" />
          <select
            value={filterDoctor}
            onChange={(e) => setFilterDoctor(e.target.value)}
            className="rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
          >
            <option value="all">All Doctors</option>
            {doctors.map(d => {
              const count = appointments.filter(a => a.doctor_id === d.id).length;
              return <option key={d.id} value={d.id}>Dr. {d.name} ({count})</option>;
            })}
          </select>
        </div>

        {/* Sort */}
        <div className="flex items-center gap-1.5">
          <ArrowUpDown size={14} className="text-gray-400" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
          >
            {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>

        {/* View toggle */}
        <div className="flex rounded-lg border border-gray-200 overflow-hidden">
          <button
            onClick={() => setViewMode('grouped')}
            className={`px-3 py-2 text-xs font-medium transition-colors ${
              viewMode === 'grouped' ? 'bg-teal-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
            title="Group by doctor"
          >
            <Users size={14} />
          </button>
          <button
            onClick={() => setViewMode('flat')}
            className={`px-3 py-2 text-xs font-medium transition-colors ${
              viewMode === 'flat' ? 'bg-teal-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
            title="Flat list"
          >
            <Filter size={14} />
          </button>
        </div>
      </div>

      {/* Content */}
      {filteredSorted.length === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-gray-200 p-12 text-center">
          <CalendarDays className="mx-auto mb-3 text-gray-300" size={40} />
          <p className="text-gray-500">
            {appointments.length === 0 ? 'No appointments for this day.' : 'No appointments match your filters.'}
          </p>
          {appointments.length > 0 && (
            <button
              onClick={() => { setFilterDoctor('all'); setStatusTab('all'); setSearchTerm(''); }}
              className="mt-2 text-sm text-teal-600 hover:underline"
            >
              Clear all filters
            </button>
          )}
        </div>
      ) : viewMode === 'grouped' ? (
        // ──── Grouped by Doctor view ────
        <div>
          {groupedByDoctor.map((group, idx) => renderDoctorGroup(group, idx))}
        </div>
      ) : (
        // ──── Flat table view ────
        <div className="overflow-x-auto rounded-xl border border-gray-100 bg-white shadow-sm">
          <table className="w-full min-w-[700px] text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Token</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Patient</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Doctor</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filteredSorted.map(a => renderRow(a, true))}
            </tbody>
          </table>
        </div>
      )}

      {/* Quick stats bar */}
      {appointments.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-3 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-purple-500" />
            {statusCounts['in-consultation'] || 0} with doctor
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-yellow-500" />
            {statusCounts['in-queue'] || 0} in queue
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            {statusCounts['booked'] || 0} upcoming
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            {statusCounts['completed'] || 0} completed
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500" />
            {statusCounts['cancelled'] || 0} cancelled
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-orange-500" />
            {statusCounts['no-show'] || 0} no-show
          </span>
        </div>
      )}

      {/* Book Appointment Modal */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Book Appointment">
        {(() => {
          const selectedDoc = doctors.find((d) => d.id === form.doctor_id);
          const timeSlots = selectedDoc ? generateTimeSlots(selectedDoc.available_from, selectedDoc.available_to) : [];
          const today = getLocalToday();
          const nowMinutes = (() => { const d = new Date(); return d.getHours() * 60 + d.getMinutes(); })();

          return (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Doctor *</label>
                <select required value={form.doctor_id} onChange={(e) => setForm({ ...form, doctor_id: e.target.value, appointment_time: '' })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500">
                  <option value="">Select doctor</option>
                  {doctors.map((d) => <option key={d.id} value={d.id}>Dr. {d.name} — {d.specialty}</option>)}
                </select>
                {selectedDoc && (
                  <p className="mt-1 flex items-center gap-1 text-xs text-teal-600">
                    <Clock size={11} />
                    Available: {selectedDoc.available_from} — {selectedDoc.available_to}
                  </p>
                )}
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Patient *</label>
                <select required value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500">
                  <option value="">Select patient</option>
                  {patients.map((p) => <option key={p.id} value={p.id}>{p.name} — {p.phone}</option>)}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Date *</label>
                <input type="date" required value={form.appointment_date} onChange={(e) => setForm({ ...form, appointment_date: e.target.value, appointment_time: '' })} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
              </div>
              {selectedDoc && (
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">Time Slot *</label>
                  {timeSlots.length > 0 ? (
                    <div className="grid grid-cols-3 sm:grid-cols-4 gap-2 max-h-40 overflow-y-auto">
                      {timeSlots.map((slot) => {
                        const isToday = form.appointment_date === today;
                        const [sh, sm] = slot.value.split(':').map(Number);
                        const slotMin = sh * 60 + sm;
                        const isPast = isToday && slotMin <= nowMinutes;
                        return (
                          <button key={slot.value} type="button" disabled={isPast}
                            onClick={() => setForm({ ...form, appointment_time: slot.value })}
                            className={`rounded-lg border px-2 py-1.5 text-xs font-medium transition-colors ${
                              form.appointment_time === slot.value
                                ? 'border-teal-500 bg-teal-50 text-teal-700'
                                : isPast
                                  ? 'border-gray-100 bg-gray-50 text-gray-300 line-through cursor-not-allowed'
                                  : 'border-gray-200 bg-white text-gray-600 hover:border-teal-300 hover:bg-teal-50'
                            }`}
                          >
                            {slot.label}
                          </button>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-xs text-gray-400">No time slots available</p>
                  )}
                </div>
              )}
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Notes</label>
                <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={2} className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
              </div>
              <button type="submit" disabled={submitting} className="w-full rounded-lg bg-teal-600 py-2.5 text-sm font-medium text-white hover:bg-teal-700 disabled:opacity-50">
                {submitting ? 'Booking...' : 'Book Appointment'}
              </button>
            </form>
          );
        })()}
      </Modal>
    </div>
  );
}
