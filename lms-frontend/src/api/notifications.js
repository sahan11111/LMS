import api from './axios';

export const notificationAPI = {
  list: (params) => api.get('api/Notification/', { params }),
  get: (id) => api.get(`api/Notification/${id}/`),
  markRead: (id) => api.patch(`api/Notification/${id}/`, { is_read: true }),
};