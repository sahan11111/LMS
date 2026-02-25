import React, { useEffect, useState, useCallback } from 'react';
import { courseAPI } from '../../api/courses';
import { enrollmentAPI } from '../../api/enrollments';
import { useAuth } from '../../context/AuthContext';
import PageHeader from '../../components/UI/PageHeader';
import Modal from '../../components/UI/Modal';
import Pagination from '../../components/UI/Pagination';
import toast from 'react-hot-toast';
import { HiOutlinePlus, HiOutlineSearch, HiOutlinePencil, HiOutlineTrash } from 'react-icons/hi';

const CoursesPage = () => {
  const { user } = useAuth();
  const role = user?.role;
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState(null);
  const [form, setForm] = useState({ title: '', description: '', difficulty_level: 'beginner' });

  const fetchCourses = useCallback(async () => {
    setLoading(true);
    try {
      const res = await courseAPI.list({ page, search: search || undefined });
      setCourses(res.data.results || res.data);
      setTotalPages(res.data.count ? Math.ceil(res.data.count / 10) : 1);
    } catch { toast.error('Failed to load courses'); }
    finally { setLoading(false); }
  }, [page, search]);

  useEffect(() => { fetchCourses(); }, [fetchCourses]);

  const openCreate = () => { setEditingCourse(null); setForm({ title: '', description: '', difficulty_level: 'beginner' }); setModalOpen(true); };
  const openEdit = (c) => { setEditingCourse(c); setForm({ title: c.title, description: c.description, difficulty_level: c.difficulty_level }); setModalOpen(true); };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      if (editingCourse) { await courseAPI.update(editingCourse.id, form); toast.success('Course updated'); }
      else { await courseAPI.create(form); toast.success('Course created'); }
      setModalOpen(false); fetchCourses();
    } catch (err) {
      toast.error(typeof err.response?.data === 'object' ? Object.values(err.response.data).flat().join(', ') : 'Failed');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this course?')) return;
    try { await courseAPI.delete(id); toast.success('Course deleted'); fetchCourses(); }
    catch { toast.error('Failed to delete'); }
  };

  const handleEnroll = async (courseId) => {
    try { await enrollmentAPI.create({ course: courseId }); toast.success('Enrolled successfully!'); }
    catch (err) { toast.error(err.response?.data?.non_field_errors?.[0] || 'Enrollment failed'); }
  };

  const canCreate = ['admin', 'instructor'].includes(role);

  const difficultyColors = { beginner: 'bg-emerald-50 text-emerald-700', intermediate: 'bg-amber-50 text-amber-700', advanced: 'bg-red-50 text-red-700' };

  return (
    <div>
      <PageHeader title="Courses" subtitle="Manage and explore courses" action={canCreate && <button onClick={openCreate} className="btn-primary"><HiOutlinePlus className="mr-2" />New Course</button>} />

      {/* Search */}
      <div className="mb-6 max-w-md relative">
        <HiOutlineSearch className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
        <input type="text" placeholder="Search courses..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} className="input-field pl-10" />
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" /></div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {courses.map((c) => (
              <div key={c.id} className="card p-6 flex flex-col">
                <div className="flex items-start justify-between mb-3">
                  <span className={`badge ${difficultyColors[c.difficulty_level] || 'bg-gray-100 text-gray-600'}`}>{c.difficulty_level}</span>
                  {canCreate && (
                    <div className="flex gap-1">
                      <button onClick={() => openEdit(c)} className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400"><HiOutlinePencil /></button>
                      <button onClick={() => handleDelete(c.id)} className="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500"><HiOutlineTrash /></button>
                    </div>
                  )}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{c.title}</h3>
                <p className="text-sm text-gray-500 flex-1 line-clamp-3 mb-4">{c.description}</p>
                {role === 'student' && (
                  <button onClick={() => handleEnroll(c.id)} className="btn-secondary w-full">Enroll Now</button>
                )}
              </div>
            ))}
          </div>
          {courses.length === 0 && <div className="text-center py-12 text-gray-400">No courses found.</div>}
          <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
        </>
      )}

      {/* Create/Edit Modal */}
      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingCourse ? 'Edit Course' : 'Create Course'}>
        <form onSubmit={handleSave} className="space-y-4">
          <div><label className="label">Title</label><input type="text" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="input-field" /></div>
          <div><label className="label">Description</label><textarea required value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={4} className="input-field" /></div>
          <div><label className="label">Difficulty</label><select value={form.difficulty_level} onChange={(e) => setForm({ ...form, difficulty_level: e.target.value })} className="input-field">
            <option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option>
          </select></div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setModalOpen(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" className="btn-primary flex-1">{editingCourse ? 'Update' : 'Create'}</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default CoursesPage;