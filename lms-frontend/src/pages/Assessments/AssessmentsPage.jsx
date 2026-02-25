import React, { useEffect, useState } from 'react';
import { assessmentAPI } from '../../api/assessments';
import PageHeader from '../../components/UI/PageHeader';
import DataTable from '../../components/UI/DataTable';
import toast from 'react-hot-toast';

const AssessmentsPage = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { assessmentAPI.list().then((r) => setData(r.data.results || r.data)).catch(() => toast.error('Failed')).finally(() => setLoading(false)); }, []);

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'title', label: 'Title' },
    { key: 'course', label: 'Course' },
    { key: 'max_score', label: 'Max Score' },
    { key: 'due_date', label: 'Due Date', render: (r) => new Date(r.due_date).toLocaleDateString() },
  ];

  return (
    <div>
      <PageHeader title="Assessments" subtitle="View and manage assessments" />
      {loading ? <div className="flex justify-center py-12"><div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div> : <DataTable columns={columns} data={data} />}
    </div>
  );
};

export default AssessmentsPage;