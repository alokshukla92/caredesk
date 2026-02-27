import { useState, useEffect } from 'react';
import { fetchAPI } from '../api';
import StatsCard from '../components/StatsCard';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  CalendarDays, Users, ListOrdered, CheckCircle,
  Stethoscope, Star, Clock, TrendingUp,
} from 'lucide-react';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    const today = new Date().toISOString().split('T')[0];
    const res = await fetchAPI(`/api/dashboard/stats?date=${today}`);
    if (res.status === 'success') {
      setStats(res.data);
    }
    setLoading(false);
  };

  if (loading) return <LoadingSpinner />;

  if (!stats) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-700">Welcome to CareDesk!</h2>
        <p className="mt-2 text-gray-500">Set up your clinic in Settings to get started.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500">Today's overview — {stats.date}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard icon={CalendarDays} label="Appointments Today" value={stats.total_appointments_today} color="blue" />
        <StatsCard icon={ListOrdered} label="In Queue" value={stats.in_queue} color="yellow" />
        <StatsCard icon={CheckCircle} label="Completed" value={stats.completed} color="green" />
        <StatsCard icon={Clock} label="Booked" value={stats.booked} color="purple" />
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard icon={Users} label="Total Patients" value={stats.total_patients} color="teal" />
        <StatsCard icon={Stethoscope} label="Active Doctors" value={stats.total_doctors} color="blue" />
        <StatsCard icon={Star} label="Avg Rating" value={stats.avg_feedback_score || '—'} color="yellow" />
        <StatsCard icon={TrendingUp} label="Positive Feedback" value={stats.sentiment_breakdown?.positive || 0} color="green" />
      </div>

      {stats.sentiment_breakdown && (
        <div className="mt-6 rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-gray-700">Feedback Sentiment</h3>
          <div className="flex gap-6">
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-green-500" />
              <span className="text-sm text-gray-600">Positive: {stats.sentiment_breakdown.positive}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-gray-400" />
              <span className="text-sm text-gray-600">Neutral: {stats.sentiment_breakdown.neutral}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-red-500" />
              <span className="text-sm text-gray-600">Negative: {stats.sentiment_breakdown.negative}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
