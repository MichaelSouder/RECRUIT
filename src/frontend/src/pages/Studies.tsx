import React, { useEffect, useState } from 'react';
import { studiesApi } from '../api/endpoints';
import { Study, PaginatedResponse } from '../types';
import { Button } from '../components/ui/Button';
import { Edit, Trash2, Eye } from 'lucide-react';
import { format } from 'date-fns';
import { Link } from 'react-router-dom';

export const Studies: React.FC = () => {
  const [studies, setStudies] = useState<Study[]>([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    page: 1,
    size: 20,
    total: 0,
    pages: 0,
  });

  const fetchStudies = async () => {
    setLoading(true);
    try {
      const response = await studiesApi.getAll({
        skip: (pagination.page - 1) * pagination.size,
        limit: pagination.size,
      });
      const data: PaginatedResponse<Study> = response.data;
      setStudies(data.items);
      setPagination({
        page: data.page,
        size: data.size,
        total: data.total,
        pages: data.pages,
      });
    } catch (error) {
      console.error('Failed to fetch studies:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudies();
  }, [pagination.page]);

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this study?')) return;
    try {
      await studiesApi.delete(id);
      fetchStudies();
    } catch (error) {
      console.error('Failed to delete study:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Studies</h1>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : studies.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No studies found</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {studies.map((study) => (
              <div key={study.id} className="card">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">{study.name}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(study.status)}`}>
                    {study.status}
                  </span>
                </div>
                {study.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">{study.description}</p>
                )}
                <div className="space-y-2 text-sm text-gray-500 mb-4">
                  {study.start_date && (
                    <p>Start: {format(new Date(study.start_date), 'MMM dd, yyyy')}</p>
                  )}
                  {study.end_date && (
                    <p>End: {format(new Date(study.end_date), 'MMM dd, yyyy')}</p>
                  )}
                </div>
                <div className="flex space-x-2">
                  <Link
                    to={`/studies/${study.id}`}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center space-x-2"
                    title="View Details"
                  >
                    <Eye className="w-4 h-4" />
                  </Link>
                  <Link
                    to={`/studies/${study.id}/edit`}
                    className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 flex items-center space-x-2"
                    title="Edit"
                  >
                    <Edit className="w-4 h-4" />
                  </Link>
                  <button
                    onClick={() => handleDelete(study.id)}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center space-x-2"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {pagination.pages > 1 && (
            <div className="mt-6 flex justify-center space-x-2">
              <Button
                variant="secondary"
                onClick={() => setPagination({ ...pagination, page: pagination.page - 1 })}
                disabled={pagination.page === 1}
              >
                Previous
              </Button>
              <span className="px-4 py-2 text-sm text-gray-700">
                Page {pagination.page} of {pagination.pages}
              </span>
              <Button
                variant="secondary"
                onClick={() => setPagination({ ...pagination, page: pagination.page + 1 })}
                disabled={pagination.page >= pagination.pages}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

