import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchAPI } from '../api';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { ArrowLeft, User, Phone, Mail, Calendar, FileText } from 'lucide-react';

export default function PatientDetailPage() {
  const { patientId } = useParams();
  const [patient, setPatient] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [prescriptions, setPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('appointments');

  useEffect(() => { loadAll(); }, [patientId]);

  const loadAll = async () => {
    const [patRes, apptRes, rxRes] = await Promise.all([
      fetchAPI(`/api/patients/${patientId}`),
      fetchAPI(`/api/appointments/patient/${patientId}`),
      fetchAPI(`/api/prescriptions/patient/${patientId}`),
    ]);
    if (patRes.status === 'success') setPatient(patRes.data);
    if (apptRes.status === 'success') setAppointments(apptRes.data);
    if (rxRes.status === 'success') setPrescriptions(rxRes.data);
    setLoading(false);
  };

  if (loading) return <LoadingSpinner />;
  if (!patient) return <p className="text-center text-gray-500 py-12">Patient not found.</p>;

  return (
    <div>
      {/* Back link */}
      <Link to="/patients" className="mb-4 inline-flex items-center gap-1 text-sm text-teal-600 hover:text-teal-700">
        <ArrowLeft size={14} /> Back to Patients
      </Link>

      {/* Patient info card */}
      <div className="mb-6 rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-teal-50 text-teal-600">
            <User size={28} />
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-gray-900">{patient.name}</h1>
            <div className="mt-1 flex flex-wrap gap-4 text-sm text-gray-500">
              {patient.phone && <span className="flex items-center gap-1"><Phone size={13} /> {patient.phone}</span>}
              {patient.email && <span className="flex items-center gap-1"><Mail size={13} /> {patient.email}</span>}
              {patient.age && <span>Age: {patient.age}</span>}
              {patient.gender && <span>{patient.gender}</span>}
              {patient.blood_group && <span>Blood: {patient.blood_group}</span>}
            </div>
            {patient.medical_history && (
              <p className="mt-2 text-sm text-gray-600"><strong>Medical History:</strong> {patient.medical_history}</p>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-4 flex gap-1 rounded-lg bg-gray-100 p-1">
        <button
          onClick={() => setTab('appointments')}
          className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition ${tab === 'appointments' ? 'bg-white text-teal-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
        >
          <Calendar size={14} className="mr-1 inline" /> Appointments ({appointments.length})
        </button>
        <button
          onClick={() => setTab('prescriptions')}
          className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition ${tab === 'prescriptions' ? 'bg-white text-teal-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
        >
          <FileText size={14} className="mr-1 inline" /> Prescriptions ({prescriptions.length})
        </button>
      </div>

      {/* Appointments tab */}
      {tab === 'appointments' && (
        appointments.length === 0 ? (
          <div className="rounded-xl border-2 border-dashed border-gray-200 p-8 text-center">
            <p className="text-gray-500">No appointments found for this patient.</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-gray-100 bg-white shadow-sm">
            <table className="w-full min-w-[600px] text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Date</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Time</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Doctor</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Token</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Status</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {appointments.map((a) => (
                  <tr key={a.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{a.appointment_date}</td>
                    <td className="px-4 py-3 text-gray-600">{a.appointment_time || '—'}</td>
                    <td className="px-4 py-3 text-gray-600">Dr. {a.doctor_name}</td>
                    <td className="px-4 py-3 font-bold text-teal-600">{a.token_number}</td>
                    <td className="px-4 py-3"><StatusBadge status={a.status} /></td>
                    <td className="px-4 py-3 text-gray-600">
                      {a.feedback_score ? `${a.feedback_score}/5` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {/* Prescriptions tab */}
      {tab === 'prescriptions' && (
        prescriptions.length === 0 ? (
          <div className="rounded-xl border-2 border-dashed border-gray-200 p-8 text-center">
            <p className="text-gray-500">No prescriptions found for this patient.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {prescriptions.map((rx) => (
              <div key={rx.id} className="rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{rx.diagnosis}</p>
                    <p className="text-sm text-gray-500">Dr. {rx.doctor_name} &middot; {rx.appointment_date || rx.created_at || ''}</p>
                  </div>
                  <Link
                    to={`/prescription/${rx.id}`}
                    className="rounded bg-teal-50 px-3 py-1 text-xs font-medium text-teal-700 hover:bg-teal-100"
                  >
                    View Rx
                  </Link>
                </div>
                {rx.advice && <p className="mt-2 text-sm text-gray-600">{rx.advice}</p>}
                {rx.follow_up_date && (
                  <p className="mt-1 text-xs text-orange-600">Follow-up: {rx.follow_up_date}</p>
                )}
              </div>
            ))}
          </div>
        )
      )}
    </div>
  );
}
