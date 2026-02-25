import React, { useEffect, useState } from 'react';
import { sponsorAPI } from '../../api/sponsors';
import PageHeader from '../../components/UI/PageHeader';
import DataTable from '../../components/UI/DataTable';
import toast from 'react-hot-toast';

const SponsorsPage = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { sponsorAPI.list().then((r) => setData(r.data.results || r.data)).catch(() => toast.error('Failed')).finally(() => setLoading(false)); }, []);

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'user', label: 'User' },
    { key: 'company_name', label: 'Company', render: (r) => r.company_name || '—' },
    { key: 'funds_provided', label: 'Funds', render: (r) => `$${r.funds_provided}` },
  ];

  return (
    <div>
      <PageHeader title="Sponsors" subtitle="Manage sponsors" />
      {loading ? <div className="flex justify-center py-12"><div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div> : <DataTable columns={columns} data={data} />}
    </div>
  );
};

export default SponsorsPage;