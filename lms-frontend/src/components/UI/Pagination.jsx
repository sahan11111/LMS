import React from 'react';
import { HiOutlineChevronLeft, HiOutlineChevronRight } from 'react-icons/hi';

const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  if (totalPages <= 1) return null;

  const pages = [];
  const start = Math.max(1, currentPage - 2);
  const end = Math.min(totalPages, currentPage + 2);
  for (let i = start; i <= end; i++) pages.push(i);

  return (
    <div className="flex items-center justify-center gap-1 mt-6">
      <button disabled={currentPage === 1} onClick={() => onPageChange(currentPage - 1)} className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed text-gray-500">
        <HiOutlineChevronLeft />
      </button>
      {pages.map((p) => (
        <button key={p} onClick={() => onPageChange(p)} className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${p === currentPage ? 'bg-primary-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}>
          {p}
        </button>
      ))}
      <button disabled={currentPage === totalPages} onClick={() => onPageChange(currentPage + 1)} className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed text-gray-500">
        <HiOutlineChevronRight />
      </button>
    </div>
  );
};

export default Pagination;