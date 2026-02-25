import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  HiOutlineHome, HiOutlineAcademicCap, HiOutlineClipboardList,
  HiOutlineDocumentText, HiOutlinePuzzle, HiOutlineBell,
  HiOutlineUserGroup, HiOutlineCurrencyDollar, HiOutlineLogout,
  HiOutlineChevronLeft, HiOutlineChevronRight, HiOutlineUser,
} from 'react-icons/hi';

const Sidebar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const role = user?.role;

  const handleLogout = () => { logout(); navigate('/login'); };

  const navItems = [
    { to: '/dashboard', icon: HiOutlineHome, label: 'Dashboard', roles: ['admin', 'instructor', 'student', 'sponsor'] },
    { to: '/courses', icon: HiOutlineAcademicCap, label: 'Courses', roles: ['admin', 'instructor', 'student', 'sponsor'] },
    { to: '/enrollments', icon: HiOutlineClipboardList, label: 'Enrollments', roles: ['admin', 'instructor', 'student', 'sponsor'] },
    { to: '/assessments', icon: HiOutlineDocumentText, label: 'Assessments', roles: ['admin', 'instructor', 'student'] },
    { to: '/submissions', icon: HiOutlineDocumentText, label: 'Submissions', roles: ['admin', 'instructor', 'student'] },
    { to: '/quizzes', icon: HiOutlinePuzzle, label: 'Quizzes', roles: ['admin', 'instructor', 'student'] },
    { to: '/sponsors', icon: HiOutlineCurrencyDollar, label: 'Sponsors', roles: ['admin', 'sponsor'] },
    { to: '/sponsorships', icon: HiOutlineCurrencyDollar, label: 'Sponsorships', roles: ['admin', 'sponsor', 'student'] },
    { to: '/users', icon: HiOutlineUserGroup, label: 'Users', roles: ['admin'] },
    { to: '/notifications', icon: HiOutlineBell, label: 'Notifications', roles: ['admin', 'instructor', 'student', 'sponsor'] },
  ];

  const filtered = navItems.filter((item) => item.roles.includes(role));

  return (
    <aside className={`fixed top-0 left-0 h-screen bg-white border-r border-gray-200 z-40 transition-all duration-300 flex flex-col ${collapsed ? 'w-20' : 'w-64'}`}>
      {/* Logo */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-gray-100">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 bg-primary-600 rounded-xl flex items-center justify-center">
              <HiOutlineAcademicCap className="text-white text-xl" />
            </div>
            <span className="text-lg font-bold text-gray-900">LMS</span>
          </div>
        )}
        <button onClick={() => setCollapsed(!collapsed)} className="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
          {collapsed ? <HiOutlineChevronRight /> : <HiOutlineChevronLeft />}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        {filtered.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200
              ${isActive ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`
            }
          >
            <item.icon className="text-lg flex-shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="border-t border-gray-100 p-3">
        <div className={`flex items-center gap-3 px-3 py-2 ${collapsed ? 'justify-center' : ''}`}>
          <div className="w-9 h-9 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
            <HiOutlineUser className="text-primary-600" />
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-900 truncate">{user?.email}</p>
              <p className="text-xs text-gray-500 capitalize">{role}</p>
            </div>
          )}
        </div>
        <button onClick={handleLogout} className={`flex items-center gap-3 w-full px-3 py-2.5 mt-1 rounded-xl text-sm font-medium text-red-600 hover:bg-red-50 transition-all ${collapsed ? 'justify-center' : ''}`}>
          <HiOutlineLogout className="text-lg" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;