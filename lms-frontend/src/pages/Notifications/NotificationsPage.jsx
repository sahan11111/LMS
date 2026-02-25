import React, { useEffect, useState } from 'react';
import { notificationAPI } from '../../api/notifications';
import PageHeader from '../../components/UI/PageHeader';
import toast from 'react-hot-toast';
import { HiOutlineBell, HiOutlineCheckCircle } from 'react-icons/hi';

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    notificationAPI.list().then((r) => setNotifications(r.data.results || r.data)).catch(() => toast.error('Failed')).finally(() => setLoading(false));
  }, []);

  const markRead = async (id) => {
    try { await notificationAPI.markRead(id); setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, is_read: true } : n)); }
    catch { toast.error('Failed'); }
  };

  return (
    <div>
      <PageHeader title="Notifications" subtitle="Stay updated" />
      {loading ? <div className="flex justify-center py-12"><div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div> : (
        <div className="space-y-3">
          {notifications.length === 0 && <div className="text-center py-12 text-gray-400">No notifications</div>}
          {notifications.map((n) => (
            <div key={n.id} className={`card p-5 flex items-start gap-4 ${n.is_read ? 'opacity-60' : ''}`}>
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${n.is_read ? 'bg-gray-100' : 'bg-primary-50'}`}>
                <HiOutlineBell className={n.is_read ? 'text-gray-400' : 'text-primary-600'} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-800">{n.message}</p>
                <p className="text-xs text-gray-400 mt-1">{new Date(n.created_at).toLocaleString()}</p>
              </div>
              {!n.is_read && <button onClick={() => markRead(n.id)} className="p-2 rounded-lg hover:bg-emerald-50 text-gray-400 hover:text-emerald-600"><HiOutlineCheckCircle className="text-xl" /></button>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NotificationsPage;