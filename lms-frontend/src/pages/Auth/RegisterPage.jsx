import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../../api/auth';
import toast from 'react-hot-toast';
import { HiOutlineAcademicCap } from 'react-icons/hi';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', email: '', role: 'student', password: '', confirm_password: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm_password) { toast.error('Passwords do not match'); return; }
    setLoading(true);
    try {
      await authAPI.register(form);
      toast.success('Account created! Check your email for OTP.');
      navigate('/verify', { state: { email: form.email } });
    } catch (err) {
      const data = err.response?.data;
      const msg = typeof data === 'object' ? Object.values(data).flat().join(', ') : 'Registration failed';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-8">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-2 mb-8 justify-center">
          <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center"><HiOutlineAcademicCap className="text-white text-xl" /></div>
          <span className="text-xl font-bold text-gray-900">LMS</span>
        </div>
        <div className="card p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-1 text-center">Create Account</h2>
          <p className="text-gray-500 mb-6 text-center">Get started with your learning journey</p>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div><label className="label">Username</label><input type="text" required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} className="input-field" placeholder="johndoe" /></div>
            <div><label className="label">Email</label><input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="input-field" placeholder="you@example.com" /></div>
            <div><label className="label">Role</label><select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} className="input-field">
              <option value="student">Student</option><option value="instructor">Instructor</option><option value="sponsor">Sponsor</option>
            </select></div>
            <div><label className="label">Password</label><input type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="input-field" placeholder="Min 8 characters" /></div>
            <div><label className="label">Confirm Password</label><input type="password" required value={form.confirm_password} onChange={(e) => setForm({ ...form, confirm_password: e.target.value })} className="input-field" placeholder="••••••••" /></div>
            <button type="submit" disabled={loading} className="btn-primary w-full py-3!">{loading ? 'Creating...' : 'Create Account'}</button>
          </form>
          <p className="text-center text-sm text-gray-500 mt-4">Already have an account? <Link to="/login" className="text-primary-600 font-medium">Sign in</Link></p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;