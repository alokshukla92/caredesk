import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { fetchPublicAPI } from '../../api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { Printer, Stethoscope, Pill, FileText, CalendarDays, Sun, CloudSun, Moon } from 'lucide-react';

function FreqDot({ active, icon: Icon, label }) {
  return (
    <span className={`inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[10px] font-semibold ${active ? 'bg-teal-100 text-teal-700' : 'bg-gray-100 text-gray-300'}`}>
      <Icon size={10} /> {label}
    </span>
  );
}

function MedicineFrequency({ med }) {
  if (med.morning !== undefined) {
    return (
      <div className="flex items-center gap-1">
        <FreqDot active={med.morning} icon={Sun} label="M" />
        <FreqDot active={med.afternoon} icon={CloudSun} label="A" />
        <FreqDot active={med.night} icon={Moon} label="N" />
      </div>
    );
  }
  return <span className="text-gray-500 italic text-xs">{med.instructions || ''}</span>;
}

function TimingBadge({ when }) {
  if (!when) return null;
  const label = when === 'before_meal' ? 'Before meal' : when === 'after_meal' ? 'After meal' : when;
  return <span className="rounded bg-orange-50 px-1.5 py-0.5 text-[10px] font-medium text-orange-600">{label}</span>;
}

export default function PublicPrescriptionPage() {
  const { prescriptionId } = useParams();
  const [rx, setRx] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPublicAPI(`/api/public/prescription/${prescriptionId}`).then((res) => {
      if (res.status === 'success') setRx(res.data);
      setLoading(false);
    });
  }, [prescriptionId]);

  if (loading) return <LoadingSpinner />;

  if (!rx) {
    return (
      <div className="flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-lg">
          <FileText className="mx-auto mb-3 text-gray-300" size={40} />
          <h2 className="text-lg font-bold text-gray-700">Prescription Not Found</h2>
          <p className="mt-1 text-sm text-gray-400">The prescription may have been removed or the link is invalid.</p>
        </div>
      </div>
    );
  }

  const medicines = Array.isArray(rx.medicines) ? rx.medicines : [];
  const rxDate = rx.created_time?.split('T')[0] || '';

  return (
    <div className="px-4 py-6">
      <div className="mx-auto max-w-2xl">
        {/* Print Button */}
        <div className="mb-4 flex justify-end print:hidden">
          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 rounded-xl bg-teal-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-teal-700"
          >
            <Printer size={14} /> Print / Save PDF
          </button>
        </div>

        {/* Prescription Card */}
        <div className="rounded-2xl bg-white shadow-sm print:shadow-none print:rounded-none">
          {/* Header */}
          <div className="border-b-[3px] border-teal-500 px-6 pt-6 pb-4">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-xl font-bold text-teal-600">{rx.clinic_name || 'CareDesk Clinic'}</h1>
                <p className="text-xs text-gray-400 mt-0.5">Smart Clinic Management System</p>
                {rx.clinic_address && <p className="text-xs text-gray-500 mt-1">{rx.clinic_address}</p>}
                {rx.clinic_phone && <p className="text-xs text-gray-500">{rx.clinic_phone}</p>}
              </div>
              <div className="text-right">
                <p className="font-semibold text-gray-900">Dr. {rx.doctor_name}</p>
                {rx.doctor_specialty && <p className="text-xs text-teal-600 font-medium">{rx.doctor_specialty}</p>}
                <p className="text-xs text-gray-500 mt-1">Date: {rxDate}</p>
                <p className="text-xs text-gray-400">Rx #{rx.id}</p>
              </div>
            </div>
          </div>

          {/* Patient Info Bar */}
          <div className="mx-6 mt-4 mb-5 flex items-center justify-between rounded-lg bg-teal-50 border border-teal-100 px-4 py-3">
            <div>
              <p className="text-[10px] uppercase tracking-wider text-gray-400 font-semibold">Patient</p>
              <p className="text-sm font-semibold text-gray-900">
                {rx.patient_name}
                {rx.patient_age && <span className="text-gray-500 font-normal"> &middot; {rx.patient_age} yrs</span>}
                {rx.patient_gender && <span className="text-gray-500 font-normal"> &middot; {rx.patient_gender}</span>}
              </p>
            </div>
            <div className="text-right">
              <p className="text-[10px] uppercase tracking-wider text-gray-400 font-semibold">Date</p>
              <p className="text-sm font-semibold text-gray-900">{rxDate}</p>
            </div>
          </div>

          <div className="px-6 pb-6 space-y-5">
            {/* Diagnosis */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Stethoscope size={14} className="text-teal-500" />
                <h3 className="text-[10px] uppercase tracking-wider text-gray-400 font-bold">Diagnosis</h3>
              </div>
              <p className="text-sm text-gray-800 leading-relaxed pl-[22px]">{rx.diagnosis}</p>
            </div>

            {/* Medicines */}
            {medicines.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Pill size={14} className="text-teal-500" />
                  <h3 className="text-[10px] uppercase tracking-wider text-gray-400 font-bold">Prescribed Medicines</h3>
                </div>
                <div className="space-y-2">
                  {medicines.map((m, i) => (
                    <div key={i} className={`rounded-lg border p-3 ${i % 2 === 1 ? 'bg-gray-50 border-gray-100' : 'bg-white border-gray-100'}`}>
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-xs font-bold text-gray-300">{i + 1}.</span>
                            <span className="font-semibold text-gray-900 text-sm">{m.name}</span>
                            {m.dosage && <span className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] font-medium text-blue-600">{m.dosage}</span>}
                            <TimingBadge when={m.when} />
                          </div>
                          <div className="mt-1.5 flex items-center gap-3">
                            <MedicineFrequency med={m} />
                            {m.duration && <span className="text-xs text-gray-500">for {m.duration}</span>}
                          </div>
                          {m.notes && <p className="mt-1 text-xs text-gray-400 italic">{m.notes}</p>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Advice */}
            {rx.advice && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <FileText size={14} className="text-teal-500" />
                  <h3 className="text-[10px] uppercase tracking-wider text-gray-400 font-bold">Advice</h3>
                </div>
                <p className="text-sm text-gray-700 leading-relaxed pl-[22px]">{rx.advice}</p>
              </div>
            )}

            {/* Follow-up */}
            {rx.follow_up_date && (
              <div className="flex items-center gap-2 rounded-lg bg-orange-50 border border-orange-200 px-4 py-3">
                <CalendarDays size={16} className="text-orange-500" />
                <span className="text-sm font-semibold text-orange-700">Follow-up: {rx.follow_up_date}</span>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-gray-100 px-6 py-4 flex items-end justify-between">
            <p className="text-[9px] text-gray-300 leading-relaxed">
              Generated by CareDesk — Smart Clinic Management System<br />
              This is a digitally generated prescription.
            </p>
            <div className="text-right">
              <div className="border-t border-gray-300 w-36 mb-1 ml-auto" />
              <p className="text-xs text-gray-500 font-semibold">Dr. {rx.doctor_name}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
