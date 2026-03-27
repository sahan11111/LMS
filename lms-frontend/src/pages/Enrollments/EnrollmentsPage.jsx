import React, { useEffect, useState, useCallback } from 'react';
import { enrollmentAPI } from '../../api/enrollments';
import PageHeader from '../../components/UI/PageHeader';
import DataTable from '../../components/UI/DataTable';
import StatusBadge from '../../components/UI/StatusBadge';
import Pagination from '../../components/UI/Pagination';
import toast from 'react-hot-toast';

const EnrollmentsPage = () => {
  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const res = await enrollmentAPI.list({ page });
      setEnrollments(res.data.results || res.data);
      setTotalPages(res.data.count ? Math.ceil(res.data.count / 10) : 1);
    } catch { toast.error('Failed to load enrollments'); }
    finally { setLoading(false); }
  }, [page]);

  useEffect(() => { fetch(); }, [fetch]);

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'student', label: 'Student' },
    { key: 'course', label: 'Course' },
    { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
    { key: 'progress', label: 'Progress', render: (r) => (
      <div className="flex items-center gap-2">
        <div className="w-20 h-2 bg-gray-100 rounded-full overflow-hidden"><div className="h-full bg-primary-500 rounded-full" style={{ width: `${r.progress}%` }} /></div>
        <span className="text-xs text-gray-500">{r.progress}%</span>
      </div>
    )},
  ];
  return (
    <div>
      <PageHeader title="Enrollments" subtitle="View all enrollments" />
      {loading ? <div className="flex justify-center py-12"><div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div> : (
        <><DataTable columns={columns} data={enrollments} /><Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} /></>
      )}
    </div>
  );
};

export default EnrollmentsPage;
