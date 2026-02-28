import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, Menu, X, Building2, CalendarSearch } from 'lucide-react';

const NAV_ITEMS = [
  { to: '/clinics', label: 'Clinics', icon: Building2 },
  { to: '/my-appointments', label: 'My Appointments', icon: CalendarSearch },
];

export default function PublicNavbar() {
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();

  return (
    <nav className="sticky top-0 z-40 border-b border-gray-100 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-3">
        {/* Logo */}
        <Link to="/clinics" className="flex items-center gap-2">
          <Activity className="text-teal-600" size={24} />
          <span className="text-lg font-bold text-gray-900">CareDesk</span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden items-center gap-1 sm:flex">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition ${
                pathname === to || pathname.startsWith(to + '/')
                  ? 'bg-teal-50 text-teal-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Icon size={15} /> {label}
            </Link>
          ))}
        </div>

        {/* Mobile toggle */}
        <button
          onClick={() => setOpen(!open)}
          className="rounded-lg p-2 text-gray-600 hover:bg-gray-50 sm:hidden"
        >
          {open ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="border-t border-gray-100 bg-white px-4 pb-3 sm:hidden">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              onClick={() => setOpen(false)}
              className={`flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium ${
                pathname === to || pathname.startsWith(to + '/')
                  ? 'bg-teal-50 text-teal-700'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Icon size={16} /> {label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
}
