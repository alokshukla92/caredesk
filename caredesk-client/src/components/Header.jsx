export default function Header({ clinicName = 'CareDesk' }) {
  return (
    <header className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-3">
      <div>
        <h1 className="text-lg font-semibold text-gray-900">{clinicName}</h1>
        <p className="text-xs text-gray-500">Hospital Management System</p>
      </div>
    </header>
  );
}
