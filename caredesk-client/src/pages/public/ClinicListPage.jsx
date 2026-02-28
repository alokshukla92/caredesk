import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchPublicAPI } from '../../api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { MapPin, Phone, Users, ArrowRight, Search } from 'lucide-react';

export default function ClinicListPage() {
  const [clinics, setClinics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchPublicAPI('/api/public/clinics').then((res) => {
      if (res.status === 'success') setClinics(res.data);
      setLoading(false);
    });
  }, []);

  const filtered = clinics.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    (c.address || '').toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <LoadingSpinner />;

  return (
    <div className="px-4 py-6">
      <div className="mx-auto max-w-3xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Find a Clinic</h1>
          <p className="text-sm text-gray-500">Browse clinics and book your appointment</p>
        </div>

        {/* Search */}
        <div className="relative mb-6">
          <Search className="absolute left-4 top-3.5 text-gray-400" size={18} />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by clinic name or location..."
            className="w-full rounded-xl border border-gray-200 bg-white py-3 pl-11 pr-4 text-sm shadow-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
          />
        </div>

        {/* Clinic list */}
        {filtered.length === 0 ? (
          <div className="rounded-2xl bg-white p-12 text-center shadow-sm">
            <p className="text-gray-500">No clinics found.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filtered.map((c) => (
              <div key={c.id} className="rounded-2xl bg-white p-5 shadow-sm transition hover:shadow-md">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h2 className="text-lg font-bold text-gray-900">{c.name}</h2>
                    {c.address && (
                      <p className="mt-1 flex items-center gap-1 text-sm text-gray-500">
                        <MapPin size={14} /> {c.address}
                      </p>
                    )}
                    <div className="mt-2 flex flex-wrap gap-3 text-sm text-gray-500">
                      {c.phone && (
                        <span className="flex items-center gap-1">
                          <Phone size={13} /> {c.phone}
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Users size={13} /> {c.doctor_count} doctor(s)
                      </span>
                    </div>
                  </div>
                  <div className="ml-4 flex flex-col gap-2">
                    <Link
                      to={`/book/${c.slug}`}
                      className="flex items-center gap-1 rounded-lg bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700"
                    >
                      Book Now <ArrowRight size={14} />
                    </Link>
                    <Link
                      to={`/queue-display/${c.slug}`}
                      className="rounded-lg border border-gray-200 px-4 py-2 text-center text-xs font-medium text-gray-600 hover:bg-gray-50"
                    >
                      View Queue
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <p className="mt-8 text-center text-xs text-gray-400">Powered by CareDesk</p>
      </div>
    </div>
  );
}
