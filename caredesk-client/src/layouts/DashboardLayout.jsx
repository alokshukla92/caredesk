import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { useState, useEffect } from 'react';
import { fetchAPI } from '../api';

export default function DashboardLayout() {
  const [clinicName, setClinicName] = useState('CareDesk');

  useEffect(() => {
    fetchAPI('/api/clinics/me').then((res) => {
      if (res.status === 'success' && res.data) {
        setClinicName(res.data.name);
      }
    });
  }, []);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header clinicName={clinicName} />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
