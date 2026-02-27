import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Stethoscope, Users, CalendarDays,
  ListOrdered, MessageSquare, Settings, LogOut, Activity,
} from 'lucide-react';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/doctors', icon: Stethoscope, label: 'Doctors' },
  { to: '/patients', icon: Users, label: 'Patients' },
  { to: '/appointments', icon: CalendarDays, label: 'Appointments' },
  { to: '/queue', icon: ListOrdered, label: 'Live Queue' },
  { to: '/feedback', icon: MessageSquare, label: 'Feedback' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export default function Sidebar() {
  const handleLogout = () => {
    if (window.catalyst?.auth) {
      window.catalyst.auth.signOut('/__catalyst/auth/login');
    } else {
      window.location.href = '/login';
    }
  };

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-gray-200 bg-white">
      <div className="flex items-center gap-2 border-b border-gray-200 px-5 py-4">
        <Activity className="text-teal-600" size={24} />
        <span className="text-xl font-bold text-gray-900">CareDesk</span>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-teal-50 text-teal-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-gray-200 px-3 py-3">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-600 hover:bg-red-50 hover:text-red-600"
        >
          <LogOut size={18} />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
