import api from './axios';

export const enrollmentAPI = {
  list: (params) => api.get('api/Enrollment/', { params }),
  get: (id) => api.get(`/api/Enrollment/${id}/`),
  create: (data) => api.post('/api/Enrollment/', data),
  update: (id, data) => api.put(`/api/Enrollment/${id}/`, data),
  delete: (id) => api.delete(`/api/Enrollment/${id}/`),
};