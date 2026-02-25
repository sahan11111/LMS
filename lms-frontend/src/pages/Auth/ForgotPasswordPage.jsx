import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../../api/auth';
import toast from 'react-hot-toast';

const ForgotPasswordPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({ email: '', otp: '', password: '', confirm_password: '' });
  const [loading, setLoading] = useState(false);

  const sendOTP = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await authAPI.forgotPassword({ email: form.email });
      toast.success('OTP sent to your email!');
      setStep(2);
    } catch (err) {
      toast.error('Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm_password) { toast.error('Passwords do not match'); return; }
    setLoading(true);
    try {
      await authAPI.resetPassword(form);
      toast.success('Password reset successful!');
      navigate('/login');
    } catch (err) {
      toast.error('Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-8">
      <div className="w-full max-w-md card p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-1 text-center">Reset Password</h2>
        <p className="text-gray-500 mb-6 text-center">{step === 1 ? 'Enter your email to receive an OTP' : 'Enter OTP and new password'}</p>
        {step === 1 ? (
          <form onSubmit={sendOTP} className="space-y-4">
            <div><label className="label">Email</label><input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="input-field" /></div>
            <button type="submit" disabled={loading} className="btn-primary w-full !py-3">{loading ? 'Sending...' : 'Send OTP'}</button>
          </form>
        ) : (
          <form onSubmit={resetPassword} className="space-y-4">
            <div><label className="label">OTP Code</label><input type="text" required value={form.otp} onChange={(e) => setForm({ ...form, otp: e.target.value })} className="input-field" /></div>
            <div><label className="label">New Password</label><input type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="input-field" /></div>
            <div><label className="label">Confirm Password</label><input type="password" required value={form.confirm_password} onChange={(e) => setForm({ ...form, confirm_password: e.target.value })} className="input-field" /></div>
            <button type="submit" disabled={loading} className="btn-primary w-full !py-3">{loading ? 'Resetting...' : 'Reset Password'}</button>
          </form>
        )}
        <p className="text-center text-sm text-gray-500 mt-4"><Link to="/login" className="text-primary-600 font-medium">Back to login</Link></p>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;