import { useState, useEffect, useMemo } from 'react';
import { fetchAPI } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';
import { MessageSquare, Star, ThumbsUp, ThumbsDown, Minus, RefreshCw, BarChart3, Brain, Filter, X, Tag } from 'lucide-react';

const SentimentIcon = ({ sentiment, size = 14 }) => {
  if (sentiment === 'positive') return <ThumbsUp size={size} className="text-green-600" />;
  if (sentiment === 'negative') return <ThumbsDown size={size} className="text-red-600" />;
  return <Minus size={size} className="text-gray-400" />;
};

const StarRating = ({ score }) => {
  const num = Number(score) || 0;
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star
          key={i}
          size={16}
          className={i <= num ? 'fill-yellow-400 text-yellow-400' : 'text-gray-200'}
        />
      ))}
    </div>
  );
};

const SentimentBadge = ({ sentiment }) => {
  const config = {
    positive: { bg: 'bg-green-50 border-green-200', text: 'text-green-700', label: 'Positive' },
    negative: { bg: 'bg-red-50 border-red-200', text: 'text-red-700', label: 'Negative' },
    neutral: { bg: 'bg-gray-50 border-gray-200', text: 'text-gray-600', label: 'Neutral' },
  };
  const c = config[sentiment] || config.neutral;
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-medium ${c.bg} ${c.text}`}>
      <SentimentIcon sentiment={sentiment} size={12} />
      {c.label}
    </span>
  );
};

const KeywordTags = ({ keywords }) => {
  if (!keywords || keywords.length === 0) return null;
  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {keywords.map((kw, i) => (
        <span key={i} className="inline-flex items-center gap-1 rounded-full bg-teal-50 border border-teal-200 px-2 py-0.5 text-xs text-teal-700">
          <Tag size={10} />
          {kw}
        </span>
      ))}
    </div>
  );
};

export default function FeedbackPage() {
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Filters
  const [filterDoctor, setFilterDoctor] = useState('');
  const [filterSentiment, setFilterSentiment] = useState('');
  const [filterDateFrom, setFilterDateFrom] = useState('');
  const [filterDateTo, setFilterDateTo] = useState('');

  useEffect(() => { loadFeedback(); }, []);

  const loadFeedback = async () => {
    const res = await fetchAPI('/api/appointments/feedback');
    if (res.status === 'success') {
      setFeedbacks(res.data);
    }
    setLoading(false);
    setRefreshing(false);
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadFeedback();
  };

  const clearFilters = () => {
    setFilterDoctor('');
    setFilterSentiment('');
    setFilterDateFrom('');
    setFilterDateTo('');
  };

  // Unique doctors for dropdown
  const doctors = useMemo(() => {
    const map = new Map();
    feedbacks.forEach((f) => {
      if (f.doctor_id && f.doctor_name && !map.has(f.doctor_id)) {
        map.set(f.doctor_id, f.doctor_name);
      }
    });
    return Array.from(map, ([id, name]) => ({ id, name })).sort((a, b) => a.name.localeCompare(b.name));
  }, [feedbacks]);

  // Filtered feedbacks
  const filtered = useMemo(() => {
    return feedbacks.filter((f) => {
      if (filterDoctor && f.doctor_id !== filterDoctor) return false;
      if (filterSentiment && (f.feedback_sentiment || 'neutral') !== filterSentiment) return false;
      if (filterDateFrom && f.appointment_date < filterDateFrom) return false;
      if (filterDateTo && f.appointment_date > filterDateTo) return false;
      return true;
    });
  }, [feedbacks, filterDoctor, filterSentiment, filterDateFrom, filterDateTo]);

  const hasActiveFilters = filterDoctor || filterSentiment || filterDateFrom || filterDateTo;

  if (loading) return <LoadingSpinner />;

  // Compute summary stats from filtered data
  const totalFeedback = filtered.length;
  const scores = filtered.map((f) => Number(f.feedback_score) || 0);
  const avgScore = totalFeedback > 0 ? (scores.reduce((a, b) => a + b, 0) / totalFeedback).toFixed(1) : '0';
  const sentimentCounts = { positive: 0, negative: 0, neutral: 0 };
  filtered.forEach((f) => {
    const s = f.feedback_sentiment || 'neutral';
    if (sentimentCounts[s] !== undefined) sentimentCounts[s]++;
  });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Patient Feedback</h1>
          <p className="text-sm text-gray-500">
            {totalFeedback} feedback(s){hasActiveFilters ? ' (filtered)' : ''} — {feedbacks.length} total
          </p>
        </div>
        <button onClick={handleRefresh} disabled={refreshing} className="flex items-center gap-2 rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50">
          <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="mb-6 rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase text-gray-400">
            <Filter size={13} /> Filters
          </div>
          {hasActiveFilters && (
            <button onClick={clearFilters} className="flex items-center gap-1 text-xs text-teal-600 hover:text-teal-800">
              <X size={12} /> Clear all
            </button>
          )}
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {/* Doctor Filter */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500">Doctor</label>
            <select
              value={filterDoctor}
              onChange={(e) => setFilterDoctor(e.target.value)}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:border-teal-400 focus:outline-none focus:ring-1 focus:ring-teal-400"
            >
              <option value="">All Doctors</option>
              {doctors.map((d) => (
                <option key={d.id} value={d.id}>Dr. {d.name}</option>
              ))}
            </select>
          </div>

          {/* Sentiment Filter */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500">Sentiment</label>
            <select
              value={filterSentiment}
              onChange={(e) => setFilterSentiment(e.target.value)}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:border-teal-400 focus:outline-none focus:ring-1 focus:ring-teal-400"
            >
              <option value="">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>
          </div>

          {/* Date From */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500">From Date</label>
            <input
              type="date"
              value={filterDateFrom}
              onChange={(e) => setFilterDateFrom(e.target.value)}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:border-teal-400 focus:outline-none focus:ring-1 focus:ring-teal-400"
            />
          </div>

          {/* Date To */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500">To Date</label>
            <input
              type="date"
              value={filterDateTo}
              onChange={(e) => setFilterDateTo(e.target.value)}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:border-teal-400 focus:outline-none focus:ring-1 focus:ring-teal-400"
            />
          </div>
        </div>
      </div>

      {totalFeedback === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-gray-200 p-12 text-center">
          <MessageSquare className="mx-auto mb-3 text-gray-300" size={40} />
          {hasActiveFilters ? (
            <>
              <p className="text-gray-500">No feedback matches your filters.</p>
              <button onClick={clearFilters} className="mt-2 text-sm text-teal-600 hover:text-teal-800 underline">Clear filters</button>
            </>
          ) : (
            <>
              <p className="text-gray-500">No feedback yet.</p>
              <p className="mt-1 text-xs text-gray-400">Feedback will appear here after patients rate their completed appointments.</p>
            </>
          )}
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="mb-6 grid gap-4 sm:grid-cols-3">
            {/* Average Rating */}
            <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
              <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase text-gray-400">
                <Star size={13} /> Average Rating
              </div>
              <div className="flex items-end gap-2">
                <span className="text-3xl font-bold text-gray-900">{avgScore}</span>
                <span className="mb-1 text-sm text-gray-400">/ 5</span>
              </div>
              <div className="mt-1"><StarRating score={Math.round(avgScore)} /></div>
            </div>

            {/* Zia Sentiment Breakdown */}
            <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
              <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase text-gray-400">
                <Brain size={13} /> Zia Sentiment Analysis
              </div>
              <div className="space-y-2">
                {[
                  { key: 'positive', color: 'bg-green-500', label: 'Positive' },
                  { key: 'neutral', color: 'bg-gray-400', label: 'Neutral' },
                  { key: 'negative', color: 'bg-red-500', label: 'Negative' },
                ].map(({ key, color, label }) => {
                  const pct = totalFeedback > 0 ? Math.round((sentimentCounts[key] / totalFeedback) * 100) : 0;
                  return (
                    <div key={key} className="flex items-center gap-2">
                      <span className="w-16 text-xs text-gray-500">{label}</span>
                      <div className="flex-1 rounded-full bg-gray-100 h-2">
                        <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
                      </div>
                      <span className="w-12 text-right text-xs font-medium text-gray-600">{sentimentCounts[key]} ({pct}%)</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Score Distribution */}
            <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
              <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase text-gray-400">
                <BarChart3 size={13} /> Score Distribution
              </div>
              <div className="space-y-1.5">
                {[5, 4, 3, 2, 1].map((s) => {
                  const count = scores.filter((sc) => sc === s).length;
                  const pct = totalFeedback > 0 ? Math.round((count / totalFeedback) * 100) : 0;
                  return (
                    <div key={s} className="flex items-center gap-2">
                      <span className="flex items-center gap-0.5 w-8 text-xs text-gray-500">{s} <Star size={10} className="fill-yellow-400 text-yellow-400" /></span>
                      <div className="flex-1 rounded-full bg-gray-100 h-2">
                        <div className="h-2 rounded-full bg-yellow-400" style={{ width: `${pct}%` }} />
                      </div>
                      <span className="w-6 text-right text-xs text-gray-500">{count}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Feedback List */}
          <div className="space-y-3">
            {filtered.map((a) => (
              <div key={a.id} className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-gray-900">{a.patient_name}</p>
                      <SentimentBadge sentiment={a.feedback_sentiment} />
                    </div>
                    <p className="mt-0.5 text-xs text-gray-500">
                      Dr. {a.doctor_name} &middot; {a.appointment_date} {a.appointment_time && `at ${a.appointment_time}`} &middot; Token: {a.token_number}
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <StarRating score={a.feedback_score} />
                    <span className="text-xs font-medium text-gray-500">{a.feedback_score}/5</span>
                  </div>
                </div>

                {/* Feedback Text */}
                {a.feedback_text ? (
                  <div className="mt-3 rounded-lg bg-gray-50 p-3">
                    <p className="text-sm text-gray-700 leading-relaxed">&ldquo;{a.feedback_text}&rdquo;</p>
                  </div>
                ) : (
                  <p className="mt-3 text-xs italic text-gray-400">No written feedback — rating only.</p>
                )}

                {/* Zia Keywords */}
                <KeywordTags keywords={a.feedback_keywords} />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
