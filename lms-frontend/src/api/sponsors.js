import api from './axios';

export const sponsorAPI = {
  list: (params) => api.get('api/Sponsor/', { params }),
  get: (id) => api.get(`api/Sponsor/${id}/`),
  create: (data) => api.post('api/Sponsor/', data),
  update: (id, data) => api.put(`api/Sponsor/${id}/`, data),
};

export const sponsorshipAPI = {
  list: (params) => api.get('api/Sponsorship/', { params }),
  get: (id) => api.get(`api/Sponsorship/${id}/`),
  create: (data) => api.post('api/Sponsorship/', data),
  update: (id, data) => api.put(`api/Sponsorship/${id}/`, data),
};