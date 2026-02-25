import api from './axios';

export const courseAPI = {
  list: (params) => api.get('api/Course/', { params }),
  get: (id) => api.get(`/api/Course/${id}/`),
  create: (data) => api.post('/api/Course/', data),
  update: (id, data) => api.put(`/api/Course/${id}/`, data),
  delete: (id) => api.delete(`/api/Course/${id}/`),
};