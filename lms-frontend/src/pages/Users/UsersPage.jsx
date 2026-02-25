import React, { useEffect, useState } from 'react';
import { authAPI } from '../../api/auth';
import PageHeader from '../../components/UI/PageHeader';
import DataTable from '../../components/UI/DataTable';
import toast from 'react-hot-toast';

const UsersPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { authAPI.listUsers().then((r) => setUsers(r.data)).catch(() => toast.error('Failed')).finally(() => setLoading(false)); }, []);

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'email', label: 'Email' },
    { key: 'username', label: 'Username' },
    { key: 'role', label: 'Role', render: (r) => <span className="badge bg-primary-50 text-primary-700 capitalize">{r.role}</span> },
  ];

  return (
    <div>
      <PageHeader title="Users" subtitle="All registered users (Admin only)" />
      {loading ? <div className="flex justify-center py-12"><div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div> : <DataTable columns={columns} data={users} />}
    </div>
  );
};

export default UsersPage;