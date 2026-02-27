import api from './axios';

export const submissionAPI = {
  list: (params) => api.get('api/Submission/', { params }),
  get: (id) => api.get(`api/Submission/${id}/`),
  create: (data) => api.post('api/Submission/', data),
  grade: (id, data) => api.patch(`api/Submission/${id}/grade/`, data),
};