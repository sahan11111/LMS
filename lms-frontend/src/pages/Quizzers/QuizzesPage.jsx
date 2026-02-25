import React, { useEffect, useState, useCallback } from 'react';
import { quizAPI } from '../../api/quizzes';
import { useAuth } from '../../context/AuthContext';
import PageHeader from '../../components/UI/PageHeader';
import Modal from '../../components/UI/Modal';
import toast from 'react-hot-toast';
import { HiOutlinePlus, HiOutlineSearch, HiOutlinePencil, HiOutlineTrash, HiOutlinePuzzle } from 'react-icons/hi';

const QuizzesPage = () => {
  const { user } = useAuth();
  const role = user?.role;
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({ course: '', title: '', description: '' });

  const fetch = useCallback(async () => {
    setLoading(true);
    try { const r = await quizAPI.list({ search: search || undefined }); setQuizzes(r.data.results || r.data); }
    catch { toast.error('Failed'); } finally { setLoading(false); }
  }, [search]);

  useEffect(() => { fetch(); }, [fetch]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try { await quizAPI.create({ ...form, course: parseInt(form.course) }); toast.success('Quiz created'); setModalOpen(false); fetch(); }
    catch (err) { toast.error(typeof err.response?.data === 'object' ? Object.values(err.response.data).flat().join(', ') : 'Failed'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this quiz?')) return;
    try { await quizAPI.delete(id); toast.success('Deleted'); fetch(); } catch { toast.error('Failed'); }
  };

  const canCreate = ['admin', 'instructor'].includes(role);

  return (
    <div>
      <PageHeader title="Quizzes" subtitle="Manage quizzes" action={canCreate && <button onClick={() => { setForm({ course: '', title: '', description: '' }); setModalOpen(true); }} className="btn-primary"><HiOutlinePlus className="mr-2" />New Quiz</button>} />
      <div className="mb-6 max-w-md relative"><HiOutlineSearch className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" /><input type="text" placeholder="Search quizzes..." value={search} onChange={(e) => setSearch(e.target.value)} className="input-field pl-10" /></div>
      {loading ? <div className="flex justify-center py-12"><div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div> : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {quizzes.map((q) => (
            <div key={q.id} className="card p-6">
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 bg-purple-50 rounded-xl flex items-center justify-center"><HiOutlinePuzzle className="text-purple-600" /></div>
                {canCreate && <div className="flex gap-1">
                  <button onClick={() => handleDelete(q.id)} className="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500"><HiOutlineTrash /></button>
                </div>}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">{q.title}</h3>
              <p className="text-sm text-gray-500 mb-3">{q.description || 'No description'}</p>
              <p className="text-xs text-gray-400">{q.questions?.length || 0} questions · Course #{q.course}</p>
            </div>
          ))}
          {quizzes.length === 0 && <div className="col-span-full text-center py-12 text-gray-400">No quizzes found</div>}
        </div>
      )}
      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Create Quiz">
        <form onSubmit={handleCreate} className="space-y-4">
          <div><label className="label">Course ID</label><input type="number" required value={form.course} onChange={(e) => setForm({ ...form, course: e.target.value })} className="input-field" /></div>
          <div><label className="label">Title</label><input type="text" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="input-field" /></div>
          <div><label className="label">Description</label><textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={3} className="input-field" /></div>
          <div className="flex gap-3 pt-2"><button type="button" onClick={() => setModalOpen(false)} className="btn-secondary flex-1">Cancel</button><button type="submit" className="btn-primary flex-1">Create</button></div>
        </form>
      </Modal>
    </div>
  );
};

export default QuizzesPage;