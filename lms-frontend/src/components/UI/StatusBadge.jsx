import React from 'react';

const StatusBadge = ({ status }) => {
  const styles = {
    active: 'badge-success',
    completed: 'badge-info',
    dropped: 'badge-danger',
    approved: 'badge-success',
    pending: 'badge-warning',
    rejected: 'badge-danger',
  };

  return <span className={styles[status] || 'badge bg-gray-100 text-gray-600'}>{status}</span>;
};

export default StatusBadge;