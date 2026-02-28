import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchAPI } from '../api';
import { Plus, Trash2, FileText, Pill, Sun, CloudSun, Moon } from 'lucide-react';
import { useToast } from '../components/Toast';

const EMPTY_MED = {
  name: '',
  dosage: '',
  morning: false,
  afternoon: false,
  night: false,
  when: '',
  duration: '',
  notes: '',
};

function FrequencyToggle({ label, icon: Icon, active, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex flex-col items-center gap-0.5 rounded-lg border px-3 py-1.5 text-[10px] font-semibold transition-colors ${
        active
          ? 'border-teal-500 bg-teal-50 text-teal-700'
          : 'border-gray-200 bg-white text-gray-400 hover:border-gray-300 hover:text-gray-500'
      }`}
    >
      <Icon size={14} />
      {label}
    </button>
  );
}

export default function ConsultationPage() {
  const { appointmentId } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    diagnosis: '',
    medicines: [{ ...EMPTY_MED }],
    advice: '',
    follow_up_date: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const toast = useToast();

  const addMedicine = () => {
    setForm({ ...form, medicines: [...form.medicines, { ...EMPTY_MED }] });
  };

  const removeMedicine = (idx) => {
    setForm({ ...form, medicines: form.medicines.filter((_, i) => i !== idx) });
  };

  const updateMedicine = (idx, field, value) => {
    const updated = [...form.medicines];
    updated[idx][field] = value;
    setForm({ ...form, medicines: updated });
  };

  const toggleFrequency = (idx, period) => {
    const updated = [...form.medicines];
    updated[idx][period] = !updated[idx][period];
    setForm({ ...form, medicines: updated });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Build the medicines payload — convert structured fields to display strings for backward compat
    const medicinesPayload = form.medicines.map((med) => {
      // Build frequency string like "1-0-1"
      const freq = [med.morning ? '1' : '0', med.afternoon ? '1' : '0', med.night ? '1' : '0'].join('-');
      const freqLabel = [med.morning && 'Morning', med.afternoon && 'Afternoon', med.night && 'Night'].filter(Boolean).join(', ');

      // Build timing label
      const whenLabel = med.when === 'before_meal' ? 'Before meal' : med.when === 'after_meal' ? 'After meal' : '';

      // Build instructions string from structured data
      const parts = [];
      if (freqLabel) parts.push(freqLabel);
      if (whenLabel) parts.push(whenLabel);
      if (med.notes) parts.push(med.notes);

      return {
        name: med.name,
        dosage: med.dosage,
        frequency: freq,
        frequency_label: freqLabel,
        morning: med.morning,
        afternoon: med.afternoon,
        night: med.night,
        when: med.when,
        duration: med.duration,
        notes: med.notes,
        // Backward compatible field
        instructions: parts.join(' | '),
      };
    });

    setSubmitting(true);
    const res = await fetchAPI('/api/prescriptions', {
      method: 'POST',
      body: JSON.stringify({
        appointment_id: appointmentId,
        diagnosis: form.diagnosis,
        medicines: medicinesPayload,
        advice: form.advice,
        follow_up_date: form.follow_up_date,
      }),
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
        {/* Diagnosis */}
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

        {/* Medicines */}
        <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-sm font-semibold text-gray-700">
              <Pill size={16} /> Medicines
            </h3>
            <button type="button" onClick={addMedicine} className="flex items-center gap-1 rounded-lg bg-teal-50 px-3 py-1.5 text-xs font-medium text-teal-700 hover:bg-teal-100">
              <Plus size={14} /> Add Medicine
            </button>
          </div>

          <div className="space-y-4">
            {form.medicines.map((med, idx) => (
              <div key={idx} className="rounded-xl border border-gray-100 bg-gray-50 p-4">
                {/* Row 1: Name + Dosage + Delete */}
                <div className="mb-3 flex gap-2">
                  <div className="flex-1">
                    <label className="mb-1 block text-[10px] font-semibold uppercase text-gray-400">Medicine Name</label>
                    <input
                      placeholder="e.g. Paracetamol"
                      value={med.name}
                      onChange={(e) => updateMedicine(idx, 'name', e.target.value)}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none"
                    />
                  </div>
                  <div className="w-28">
                    <label className="mb-1 block text-[10px] font-semibold uppercase text-gray-400">Dosage</label>
                    <input
                      placeholder="e.g. 500mg"
                      value={med.dosage}
                      onChange={(e) => updateMedicine(idx, 'dosage', e.target.value)}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none"
                    />
                  </div>
                  {form.medicines.length > 1 && (
                    <button type="button" onClick={() => removeMedicine(idx)} className="mt-5 rounded-lg p-2 text-red-400 hover:bg-red-50 hover:text-red-600">
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>

                {/* Row 2: Frequency + Timing + Duration */}
                <div className="mb-3 flex flex-wrap items-end gap-4">
                  {/* Frequency */}
                  <div>
                    <label className="mb-1.5 block text-[10px] font-semibold uppercase text-gray-400">Frequency</label>
                    <div className="flex gap-1.5">
                      <FrequencyToggle label="Morn" icon={Sun} active={med.morning} onClick={() => toggleFrequency(idx, 'morning')} />
                      <FrequencyToggle label="Aftn" icon={CloudSun} active={med.afternoon} onClick={() => toggleFrequency(idx, 'afternoon')} />
                      <FrequencyToggle label="Night" icon={Moon} active={med.night} onClick={() => toggleFrequency(idx, 'night')} />
                    </div>
                  </div>

                  {/* When / Timing */}
                  <div>
                    <label className="mb-1.5 block text-[10px] font-semibold uppercase text-gray-400">When</label>
                    <div className="flex gap-1.5">
                      {[
                        { value: 'before_meal', label: 'Before Meal' },
                        { value: 'after_meal', label: 'After Meal' },
                      ].map((opt) => (
                        <button
                          key={opt.value}
                          type="button"
                          onClick={() => updateMedicine(idx, 'when', med.when === opt.value ? '' : opt.value)}
                          className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors ${
                            med.when === opt.value
                              ? 'border-orange-400 bg-orange-50 text-orange-700'
                              : 'border-gray-200 bg-white text-gray-400 hover:border-gray-300 hover:text-gray-500'
                          }`}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Duration */}
                  <div>
                    <label className="mb-1.5 block text-[10px] font-semibold uppercase text-gray-400">Duration</label>
                    <input
                      placeholder="e.g. 5 days"
                      value={med.duration}
                      onChange={(e) => updateMedicine(idx, 'duration', e.target.value)}
                      className="w-28 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none"
                    />
                  </div>
                </div>

                {/* Row 3: Notes (optional) */}
                <div>
                  <label className="mb-1 block text-[10px] font-semibold uppercase text-gray-400">Special Instructions (optional)</label>
                  <input
                    placeholder="e.g. Take with warm water"
                    value={med.notes}
                    onChange={(e) => updateMedicine(idx, 'notes', e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Advice & Follow-up */}
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
