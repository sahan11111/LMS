import api from './axios';

export const submissionAPI = {
  list: (params) => api.get('/Submission/', { params }),
  get: (id) => api.get(`/Submission/${id}/`),
  create: (data) => api.post('/Submission/', data),
  grade: (id, data) => api.patch(`/Submission/${id}/grade/`, data),
};