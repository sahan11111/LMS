import api from './axios';

export const courseAPI = {
  list: (params) => api.get('/Course/', { params }),
  get: (id) => api.get(`/Course/${id}/`),
  create: (data) => api.post('/Course/', data),
  update: (id, data) => api.put(`/Course/${id}/`, data),
  delete: (id) => api.delete(`/Course/${id}/`),
};