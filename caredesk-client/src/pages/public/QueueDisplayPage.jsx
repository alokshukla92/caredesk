import { useState, useEffect, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { fetchPublicAPI } from '../../api';
import { Activity, RefreshCw, UserRound } from 'lucide-react';
import ConvoKraftBot from '../../components/ConvoKraftBot';

export default function QueueDisplayPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQueue();
    const interval = setInterval(loadQueue, 10000);
    return () => clearInterval(interval);
  }, [slug]);

  const loadQueue = async () => {
    const res = await fetchPublicAPI(`/api/public/queue/${slug}`);
    if (res.status === 'success') setData(res.data);
    setLoading(false);
  };

  // Group now_serving and waiting by doctor
  const doctorQueues = useMemo(() => {
    if (!data) return [];

    const map = {};

    // Add now_serving entries
    for (const item of (data.now_serving || [])) {
      const doc = item.doctor_name || 'Unknown';
      if (!map[doc]) map[doc] = { doctor: doc, serving: null, waiting: [] };
      map[doc].serving = item;
    }

    // Add waiting entries
    for (const item of (data.waiting || [])) {
      const doc = item.doctor_name || 'Unknown';
      if (!map[doc]) map[doc] = { doctor: doc, serving: null, waiting: [] };
      map[doc].waiting.push(item);
    }

    // Sort doctors alphabetically
    return Object.values(map).sort((a, b) => a.doctor.localeCompare(b.doctor));
  }, [data]);

  if (loading || !data) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-900">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-teal-400 border-t-transparent" />
      </div>
    );
  }

  const totalActive = (data.now_serving?.length || 0) + (data.waiting?.length || 0);

  return (
    <div className="min-h-screen bg-gray-900 p-4 sm:p-6">
      {/* Header */}
      <div className="mb-6 sm:mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Activity className="text-teal-400 shrink-0" size={28} />
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-white">{data.clinic_name}</h1>
            <p className="text-xs sm:text-sm text-gray-400">Live Queue — {data.date}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-gray-500">
          <RefreshCw size={14} className="animate-spin" />
          <span className="text-xs">Auto-refreshing</span>
        </div>
      </div>

      {/* Doctor-wise Queue Sections */}
      {doctorQueues.length > 0 ? (
        <div className="grid gap-4 sm:gap-8 md:grid-cols-2 lg:grid-cols-3">
          {doctorQueues.map((dq) => (
            <div key={dq.doctor} className="rounded-2xl border border-gray-700 bg-gray-800/50 p-4 sm:p-6">
              {/* Doctor Name */}
              <div className="mb-5 flex items-center gap-2 border-b border-gray-700 pb-3">
                <UserRound size={18} className="text-teal-400" />
                <h2 className="text-lg font-bold text-white">Dr. {dq.doctor}</h2>
              </div>

              {/* Now Serving */}
              {dq.serving ? (
                <div className="mb-5">
                  <p className="mb-2 text-center text-xs font-semibold uppercase tracking-wider text-green-400">Now Serving</p>
                  <div className="rounded-xl border-2 border-green-500 bg-green-500/10 py-6 text-center">
                    <p className="text-5xl font-black text-green-400">{dq.serving.token_number}</p>
                    {dq.serving.patient_name && (
                      <p className="mt-1 text-sm text-green-200">{dq.serving.patient_name}</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="mb-5">
                  <p className="mb-2 text-center text-xs font-semibold uppercase tracking-wider text-green-400">Now Serving</p>
                  <div className="rounded-xl border border-dashed border-gray-600 py-6 text-center">
                    <p className="text-sm text-gray-500">No patient with doctor</p>
                  </div>
                </div>
              )}

              {/* Waiting */}
              {dq.waiting.length > 0 ? (
                <div>
                  <p className="mb-2 text-center text-xs font-semibold uppercase tracking-wider text-yellow-400">
                    Waiting ({dq.waiting.length})
                  </p>
                  <div className="flex flex-wrap justify-center gap-3">
                    {dq.waiting.map((item, idx) => (
                      <div key={idx} className="rounded-lg border border-gray-600 bg-gray-700/50 px-5 py-3 text-center">
                        <p className="text-xl font-bold text-yellow-400">{item.token_number}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div>
                  <p className="mb-2 text-center text-xs font-semibold uppercase tracking-wider text-yellow-400">Waiting</p>
                  <p className="text-center text-xs text-gray-500">No patients waiting</p>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="flex min-h-[50vh] items-center justify-center">
          <p className="text-xl text-gray-500">No patients in queue</p>
        </div>
      )}
      <ConvoKraftBot />
    </div>
  );
}
