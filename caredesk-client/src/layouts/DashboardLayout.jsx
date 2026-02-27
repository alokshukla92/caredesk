import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { useState, useEffect } from 'react';
import { fetchAPI } from '../api';

export default function DashboardLayout() {
  const [clinicName, setClinicName] = useState('CareDesk');
  const [debugUserId, setDebugUserId] = useState(null);

  useEffect(() => {
    fetchAPI('/api/clinics/me').then((res) => {
      if (res.status === 'success' && res.data) {
        setClinicName(res.data.name);
        setDebugUserId(res.data._debug_user_id);
      } else {
        // No clinic — extract user_id from error message if available
        const msg = res.message || '';
        const match = msg.match(/user_id=(\d+)/);
        if (match) setDebugUserId(match[1]);
      }
    });
  }, []);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header clinicName={clinicName} debugUserId={debugUserId} />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
