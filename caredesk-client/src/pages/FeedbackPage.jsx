import { useState, useEffect } from 'react';
import { fetchAPI } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';
import { MessageSquare, Star, ThumbsUp, ThumbsDown, Minus } from 'lucide-react';
import { SENTIMENT_COLORS } from '../utils/constants';

export default function FeedbackPage() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadFeedback(); }, []);

  const loadFeedback = async () => {
    const res = await fetchAPI('/api/appointments');
    if (res.status === 'success') {
      setAppointments(res.data.filter((a) => a.feedback_score));
    }
    setLoading(false);
  };

  if (loading) return <LoadingSpinner />;

  const SentimentIcon = ({ sentiment }) => {
    if (sentiment === 'positive') return <ThumbsUp size={14} className="text-green-600" />;
    if (sentiment === 'negative') return <ThumbsDown size={14} className="text-red-600" />;
    return <Minus size={14} className="text-gray-400" />;
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Patient Feedback</h1>
        <p className="text-sm text-gray-500">{appointments.length} feedback(s) received</p>
      </div>

      {appointments.length === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-gray-200 p-12 text-center">
          <MessageSquare className="mx-auto mb-3 text-gray-300" size={40} />
          <p className="text-gray-500">No feedback yet.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {appointments.map((a) => (
            <div key={a.id} className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-gray-900">{a.patient_name}</p>
                  <p className="text-xs text-gray-500">Dr. {a.doctor_name} — {a.appointment_date}</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <Star size={14} className="text-yellow-500" />
                    <span className="text-sm font-semibold">{a.feedback_score}/5</span>
                  </div>
                  {a.feedback_sentiment && (
                    <div className={`flex items-center gap-1 ${SENTIMENT_COLORS[a.feedback_sentiment] || ''}`}>
                      <SentimentIcon sentiment={a.feedback_sentiment} />
                      <span className="text-xs font-medium capitalize">{a.feedback_sentiment}</span>
                    </div>
                  )}
                </div>
              </div>
              {a.feedback_text && (
                <p className="mt-2 text-sm text-gray-600 italic">"{a.feedback_text}"</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
