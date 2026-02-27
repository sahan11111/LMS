import api from './axios';

export const quizAPI = {
  list: (params) => api.get('api/Quiz/', { params }),
  get: (id) => api.get(`api/Quiz/${id}/`),
  create: (data) => api.post('api/Quiz/', data),
  update: (id, data) => api.put(`api/Quiz/${id}/`, data),
  delete: (id) => api.delete(`api/Quiz/${id}/`),
};

export const quizSubmissionAPI = {
  list: () => api.get('api/QuizSubmissions/'),
  submit: (data) => api.post('api/QuizSubmissions/', data),
  get: (id) => api.get(`api/QuizSubmissions/${id}/`),
};