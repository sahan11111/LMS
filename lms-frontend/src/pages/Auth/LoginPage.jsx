import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';
import {
  HiOutlineAcademicCap,
  HiOutlineMail,
  HiOutlineLockClosed,
  HiSparkles,
  HiOutlineChartBar,
  HiOutlineUserGroup,
} from 'react-icons/hi';

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '', role: 'student' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(form);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-slate-100">
      <div className="pointer-events-none absolute inset-0 opacity-60">
        <div className="absolute -top-32 -left-24 h-80 w-80 rounded-full bg-primary-300 blur-3xl" />
        <div className="absolute -bottom-28 right-0 h-80 w-80 rounded-full bg-cyan-200 blur-3xl" />
      </div>

      <div className="relative z-10 flex min-h-screen">
        {/* Left panel */}
        <div className="hidden lg:flex lg:w-1/2 bg-[radial-gradient(circle_at_top_left,_#6366f1,_#312e81_70%)] items-center justify-center p-12">
          <div className="max-w-lg text-white">
            <div className="inline-flex items-center gap-2 rounded-full bg-white/15 px-4 py-1.5 text-sm font-semibold tracking-wide backdrop-blur-sm mb-8">
              <HiSparkles className="text-amber-200" />
              Built for modern learning teams
            </div>

            <HiOutlineAcademicCap className="text-7xl mb-6 opacity-95" />
            <h1 className="text-5xl font-extrabold leading-tight mb-5">Level up teaching and learning in one workspace.</h1>
            <p className="text-lg text-primary-100 leading-relaxed mb-10">
              Organize courses, monitor progress, and deliver better outcomes with an interface designed for students, instructors, and admins.
            </p>

            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-2xl border border-white/25 bg-white/10 p-4 backdrop-blur-sm">
                <HiOutlineChartBar className="text-2xl text-cyan-200 mb-2" />
                <p className="text-sm text-primary-100">Real-time progress analytics</p>
              </div>
              <div className="rounded-2xl border border-white/25 bg-white/10 p-4 backdrop-blur-sm">
                <HiOutlineUserGroup className="text-2xl text-emerald-200 mb-2" />
                <p className="text-sm text-primary-100">Unified learner collaboration</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right panel */}
        <div className="flex-1 flex items-center justify-center p-6 md:p-10">
          <div className="w-full max-w-md rounded-3xl border border-white/60 bg-white/75 p-7 sm:p-8 shadow-2xl backdrop-blur-xl">
            <div className="lg:hidden flex items-center gap-2 mb-8">
              <div className="w-11 h-11 bg-primary-600 rounded-xl flex items-center justify-center shadow-md shadow-primary-500/30">
                <HiOutlineAcademicCap className="text-white text-xl" />
              </div>
              <span className="text-xl font-extrabold text-slate-900 tracking-tight">LMS</span>
            </div>

            <div className="mb-8">
              <h2 className="text-3xl font-extrabold text-slate-900 mb-2 tracking-tight">Welcome back</h2>
              <p className="text-slate-600">Sign in to continue to your dashboard.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="label">Email</label>
                <div className="relative">
                  <HiOutlineMail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="input-field pl-10" placeholder="you@example.com" />
                </div>
              </div>

              <div>
                <label className="label">Password</label>
                <div className="relative">
                  <HiOutlineLockClosed className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="input-field pl-10" placeholder="••••••••" />
                </div>
              </div>

              <div>
                <label className="label">Role</label>
                <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} className="input-field">
                  <option value="student">Student</option>
                  <option value="instructor">Instructor</option>
                  <option value="admin">Admin</option>
                  <option value="sponsor">Sponsor</option>
                </select>
              </div>

              <button type="submit" disabled={loading} className="btn-primary w-full py-3! bg-slate-900 hover:bg-slate-800 focus:ring-slate-400">
                {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Sign In'}
              </button>
            </form>

            <div className="mt-6 flex items-center justify-between text-sm">
              <Link to="/forgot-password" className="text-slate-600 hover:text-slate-900 font-semibold transition-colors">Forgot password?</Link>
              <Link to="/register" className="text-primary-700 hover:text-primary-800 font-semibold transition-colors">Create account</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;