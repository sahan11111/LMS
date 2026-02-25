import api from './axios';

export const notificationAPI = {
  list: (params) => api.get('/Notification/', { params }),
  get: (id) => api.get(`/Notification/${id}/`),
  markRead: (id) => api.patch(`/Notification/${id}/`, { is_read: true }),
};