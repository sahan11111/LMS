import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { dashboardAPI } from '../../api/dashboard';
import PageHeader from '../../components/UI/PageHeader';
import StatsCard from '../../components/UI/StatsCard';
import toast from 'react-hot-toast';
import {
  HiOutlineUserGroup, HiOutlineAcademicCap, HiOutlineClipboardList,
  HiOutlineDocumentText, HiOutlineCurrencyDollar, HiOutlineBell,
  HiOutlinePuzzle, HiOutlineMail, HiOutlineCheckCircle, HiOutlineClock,
} from 'react-icons/hi';

const DashboardPage = () => {
  const { user } = useAuth();
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardAPI.get().then((r) => setData(r.data)).catch(() => toast.error('Failed to load dashboard')).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div>;

  const role = user?.role;

  const adminStats = [
    { title: 'Total Users', value: data.total_users, icon: HiOutlineUserGroup, color: 'primary' },
    { title: 'Courses', value: data.total_courses, icon: HiOutlineAcademicCap, color: 'emerald' },
    { title: 'Enrollments', value: data.total_enrollments, icon: HiOutlineClipboardList, color: 'blue' },
    { title: 'Assessments', value: data.total_assessments, icon: HiOutlineDocumentText, color: 'amber' },
    { title: 'Submissions', value: data.total_submissions, icon: HiOutlineDocumentText, color: 'purple' },
    { title: 'Sponsors', value: data.total_sponsors, icon: HiOutlineCurrencyDollar, color: 'pink' },
    { title: 'Sponsorships', value: data.total_sponsorships, icon: HiOutlineCurrencyDollar, color: 'cyan' },
    { title: 'Notifications', value: data.total_notifications, icon: HiOutlineBell, color: 'amber' },
    { title: 'Quizzes', value: data.total_quizzes, icon: HiOutlinePuzzle, color: 'emerald' },
    { title: 'Email Logs', value: data.total_email_logs, icon: HiOutlineMail, color: 'blue' },
  ];

  const instructorStats = [
    { title: 'My Courses', value: data.my_courses, icon: HiOutlineAcademicCap, color: 'primary' },
    { title: 'My Enrollments', value: data.my_enrollments, icon: HiOutlineClipboardList, color: 'emerald' },
    { title: 'My Assessments', value: data.my_assessments, icon: HiOutlineDocumentText, color: 'blue' },
    { title: 'My Submissions', value: data.my_submissions, icon: HiOutlineDocumentText, color: 'amber' },
    { title: 'My Quizzes', value: data.my_quizzes, icon: HiOutlinePuzzle, color: 'purple' },
  ];

  const studentStats = [
    { title: 'Enrolled Courses', value: data.my_courses, icon: HiOutlineAcademicCap, color: 'primary' },
    { title: 'My Enrollments', value: data.my_enrollments, icon: HiOutlineClipboardList, color: 'emerald' },
    { title: 'Assessments', value: data.my_assessments, icon: HiOutlineDocumentText, color: 'blue' },
    { title: 'Submissions', value: data.my_submissions, icon: HiOutlineDocumentText, color: 'amber' },
    { title: 'Quizzes', value: data.my_quizzes, icon: HiOutlinePuzzle, color: 'purple' },
    { title: 'Passed Quizzes', value: data.my_passed_quizzes, icon: HiOutlineCheckCircle, color: 'emerald' },
    { title: 'Pending Sponsorships', value: data.my_pending_sponsorships, icon: HiOutlineClock, color: 'amber' },
    { title: 'Approved Sponsorships', value: data.my_approved_sponsorships, icon: HiOutlineCheckCircle, color: 'emerald' },
  ];

  const sponsorStats = [
    { title: 'Sponsored Students', value: data.sponsored_students, icon: HiOutlineUserGroup, color: 'primary' },
    { title: 'Total Sponsorships', value: data.sponsorships, icon: HiOutlineCurrencyDollar, color: 'emerald' },
    { title: 'Approved', value: data.approved_sponsorships, icon: HiOutlineCheckCircle, color: 'blue' },
    { title: 'Pending', value: data.pending_sponsorships, icon: HiOutlineClock, color: 'amber' },
    { title: 'Rejected', value: data.rejected_sponsorships, icon: HiOutlineDocumentText, color: 'red' },
    { title: 'Total Funds Given', value: `$${data.total_funds_provided || 0}`, icon: HiOutlineCurrencyDollar, color: 'purple' },
  ];

  const statsMap = { admin: adminStats, instructor: instructorStats, student: studentStats, sponsor: sponsorStats };
  const stats = statsMap[role] || [];

  return (
    <div>
      <PageHeader title={`Welcome back${user?.email ? ', ' + user.email.split('@')[0] : ''}!`} subtitle={`Your ${role} dashboard overview`} />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {stats.map((s, i) => <StatsCard key={i} {...s} />)}
      </div>
      {role === 'sponsor' && data.sponsored_students_list?.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sponsored Students</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.sponsored_students_list.map((s) => (
              <div key={s.id} className="card p-4 flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-bold text-sm">
                  {s.username?.charAt(0).toUpperCase()}
                </div>
                <div><p className="font-medium text-gray-900">{s.username}</p><p className="text-xs text-gray-500">ID: {s.id}</p></div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;