import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import PublicLayout from './layouts/PublicLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import DoctorsPage from './pages/DoctorsPage';
import PatientsPage from './pages/PatientsPage';
import AppointmentsPage from './pages/AppointmentsPage';
import QueuePage from './pages/QueuePage';
import ConsultationPage from './pages/ConsultationPage';
import FeedbackPage from './pages/FeedbackPage';
import SettingsPage from './pages/SettingsPage';
import PatientDetailPage from './pages/PatientDetailPage';
import PrescriptionViewPage from './pages/PrescriptionViewPage';
import ClinicListPage from './pages/public/ClinicListPage';
import BookingPage from './pages/public/BookingPage';
import QueueDisplayPage from './pages/public/QueueDisplayPage';
import FeedbackFormPage from './pages/public/FeedbackFormPage';
import MyAppointmentsPage from './pages/public/MyAppointmentsPage';
import PublicPrescriptionPage from './pages/public/PublicPrescriptionPage';
import ProtectedRoute from './components/ProtectedRoute';
import { ToastProvider } from './components/Toast';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ToastProvider>
    <BrowserRouter basename={import.meta.env.BASE_URL.replace(/\/$/, '')}>
      <Routes>
        {/* Public routes with shared navbar */}
        <Route element={<PublicLayout />}>
          <Route path="/clinics" element={<ClinicListPage />} />
          <Route path="/book/:slug" element={<BookingPage />} />
          <Route path="/my-appointments" element={<MyAppointmentsPage />} />
          <Route path="/prescription/:prescriptionId" element={<PublicPrescriptionPage />} />
          <Route path="/feedback/:appointmentId" element={<FeedbackFormPage />} />
        </Route>

        {/* Standalone public routes (no navbar) */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/queue-display/:slug" element={<QueueDisplayPage />} />

        {/* Authenticated dashboard routes */}
        <Route path="/" element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="doctors" element={<DoctorsPage />} />
          <Route path="patients" element={<PatientsPage />} />
          <Route path="appointments" element={<AppointmentsPage />} />
          <Route path="queue" element={<QueuePage />} />
          <Route path="consultation/:appointmentId" element={<ConsultationPage />} />
          <Route path="patients/:patientId" element={<PatientDetailPage />} />
          <Route path="prescription/:prescriptionId" element={<PrescriptionViewPage />} />
          <Route path="feedback" element={<FeedbackPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        {/* Default redirect */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
    </ToastProvider>
  </React.StrictMode>
);
