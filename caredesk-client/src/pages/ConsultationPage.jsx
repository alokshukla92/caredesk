import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchAPI } from '../api';
import { Plus, Trash2, FileText } from 'lucide-react';
import { useToast } from '../components/Toast';

export default function ConsultationPage() {
  const { appointmentId } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    diagnosis: '',
    medicines: [{ name: '', dosage: '', duration: '', instructions: '' }],
    advice: '',
    follow_up_date: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const toast = useToast();

  const addMedicine = () => {
    setForm({ ...form, medicines: [...form.medicines, { name: '', dosage: '', duration: '', instructions: '' }] });
  };

  const removeMedicine = (idx) => {
    setForm({ ...form, medicines: form.medicines.filter((_, i) => i !== idx) });
  };

  const updateMedicine = (idx, field, value) => {
    const updated = [...form.medicines];
    updated[idx][field] = value;
    setForm({ ...form, medicines: updated });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    const res = await fetchAPI('/api/prescriptions', {
      method: 'POST',
      body: JSON.stringify({ appointment_id: appointmentId, ...form }),
    });
    setSubmitting(false);
    if (res.status === 'success') {
      toast.success('Prescription created! Patient has been notified.');
      navigate('/appointments');
    } else {
      toast.error(res.message || 'Failed to create prescription');
    }
  };

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Write Prescription</h1>
        <p className="text-sm text-gray-500">Appointment #{appointmentId}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-700">
            <FileText size={16} /> Diagnosis
          </h3>
          <textarea
            required
            value={form.diagnosis}
            onChange={(e) => setForm({ ...form, diagnosis: e.target.value })}
            rows={3}
            placeholder="Enter diagnosis..."
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
          />
        </div>

        <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-700">Medicines</h3>
            <button type="button" onClick={addMedicine} className="flex items-center gap-1 rounded-lg bg-teal-50 px-3 py-1.5 text-xs font-medium text-teal-700 hover:bg-teal-100">
              <Plus size={14} /> Add Medicine
            </button>
          </div>
          <div className="space-y-3">
            {form.medicines.map((med, idx) => (
              <div key={idx} className="flex gap-2 rounded-lg bg-gray-50 p-3">
                <input placeholder="Medicine name" value={med.name} onChange={(e) => updateMedicine(idx, 'name', e.target.value)}
                  className="flex-1 rounded border border-gray-300 px-2 py-1.5 text-sm focus:border-teal-500 focus:outline-none" />
                <input placeholder="Dosage" value={med.dosage} onChange={(e) => updateMedicine(idx, 'dosage', e.target.value)}
                  className="w-24 rounded border border-gray-300 px-2 py-1.5 text-sm focus:border-teal-500 focus:outline-none" />
                <input placeholder="Duration" value={med.duration} onChange={(e) => updateMedicine(idx, 'duration', e.target.value)}
                  className="w-24 rounded border border-gray-300 px-2 py-1.5 text-sm focus:border-teal-500 focus:outline-none" />
                <input placeholder="Instructions" value={med.instructions} onChange={(e) => updateMedicine(idx, 'instructions', e.target.value)}
                  className="w-32 rounded border border-gray-300 px-2 py-1.5 text-sm focus:border-teal-500 focus:outline-none" />
                {form.medicines.length > 1 && (
                  <button type="button" onClick={() => removeMedicine(idx)} className="rounded p-1.5 text-red-400 hover:bg-red-50 hover:text-red-600">
                    <Trash2 size={14} />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-gray-700">Advice & Follow-up</h3>
          <textarea value={form.advice} onChange={(e) => setForm({ ...form, advice: e.target.value })} rows={2} placeholder="Doctor's advice..."
            className="mb-3 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Follow-up Date</label>
            <input type="date" value={form.follow_up_date} onChange={(e) => setForm({ ...form, follow_up_date: e.target.value })}
              className="w-48 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500" />
          </div>
        </div>

        <button type="submit" disabled={submitting}
          className="w-full rounded-lg bg-teal-600 py-3 text-sm font-medium text-white hover:bg-teal-700 disabled:opacity-50">
          {submitting ? 'Creating Prescription...' : 'Create Prescription & Complete'}
        </button>
      </form>
    </div>
  );
}
