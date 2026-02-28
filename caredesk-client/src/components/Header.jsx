import { Menu } from 'lucide-react';

export default function Header({ clinicName = 'CareDesk', debugUserId, onMenuClick }) {
  return (
    <header className="flex items-center justify-between border-b border-gray-200 bg-white px-4 py-3 sm:px-6">
      <div className="flex items-center gap-3">
        <button onClick={onMenuClick} className="rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 md:hidden">
          <Menu size={20} />
        </button>
        <div>
          <h1 className="text-base font-semibold text-gray-900 sm:text-lg">{clinicName}</h1>
          <p className="text-xs text-gray-500">Hospital Management System</p>
        </div>
      </div>
      {debugUserId && (
        <div className="hidden rounded bg-gray-100 px-2 py-1 text-xs text-gray-500 sm:block">
          uid: {debugUserId}
        </div>
      )}
    </header>
  );
}
