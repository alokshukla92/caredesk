import { useState, useEffect } from 'react';
import { fetchAPI } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  CalendarDays, Users, ListOrdered, CheckCircle,
  Stethoscope, Star, Clock, TrendingUp, RefreshCw,
  Activity, Pill, XCircle, AlertTriangle, ChevronLeft, ChevronRight,
  UserCheck,
} from 'lucide-react';
import { getLocalToday, STATUS_COLORS, STATUS_LABELS } from '../utils/constants';

function MiniCard({ icon: Icon, label, value, sub, color = 'teal' }) {
  const colors = {
    teal: 'bg-teal-50 text-teal-600',
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    purple: 'bg-purple-50 text-purple-600',
    red: 'bg-red-50 text-red-600',
    orange: 'bg-orange-50 text-orange-600',
  };
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
      <div className="flex items-center gap-3">
        <div className={`rounded-lg p-2 ${colors[color] || colors.teal}`}>
          <Icon size={18} />
        </div>
        <div className="min-w-0">
          <p className="text-xs text-gray-400 truncate">{label}</p>
          <p className="text-xl font-bold text-gray-900">{value}</p>
          {sub && <p className="text-[10px] text-gray-400 mt-0.5">{sub}</p>}
        </div>
      </div>
    </div>
  );
}

function WeeklyBarChart({ data }) {
  const max = Math.max(...data.map((d) => d.count), 1);
  return (
    <div className="flex items-end gap-2" style={{ height: 110 }}>
      {data.map((d, i) => {
        const h = max > 0 ? Math.max((d.count / max) * 100, 6) : 6;
        const isHighest = d.count === max && d.count > 0;
        return (
          <div key={i} className="flex-1 flex flex-col items-center gap-1">
            <span className={`text-[10px] font-bold ${isHighest ? 'text-teal-600' : 'text-gray-400'}`}>
              {d.count > 0 ? d.count : ''}
            </span>
            <div
              className={`w-full rounded-md transition-all duration-500 ${isHighest ? 'bg-teal-500' : 'bg-teal-300'}`}
              style={{ height: `${h}%`, minHeight: d.count > 0 ? 12 : 4 }}
              title={`${d.day} (${d.date}): ${d.count} appointments`}
            />
            <span className={`text-[10px] font-medium ${isHighest ? 'text-teal-600' : 'text-gray-400'}`}>{d.day}</span>
          </div>
        );
      })}
    </div>
  );
}

function HourlyHeatmap({ peakHours }) {
  // Show hours 08:00 - 20:00 as a heatmap grid
  const hourMap = {};
  (peakHours || []).forEach((ph) => {
    hourMap[ph.hour] = ph.count;
  });

  const hours = [];
  for (let h = 8; h <= 20; h++) {
    const label = `${String(h).padStart(2, '0')}:00`;
    hours.push({ hour: h, label, count: hourMap[label] || 0 });
  }

  const max = Math.max(...hours.map((h) => h.count), 1);

  const getColor = (count) => {
    if (count === 0) return 'bg-gray-100 text-gray-300';
    const ratio = count / max;
    if (ratio >= 0.75) return 'bg-teal-600 text-white';
    if (ratio >= 0.5) return 'bg-teal-400 text-white';
    if (ratio >= 0.25) return 'bg-teal-200 text-teal-700';
    return 'bg-teal-100 text-teal-600';
  };

  const totalAppts = hours.reduce((sum, h) => sum + h.count, 0);
  const busiestHour = hours.reduce((a, b) => (a.count > b.count ? a : b), hours[0]);

  return (
    <div>
      <div className="grid gap-1" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(40px, 1fr))' }}>
        {hours.map((h) => (
          <div
            key={h.hour}
            className={`flex flex-col items-center justify-center rounded-lg py-2 px-1 transition-all ${getColor(h.count)}`}
            title={`${h.label}: ${h.count} appointments`}
          >
            <span className="text-xs font-bold">{h.count}</span>
            <span className="text-[8px] font-medium mt-0.5">
              {h.hour > 12 ? `${h.hour - 12}P` : h.hour === 12 ? '12P' : `${h.hour}A`}
            </span>
          </div>
        ))}
      </div>
      {totalAppts > 0 && (
        <div className="mt-3 flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[10px] text-gray-400">
            <span className="inline-block h-2.5 w-2.5 rounded bg-gray-100" /> Low
            <span className="inline-block h-2.5 w-2.5 rounded bg-teal-200" />
            <span className="inline-block h-2.5 w-2.5 rounded bg-teal-400" />
            <span className="inline-block h-2.5 w-2.5 rounded bg-teal-600" /> High
          </div>
          <span className="text-[10px] font-semibold text-teal-600">
            Busiest: {busiestHour.label} ({busiestHour.count} appts)
          </span>
        </div>
      )}
    </div>
  );
}

function StatusDot({ status }) {
  const dotColors = {
    booked: 'bg-blue-400',
    'in-queue': 'bg-yellow-400',
    'in-consultation': 'bg-purple-400',
    completed: 'bg-green-400',
    cancelled: 'bg-red-400',
    'no-show': 'bg-orange-400',
  };
  return <span className={`inline-block h-2 w-2 rounded-full ${dotColors[status] || 'bg-gray-300'}`} />;
}

function SentimentBar({ positive, neutral, negative }) {
  const total = positive + neutral + negative;
  if (total === 0) return <p className="text-xs text-gray-400 italic">No feedback yet</p>;
  const pPct = Math.round((positive / total) * 100);
  const neuPct = Math.round((neutral / total) * 100);
  const nPct = 100 - pPct - neuPct;
  return (
    <div>
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-gray-100">
        {pPct > 0 && <div className="bg-green-400 transition-all" style={{ width: `${pPct}%` }} />}
        {neuPct > 0 && <div className="bg-gray-300 transition-all" style={{ width: `${neuPct}%` }} />}
        {nPct > 0 && <div className="bg-red-400 transition-all" style={{ width: `${nPct}%` }} />}
      </div>
      <div className="mt-1.5 flex gap-4 text-[10px]">
        <span className="flex items-center gap-1"><span className="inline-block h-2 w-2 rounded-full bg-green-400" /> Positive {pPct}%</span>
        <span className="flex items-center gap-1"><span className="inline-block h-2 w-2 rounded-full bg-gray-300" /> Neutral {neuPct}%</span>
        <span className="flex items-center gap-1"><span className="inline-block h-2 w-2 rounded-full bg-red-400" /> Negative {nPct}%</span>
      </div>
    </div>
  );
}

function AppointmentFlowRing({ completed, inQueue, booked, inConsultation, cancelled, noShow, total }) {
  if (total === 0) return <p className="text-xs text-gray-400 italic text-center">No appointments</p>;
  const segments = [
    { count: completed, color: '#4ade80', label: 'Completed' },
    { count: inConsultation, color: '#c084fc', label: 'With Doctor' },
    { count: inQueue, color: '#facc15', label: 'In Queue' },
    { count: booked, color: '#60a5fa', label: 'Booked' },
    { count: cancelled, color: '#f87171', label: 'Cancelled' },
    { count: noShow, color: '#fb923c', label: 'No Show' },
  ].filter((s) => s.count > 0);

  // Build a simple horizontal stacked bar instead of SVG ring for simplicity
  return (
    <div>
      <div className="flex h-4 w-full overflow-hidden rounded-full bg-gray-100">
        {segments.map((s, i) => (
          <div
            key={i}
            className="transition-all duration-500"
            style={{ width: `${(s.count / total) * 100}%`, backgroundColor: s.color }}
            title={`${s.label}: ${s.count}`}
          />
        ))}
      </div>
      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
        {segments.map((s, i) => (
          <span key={i} className="flex items-center gap-1 text-[10px] text-gray-500">
            <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: s.color }} />
            {s.label}: {s.count}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedDate, setSelectedDate] = useState(getLocalToday());

  useEffect(() => {
    loadStats(selectedDate);
  }, [selectedDate]);

  const loadStats = async (date) => {
    const res = await fetchAPI(`/api/dashboard/stats?date=${date}`);
    if (res.status === 'success') {
      setStats(res.data);
    }
    setLoading(false);
    setRefreshing(false);
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadStats(selectedDate);
  };

  const shiftDate = (days) => {
    const d = new Date(selectedDate);
    d.setDate(d.getDate() + days);
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    setSelectedDate(`${y}-${m}-${day}`);
  };

  const isToday = selectedDate === getLocalToday();

  if (loading) return <LoadingSpinner />;

  if (!stats) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-700">Welcome to CareDesk!</h2>
        <p className="mt-2 text-gray-500">Set up your clinic in Settings to get started.</p>
      </div>
    );
  }

  const s = stats;

  return (
    <div className="space-y-5">
      {/* Header with Date Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-400">
            {isToday ? "Today's overview" : `Overview for ${selectedDate}`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Date Navigation */}
          <div className="flex items-center gap-1 rounded-lg border border-gray-200 bg-white px-1 py-1">
            <button onClick={() => shiftDate(-1)} className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
              <ChevronLeft size={14} />
            </button>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="border-none bg-transparent px-1 text-sm font-medium text-gray-700 focus:outline-none"
            />
            <button onClick={() => shiftDate(1)} className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
              <ChevronRight size={14} />
            </button>
          </div>
          {!isToday && (
            <button onClick={() => setSelectedDate(getLocalToday())} className="rounded-lg border border-teal-200 bg-teal-50 px-3 py-2 text-xs font-medium text-teal-700 hover:bg-teal-100">
              Today
            </button>
          )}
          <button onClick={handleRefresh} disabled={refreshing} className="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-500 hover:bg-gray-50 disabled:opacity-50">
            <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} /> Refresh
          </button>
        </div>
      </div>

      {/* Row 1: Core Stats */}
      <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <MiniCard icon={CalendarDays} label="Total Appointments" value={s.total_appointments_today} color="blue" />
        <MiniCard icon={ListOrdered} label="In Queue" value={s.in_queue} sub={s.in_consultation > 0 ? `${s.in_consultation} with doctor` : undefined} color="yellow" />
        <MiniCard icon={CheckCircle} label="Completed" value={s.completed} sub={`${s.completion_rate}% rate`} color="green" />
        <MiniCard icon={Clock} label="Booked" value={s.booked} color="purple" />
      </div>

      {/* Row 2: Secondary Stats */}
      <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <MiniCard icon={Users} label="Total Patients" value={s.total_patients} color="teal" />
        <MiniCard icon={Stethoscope} label="Active Doctors" value={s.total_doctors} color="blue" />
        <MiniCard icon={Pill} label="Prescriptions" value={s.prescriptions_today} sub="today" color="purple" />
        <MiniCard
          icon={Star}
          label="Avg Rating"
          value={s.avg_feedback_score || '—'}
          sub={s.total_feedback_count > 0 ? `from ${s.total_feedback_count} reviews` : undefined}
          color="yellow"
        />
      </div>

      {/* Row 3: Alerts - No Shows & Cancellations */}
      {(s.no_show > 0 || s.cancelled > 0) && (
        <div className="grid gap-3 grid-cols-1 sm:grid-cols-2">
          {s.cancelled > 0 && (
            <div className="flex items-center gap-3 rounded-xl border border-red-100 bg-red-50 px-4 py-3">
              <XCircle size={18} className="text-red-500 shrink-0" />
              <div>
                <p className="text-sm font-semibold text-red-700">{s.cancelled} Cancelled</p>
                <p className="text-[10px] text-red-400">
                  {s.total_appointments_today > 0 ? `${Math.round((s.cancelled / s.total_appointments_today) * 100)}% cancellation rate` : ''}
                </p>
              </div>
            </div>
          )}
          {s.no_show > 0 && (
            <div className="flex items-center gap-3 rounded-xl border border-orange-100 bg-orange-50 px-4 py-3">
              <AlertTriangle size={18} className="text-orange-500 shrink-0" />
              <div>
                <p className="text-sm font-semibold text-orange-700">{s.no_show} No Shows</p>
                <p className="text-[10px] text-orange-400">
                  {s.total_appointments_today > 0 ? `${Math.round((s.no_show / s.total_appointments_today) * 100)}% no-show rate` : ''}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Row 4: Charts side by side */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Appointment Flow */}
        <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-700">
            <Activity size={15} className="text-teal-500" /> Appointment Flow
          </h3>
          <AppointmentFlowRing
            completed={s.completed}
            inQueue={s.in_queue}
            booked={s.booked}
            inConsultation={s.in_consultation}
            cancelled={s.cancelled}
            noShow={s.no_show}
            total={s.total_appointments_today}
          />
        </div>

        {/* Feedback Sentiment */}
        <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-700">
            <Star size={15} className="text-yellow-500" /> Feedback Sentiment
          </h3>
          <div className="mb-3 flex items-baseline gap-3">
            <span className="text-3xl font-bold text-gray-900">{s.avg_feedback_score || '—'}</span>
            <span className="text-xs text-gray-400">/ 5 avg rating</span>
          </div>
          <SentimentBar
            positive={s.sentiment_breakdown?.positive || 0}
            neutral={s.sentiment_breakdown?.neutral || 0}
            negative={s.sentiment_breakdown?.negative || 0}
          />
        </div>
      </div>

      {/* Row 5: Peak Hours Heatmap (full width) */}
      <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
        <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-700">
          <Clock size={15} className="text-blue-500" /> Hourly Distribution
        </h3>
        <HourlyHeatmap peakHours={s.peak_hours} />
      </div>

      {/* Row 6: Weekly Trend (full width) */}
      {s.weekly_trend && s.weekly_trend.length > 0 && (
        <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-700">
            <TrendingUp size={15} className="text-teal-500" /> Last 7 Days
          </h3>
          <WeeklyBarChart data={s.weekly_trend} />
        </div>
      )}

      {/* Row 7: Doctor Performance + Recent Activity */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Doctor Performance */}
        {s.doctor_performance && s.doctor_performance.length > 0 && (
          <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-700">
              <UserCheck size={15} className="text-blue-500" /> Doctor Performance
            </h3>
            <div className="space-y-2.5">
              {s.doctor_performance.map((doc) => {
                const pct = doc.total > 0 ? Math.round((doc.completed / doc.total) * 100) : 0;
                return (
                  <div key={doc.id} className="rounded-lg border border-gray-50 bg-gray-50 px-3 py-2.5">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-gray-800">Dr. {doc.name}</span>
                        {doc.in_consultation && (
                          <span className="rounded bg-purple-100 px-1.5 py-0.5 text-[9px] font-semibold text-purple-700">CONSULTING</span>
                        )}
                      </div>
                      <span className="text-xs text-gray-400">{doc.completed}/{doc.total} done</span>
                    </div>
                    <div className="flex h-1.5 w-full overflow-hidden rounded-full bg-gray-200">
                      <div className="rounded-full bg-teal-400 transition-all duration-500" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Recent Activity */}
        {s.recent_activity && s.recent_activity.length > 0 && (
          <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-700">
              <Activity size={15} className="text-green-500" /> Recent Activity
            </h3>
            <div className="space-y-1.5">
              {s.recent_activity.map((item) => (
                <div key={item.id} className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-gray-50">
                  <StatusDot status={item.status} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-800 truncate">
                      <span className="font-medium">{item.patient_name}</span>
                      {item.doctor_name && <span className="text-gray-400"> &middot; Dr. {item.doctor_name}</span>}
                    </p>
                    <p className="text-[10px] text-gray-400">
                      {item.token_number} &middot; {item.appointment_time}
                    </p>
                  </div>
                  <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold ${STATUS_COLORS[item.status] || 'bg-gray-100 text-gray-600'}`}>
                    {STATUS_LABELS[item.status] || item.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
