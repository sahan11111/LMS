import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';

import AppLayout from './components/Layout/AppLayout';
import LoginPage from './pages/Auth/LoginPage';
import RegisterPage from './pages/Auth/RegisterPage';
import VerifyPage from './pages/Auth/VerifyPage';
import ForgotPasswordPage from './pages/Auth/ForgotPasswordPage';
import DashboardPage from './pages/Dashboard/DashboardPage';
import CoursesPage from './pages/Courses/CoursesPage';
import EnrollmentsPage from './pages/Enrollments/EnrollmentsPage';
import AssessmentsPage from './pages/Assessments/AssessmentsPage';
import SubmissionsPage from './pages/Submissions/SubmissionsPage';
import QuizzesPage from './pages/Quizzes/QuizzesPage';
import SponsorsPage from './pages/Sponsors/SponsorsPage';
import SponsorshipsPage from './pages/Sponsorships/SponsorshipsPage';
import NotificationsPage from './pages/Notifications/NotificationsPage';
import UsersPage from './pages/Users/UsersPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: { borderRadius: '12px', background: '#1e293b', color: '#fff', fontSize: '14px' },
          }}
        />
        <Routes>
          {/* Auth */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify" element={<VerifyPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />

          {/* Protected */}
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/courses" element={<CoursesPage />} />
            <Route path="/enrollments" element={<EnrollmentsPage />} />
            <Route path="/assessments" element={<AssessmentsPage />} />
            <Route path="/submissions" element={<SubmissionsPage />} />
            <Route path="/quizzes" element={<QuizzesPage />} />
            <Route path="/sponsors" element={<SponsorsPage />} />
            <Route path="/sponsorships" element={<SponsorshipsPage />} />
            <Route path="/notifications" element={<NotificationsPage />} />
            <Route path="/users" element={<UsersPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;