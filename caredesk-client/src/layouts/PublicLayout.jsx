import { Outlet } from 'react-router-dom';
import PublicNavbar from '../components/PublicNavbar';

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-blue-50">
      <PublicNavbar />
      <Outlet />
    </div>
  );
}
