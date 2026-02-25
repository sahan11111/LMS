import React, { useEffect, useState } from 'react';
import { submissionAPI } from '../../api/submissions';
import PageHeader from '../../components/UI/PageHeader';
import DataTable from '../../components/UI/DataTable';
import toast from 'react-hot-toast';

const SubmissionsPage = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    submissionAPI
      .list()
      .then((r) => setData(r.data.results || r.data))
      .catch(() => toast.error('Failed to load submissions'))
      .finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'assessment', label: 'Assessment' },
    { key: 'student', label: 'Student' },
    {
      key: 'score',
      label: 'Score',
      render: (r) =>
        r.score !== null ? r.score : <span className="text-gray-400">Ungraded</span>,
    },
    {
      key: 'submitted_at',
      label: 'Submitted',
      render: (r) => new Date(r.submitted_at).toLocaleString(),
    },
  ];

  return (
    <div>
      <PageHeader title="Submissions" subtitle="View assessment submissions" />
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
        </div>
      ) : (
        <DataTable columns={columns} data={data} />
      )}
    </div>
  );
};

export default SubmissionsPage;