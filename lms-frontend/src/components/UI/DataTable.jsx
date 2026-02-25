import React from 'react';

const DataTable = ({ columns, data, onRowClick, emptyMessage = 'No data found.' }) => (
  <div className="card overflow-hidden">
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-100">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col) => (
              <th key={col.key} className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-50">
          {data.length === 0 ? (
            <tr><td colSpan={columns.length} className="px-6 py-12 text-center text-gray-400">{emptyMessage}</td></tr>
          ) : (
            data.map((row, i) => (
              <tr key={row.id || i} onClick={() => onRowClick?.(row)} className={`hover:bg-gray-50 transition-colors ${onRowClick ? 'cursor-pointer' : ''}`}>
                {columns.map((col) => (
                  <td key={col.key} className="px-6 py-4 text-sm text-gray-700 whitespace-nowrap">
                    {col.render ? col.render(row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  </div>
);

export default DataTable;