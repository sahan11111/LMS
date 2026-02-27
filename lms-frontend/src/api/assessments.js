import api from './axios';

export const assessmentAPI = {
  list: (params) => api.get('api/Assessment/', { params }),
  get: (id) => api.get(`api/Assessment/${id}/`),
  create: (data) => api.post('api/Assessment/', data),
  update: (id, data) => api.put(`api/Assessment/${id}/`, data),
  delete: (id) => api.delete(`api/Assessment/${id}/`),
};