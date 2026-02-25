import api from './axios';

export const authAPI = {
  register: (data) => api.post('/user/', data),
  login: (data) => api.post('/user/login/', data),
  verify: (data) => api.put('/user/verification/', data),
  forgotPassword: (data) => api.post('/user/send_otp_forgot_password/', data),
  resetPassword: (data) => api.put('/user/update_forgot_password/', data),
  getUserDetail: () => api.get('/user/detail/'),
  listUsers: () => api.get('/user/list_users/'),
};