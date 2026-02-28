import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { fetchPublicAPI } from '../../api';
import { Star, CheckCircle } from 'lucide-react';
import { useToast } from '../../components/Toast';

export default function FeedbackFormPage() {
  const { appointmentId } = useParams();
  const [score, setScore] = useState(0);
  const [hoverScore, setHoverScore] = useState(0);
  const [feedbackText, setFeedbackText] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const toast = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!score) { toast.error('Please select a rating'); return; }
    setSubmitting(true);
    const res = await fetchPublicAPI(`/api/public/feedback/${appointmentId}`, {
      method: 'POST',
      body: JSON.stringify({ score, feedback_text: feedbackText }),
    });
    setSubmitting(false);
    if (res.status === 'success') {
      setSubmitted(true);
    } else {
      toast.error(res.message || 'Failed to submit feedback');
    }
  };

  if (submitted) {
    return (
      <div className="flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-lg">
          <CheckCircle className="mx-auto mb-4 text-green-500" size={48} />
          <h2 className="text-xl font-bold text-gray-900">Thank You!</h2>
          <p className="mt-2 text-gray-500">Your feedback has been submitted.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-xl font-bold text-gray-900">How was your visit?</h1>
          <p className="text-sm text-gray-500">Your feedback helps us improve</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6 rounded-2xl bg-white p-6 shadow-lg">
          <div className="text-center">
            <p className="mb-3 text-sm font-medium text-gray-700">Rate your experience</p>
            <div className="flex justify-center gap-2">
              {[1, 2, 3, 4, 5].map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setScore(s)}
                  onMouseEnter={() => setHoverScore(s)}
                  onMouseLeave={() => setHoverScore(0)}
                  className="p-1"
                >
                  <Star
                    size={36}
                    className={`transition-colors ${
                      s <= (hoverScore || score) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                    }`}
                  />
                </button>
              ))}
            </div>
            {score > 0 && (
              <p className="mt-1 text-sm text-gray-500">
                {score <= 2 ? 'We\'re sorry to hear that' : score <= 3 ? 'Thank you' : 'Glad you had a great experience!'}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Tell us more (optional)</label>
            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              rows={3}
              placeholder="Share your experience..."
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
            />
          </div>

          <button type="submit" disabled={submitting || !score}
            className="w-full rounded-lg bg-teal-600 py-3 text-sm font-medium text-white hover:bg-teal-700 disabled:opacity-50">
            {submitting ? 'Submitting...' : 'Submit Feedback'}
          </button>
        </form>
      </div>
    </div>
  );
}
