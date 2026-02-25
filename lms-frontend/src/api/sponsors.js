import api from './axios';

export const sponsorAPI = {
  list: (params) => api.get('/Sponsor/', { params }),
  get: (id) => api.get(`/Sponsor/${id}/`),
  create: (data) => api.post('/Sponsor/', data),
  update: (id, data) => api.put(`/Sponsor/${id}/`, data),
};

export const sponsorshipAPI = {
  list: (params) => api.get('/Sponsorship/', { params }),
  get: (id) => api.get(`/Sponsorship/${id}/`),
  create: (data) => api.post('/Sponsorship/', data),
  update: (id, data) => api.put(`/Sponsorship/${id}/`, data),
};