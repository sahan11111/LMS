import React, { useEffect, useState } from 'react';
import { sponsorshipAPI } from '../../api/sponsors';
import { useAuth } from '../../context/AuthContext';
import PageHeader from '../../components/UI/PageHeader';
import DataTable from '../../components/UI/DataTable';
import StatusBadge from '../../components/UI/StatusBadge';
import toast from 'react-hot-toast';

const SponsorshipsPage = () => {
  const { user } = useAuth();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetch = () => { sponsorshipAPI.list().then((r) => setData(r.data.results || r.data)).catch(() => toast.error('Failed')).finally(() => setLoading(false)); };
  useEffect(() => { fetch(); }, []);

  const handleAction = async (id, status) => {
    try { await sponsorshipAPI.update(id, { status }); toast.success(`Sponsorship ${status}`); fetch(); }
    catch { toast.error('Failed'); }
  };

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'sponsor', label: 'Sponsor' },
    { key: 'student', label: 'Student' },
    { key: 'amount', label: 'Amount', render: (r) => `$${r.amount}` },
    { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
    ...(user?.role === 'sponsor' ? [{
      key: 'actions', label: 'Actions', render: (r) => r.status === 'pending' ? (
        <div className="flex gap-2">
          <button onClick={() => handleAction(r.id, 'approved')} className="btn-success !py-1 !px-3 !text-xs">Approve</button>
          <button onClick={() => handleAction(r.id, 'rejected')} className="btn-danger !py-1 !px-3 !text-xs">Reject</button>
        </div>
      ) : null
    }] : []),
  ];

  return (
    <div>
      <PageHeader title="Sponsorships" subtitle="Manage sponsorship requests" />
      {loading ? <div className="flex justify-center py-12"><div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div> : <DataTable columns={columns} data={data} />}
    </div>
  );
};

export default SponsorshipsPage;