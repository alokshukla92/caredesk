import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { fetchPublicAPI } from '../../api';
import { Activity, RefreshCw } from 'lucide-react';

export default function QueueDisplayPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQueue();
    const interval = setInterval(loadQueue, 10000); // Auto-refresh every 10 seconds
    return () => clearInterval(interval);
  }, [slug]);

  const loadQueue = async () => {
    const res = await fetchPublicAPI(`/api/public/queue/${slug}`);
    if (res.status === 'success') setData(res.data);
    setLoading(false);
  };

  if (loading || !data) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-900">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-teal-400 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="text-teal-400" size={32} />
          <div>
            <h1 className="text-2xl font-bold text-white">{data.clinic_name}</h1>
            <p className="text-sm text-gray-400">Live Queue — {data.date}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-gray-500">
          <RefreshCw size={14} className="animate-spin" />
          <span className="text-xs">Auto-refreshing</span>
        </div>
      </div>

      {/* Now Serving */}
      {data.now_serving.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-4 text-center text-sm font-semibold uppercase tracking-wider text-green-400">Now Serving</h2>
          <div className="flex flex-wrap justify-center gap-6">
            {data.now_serving.map((item, idx) => (
              <div key={idx} className="rounded-2xl border-2 border-green-500 bg-green-500/10 px-12 py-8 text-center">
                <p className="text-6xl font-black text-green-400">{item.token_number}</p>
                <p className="mt-2 text-lg text-white">Dr. {item.doctor_name}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Waiting */}
      {data.waiting.length > 0 && (
        <div>
          <h2 className="mb-4 text-center text-sm font-semibold uppercase tracking-wider text-yellow-400">
            Waiting ({data.total_waiting})
          </h2>
          <div className="flex flex-wrap justify-center gap-4">
            {data.waiting.map((item, idx) => (
              <div key={idx} className="rounded-xl border border-gray-700 bg-gray-800 px-8 py-5 text-center">
                <p className="text-3xl font-bold text-yellow-400">{item.token_number}</p>
                <p className="mt-1 text-xs text-gray-400">Dr. {item.doctor_name}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.now_serving.length === 0 && data.waiting.length === 0 && (
        <div className="flex min-h-[50vh] items-center justify-center">
          <p className="text-xl text-gray-500">No patients in queue</p>
        </div>
      )}
    </div>
  );
}
