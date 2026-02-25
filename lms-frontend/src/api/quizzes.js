import api from './axios';

export const quizAPI = {
  list: (params) => api.get('/Quiz/', { params }),
  get: (id) => api.get(`/Quiz/${id}/`),
  create: (data) => api.post('/Quiz/', data),
  update: (id, data) => api.put(`/Quiz/${id}/`, data),
  delete: (id) => api.delete(`/Quiz/${id}/`),
};

export const quizSubmissionAPI = {
  list: () => api.get('/QuizSubmissions/'),
  submit: (data) => api.post('/QuizSubmissions/', data),
  get: (id) => api.get(`/QuizSubmissions/${id}/`),
};