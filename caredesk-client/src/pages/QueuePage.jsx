import { useState, useEffect } from 'react';
import { fetchAPI } from '../api';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { RefreshCw, ListOrdered } from 'lucide-react';
import { useToast } from '../components/Toast';

export default function QueuePage() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => { loadQueue(); }, []);

  const loadQueue = async () => {
    setLoading(true);
    const res = await fetchAPI('/api/appointments/queue');
    if (res.status === 'success') setQueue(res.data);
    setLoading(false);
  };

  const updateStatus = async (id, status) => {
    const res = await fetchAPI(`/api/appointments/${id}`, { method: 'PUT', body: JSON.stringify({ status }) });
    if (res.status === 'error') {
      toast.error(res.message || 'Failed to update status');
      return;
    }
    toast.success(status === 'in-consultation' ? 'Patient called in' : 'Status updated');
    loadQueue();
  };

  if (loading) return <LoadingSpinner />;

  const inConsultation = queue.filter((q) => q.status === 'in-consultation');
  const waiting = queue.filter((q) => q.status === 'in-queue');

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Live Queue</h1>
          <p className="text-sm text-gray-500">{waiting.length} waiting, {inConsultation.length} with doctor</p>
        </div>
        <button onClick={loadQueue} className="flex items-center gap-2 rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {inConsultation.length > 0 && (
        <div className="mb-6">
          <h2 className="mb-3 text-sm font-semibold uppercase text-purple-600">Now Serving</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {inConsultation.map((item) => (
              <div key={item.id} className="rounded-xl border-2 border-purple-200 bg-purple-50 p-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-2xl font-bold text-purple-700">{item.token_number}</span>
                  <StatusBadge status={item.status} />
                </div>
                <p className="font-medium text-gray-900">{item.patient_name}</p>
                <p className="text-sm text-gray-500">Dr. {item.doctor_name}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {waiting.length > 0 ? (
        <div>
          <h2 className="mb-3 text-sm font-semibold uppercase text-yellow-600">Waiting ({waiting.length})</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {waiting.map((item, idx) => (
              <div key={item.id} className="rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-2xl font-bold text-teal-600">{item.token_number}</span>
                  <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">#{idx + 1}</span>
                </div>
                <p className="font-medium text-gray-900">{item.patient_name}</p>
                <p className="mb-3 text-sm text-gray-500">Dr. {item.doctor_name}</p>
                <button
                  onClick={() => updateStatus(item.id, 'in-consultation')}
                  className="w-full rounded-lg bg-purple-600 py-2 text-xs font-medium text-white hover:bg-purple-700"
                >
                  Call Patient
                </button>
              </div>
            ))}
          </div>
        </div>
      ) : (
        !inConsultation.length && (
          <div className="rounded-xl border-2 border-dashed border-gray-200 p-12 text-center">
            <ListOrdered className="mx-auto mb-3 text-gray-300" size={40} />
            <p className="text-gray-500">No patients in queue right now.</p>
          </div>
        )
      )}
    </div>
  );
}
