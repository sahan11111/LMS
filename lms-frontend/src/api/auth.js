import api from './axios';

export const authAPI = {
  register: (data) => api.post('api/auth/user/', data),
  login: (data) => api.post('api/auth/user/login/', data),
  verify: (data) => api.put('api/auth/user/verification/', data),
  forgotPassword: (data) => api.post('api/auth/user/forgot-password/', data),
  resetPassword: (data) => api.put('api/auth/user/reset-password/', data),
  getUserDetail: () => api.get('api/auth/user/detail/'),
  listUsers: () => api.get('api/auth/user/list_users/'),
};