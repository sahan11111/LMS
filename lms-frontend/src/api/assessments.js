import api from './axios';

export const assessmentAPI = {
  list: (params) => api.get('/Assessment/', { params }),
  get: (id) => api.get(`/Assessment/${id}/`),
  create: (data) => api.post('/Assessment/', data),
  update: (id, data) => api.put(`/Assessment/${id}/`, data),
  delete: (id) => api.delete(`/Assessment/${id}/`),
};