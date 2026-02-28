import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchAPI } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../components/Toast';
import { ArrowLeft, Printer, Download, FileText, Pill, Stethoscope, CalendarDays, Sun, CloudSun, Moon } from 'lucide-react';

function FreqDot({ active, icon: Icon, label }) {
  return (
    <span className={`inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[10px] font-semibold ${active ? 'bg-teal-100 text-teal-700' : 'bg-gray-100 text-gray-300'}`}>
      <Icon size={10} /> {label}
    </span>
  );
}

function MedicineFrequency({ med }) {
  // Check if new structured format exists
  if (med.morning !== undefined) {
    return (
      <div className="flex items-center gap-1">
        <FreqDot active={med.morning} icon={Sun} label="M" />
        <FreqDot active={med.afternoon} icon={CloudSun} label="A" />
        <FreqDot active={med.night} icon={Moon} label="N" />
      </div>
    );
  }
  // Fallback: old format — show instructions
  return <span className="text-gray-500 italic text-xs">{med.instructions || ''}</span>;
}

function TimingBadge({ when }) {
  if (!when) return null;
  const label = when === 'before_meal' ? 'Before meal' : when === 'after_meal' ? 'After meal' : when;
  return <span className="rounded bg-orange-50 px-1.5 py-0.5 text-[10px] font-medium text-orange-600">{label}</span>;
}

export default function PrescriptionViewPage() {
  const { prescriptionId } = useParams();
  const [rx, setRx] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const toast = useToast();

  useEffect(() => {
    fetchAPI(`/api/prescriptions/${prescriptionId}`).then((res) => {
      if (res.status === 'success') setRx(res.data);
      setLoading(false);
    });
  }, [prescriptionId]);

  const handleDownloadPDF = async () => {
    setDownloading(true);
    try {
      const res = await fetchAPI(`/api/prescriptions/${prescriptionId}/pdf`);
      if (res.status === 'success' && res.data?.download_url) {
        window.open(res.data.download_url, '_blank');
        toast.success('PDF download started');
      } else {
        toast.error(res.message || 'PDF generation failed. Use Print instead.');
      }
    } catch {
      toast.error('Failed to download PDF');
    }
    setDownloading(false);
  };

  if (loading) return <LoadingSpinner />;
  if (!rx) return <p className="text-center text-gray-500 py-12">Prescription not found.</p>;

  const medicines = Array.isArray(rx.medicines) ? rx.medicines : [];
  const rxDate = rx.created_time?.split('T')[0] || '';

  return (
    <div>
      {/* Action Bar */}
      <div className="mb-4 flex items-center justify-between print:hidden">
        <Link to={-1} className="inline-flex items-center gap-1 text-sm text-teal-600 hover:text-teal-700">
          <ArrowLeft size={14} /> Back
        </Link>
        <div className="flex items-center gap-2">
          <button
            onClick={handleDownloadPDF}
            disabled={downloading}
            className="flex items-center gap-2 rounded-lg border border-teal-200 bg-teal-50 px-4 py-2 text-sm font-medium text-teal-700 hover:bg-teal-100 disabled:opacity-50"
          >
            <Download size={14} /> {downloading ? 'Generating...' : 'Download PDF'}
          </button>
          <button onClick={() => window.print()} className="flex items-center gap-2 rounded-lg bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700">
            <Printer size={14} /> Print
          </button>
        </div>
      </div>

      {/* Prescription Card */}
      <div className="mx-auto max-w-2xl rounded-xl border border-gray-100 bg-white shadow-sm print:shadow-none print:border-none print:max-w-none">

        {/* Header */}
        <div className="border-b-[3px] border-teal-500 px-4 sm:px-6 pt-6 pb-4">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
            <div>
              <h1 className="text-xl font-bold text-teal-600">{rx.clinic_name || 'CareDesk Clinic'}</h1>
              <p className="text-xs text-gray-400 mt-0.5">Smart Clinic Management System</p>
              {rx.clinic_address && <p className="text-xs text-gray-500 mt-1">{rx.clinic_address}</p>}
              {rx.clinic_phone && <p className="text-xs text-gray-500">{rx.clinic_phone}</p>}
            </div>
            <div className="sm:text-right">
              <p className="font-semibold text-gray-900">Dr. {rx.doctor_name}</p>
              {rx.doctor_specialty && <p className="text-xs text-teal-600 font-medium">{rx.doctor_specialty}</p>}
              <p className="text-xs text-gray-500 mt-1">Date: {rxDate}</p>
              <p className="text-xs text-gray-400">Rx #{rx.id}</p>
            </div>
          </div>
        </div>

        {/* Patient Info Bar */}
        <div className="mx-4 sm:mx-6 mt-4 mb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 rounded-lg bg-teal-50 border border-teal-100 px-4 py-3">
          <div>
            <p className="text-[10px] uppercase tracking-wider text-gray-400 font-semibold">Patient</p>
            <p className="text-sm font-semibold text-gray-900">
              {rx.patient_name}
              {rx.patient_age && <span className="text-gray-500 font-normal"> &middot; {rx.patient_age} yrs</span>}
              {rx.patient_gender && <span className="text-gray-500 font-normal"> &middot; {rx.patient_gender}</span>}
            </p>
          </div>
          <div className="text-right">
            <p className="text-[10px] uppercase tracking-wider text-gray-400 font-semibold">Appointment Date</p>
            <p className="text-sm font-semibold text-gray-900">{rxDate}</p>
          </div>
        </div>

        <div className="px-4 sm:px-6 pb-6 space-y-5">
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
                        <div className="flex items-center gap-2">
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
        <div className="border-t border-gray-100 px-4 sm:px-6 py-4 flex flex-col sm:flex-row items-start sm:items-end justify-between gap-3">
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
  );
}
