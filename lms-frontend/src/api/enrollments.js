import api from './axios';

export const enrollmentAPI = {
  list: (params) => api.get('/Enrollment/', { params }),
  get: (id) => api.get(`/Enrollment/${id}/`),
  create: (data) => api.post('/Enrollment/', data),
  update: (id, data) => api.put(`/Enrollment/${id}/`, data),
  delete: (id) => api.delete(`/Enrollment/${id}/`),
};