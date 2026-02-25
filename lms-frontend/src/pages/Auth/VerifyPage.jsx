import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { authAPI } from '../../api/auth';
import toast from 'react-hot-toast';
import { HiOutlineShieldCheck } from 'react-icons/hi';

const VerifyPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: location.state?.email || '', otp: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await authAPI.verify(form);
      toast.success('Email verified! You can now login.');
      navigate('/login');
    } catch (err) {
      toast.error(err.response?.data?.otp?.[0] || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-8">
      <div className="w-full max-w-md card p-8 text-center">
        <div className="w-16 h-16 bg-primary-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <HiOutlineShieldCheck className="text-primary-600 text-3xl" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-1">Verify Your Email</h2>
        <p className="text-gray-500 mb-6">Enter the OTP sent to your email</p>
        <form onSubmit={handleSubmit} className="space-y-4 text-left">
          <div><label className="label">Email</label><input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="input-field" /></div>
          <div><label className="label">OTP Code</label><input type="text" required maxLength={6} value={form.otp} onChange={(e) => setForm({ ...form, otp: e.target.value })} className="input-field text-center text-2xl tracking-[0.5em] font-mono" placeholder="••••" /></div>
          <button type="submit" disabled={loading} className="btn-primary w-full py-3!">{loading ? 'Verifying...' : 'Verify Email'}</button>
        </form>
        <p className="text-sm text-gray-500 mt-4"><Link to="/login" className="text-primary-600 font-medium">Back to login</Link></p>
      </div>
    </div>
  );
};

export default VerifyPage;