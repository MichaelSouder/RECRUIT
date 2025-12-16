import React, { useEffect, useState } from 'react';
import { subjectsApi } from '../api/endpoints';
import { Subject, PaginatedResponse } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { Search, Plus, Edit, Trash2, Eye, ArrowUp, ArrowDown } from 'lucide-react';
import { format } from 'date-fns';
import { Link } from 'react-router-dom';
import { useStudyStore } from '../store/studyStore';

export const Subjects: React.FC = () => {
  const { selectedStudy } = useStudyStore();
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [sortBy, setSortBy] = useState<'name' | 'dob' | 'sex' | 'race' | null>(null);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [pagination, setPagination] = useState({
    page: 1,
    size: 20,
    total: 0,
    pages: 0,
  });

  const fetchSubjects = async () => {
    setLoading(true);
    try {
      const params: any = {
        skip: (pagination.page - 1) * pagination.size,
        limit: pagination.size,
        search: search || undefined,
        study_id: selectedStudy?.id,
      };
      if (sortBy) {
        params.sort_by = sortBy;
        params.sort_order = sortOrder;
      }
      const response = await subjectsApi.getAll(params);
      const data: PaginatedResponse<Subject> = response.data;
      setSubjects(data.items);
      setPagination({
        page: data.page,
        size: data.size,
        total: data.total,
        pages: data.pages,
      });
    } catch (error) {
      console.error('Failed to fetch subjects:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubjects();
  }, [pagination.page, search, selectedStudy, sortBy, sortOrder]);

  const handleSort = (column: 'name' | 'dob' | 'sex' | 'race') => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
    setPagination({ ...pagination, page: 1 });
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this subject?')) return;
    try {
      await subjectsApi.delete(id);
      fetchSubjects();
    } catch (error) {
      console.error('Failed to delete subject:', error);
    }
  };

  const handleShowDetails = async (id: number) => {
    setLoadingDetails(true);
    setShowDetailsModal(true);
    try {
      const response = await subjectsApi.getById(id);
      setSelectedSubject(response.data);
    } catch (error) {
      console.error('Failed to fetch subject details:', error);
      alert('Failed to load subject details');
      setShowDetailsModal(false);
    } finally {
      setLoadingDetails(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Subjects</h1>
          {selectedStudy && (
            <p className="text-sm text-gray-600 mt-1">
              Filtered by: <span className="font-medium">{selectedStudy.name}</span>
            </p>
          )}
        </div>
        <Link to="/subjects/new">
          <Button className="flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Add Subject</span>
          </Button>
        </Link>
      </div>

      <div className="card mb-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              type="text"
              placeholder="Search by name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : subjects.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No subjects found</p>
        </div>
      ) : (
        <>
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                      onClick={() => handleSort('name')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Name</span>
                        {sortBy === 'name' && (
                          sortOrder === 'asc' ? (
                            <ArrowUp className="w-3 h-3" />
                          ) : (
                            <ArrowDown className="w-3 h-3" />
                          )
                        )}
                      </div>
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                      onClick={() => handleSort('dob')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Date of Birth</span>
                        {sortBy === 'dob' && (
                          sortOrder === 'asc' ? (
                            <ArrowUp className="w-3 h-3" />
                          ) : (
                            <ArrowDown className="w-3 h-3" />
                          )
                        )}
                      </div>
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                      onClick={() => handleSort('sex')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Sex</span>
                        {sortBy === 'sex' && (
                          sortOrder === 'asc' ? (
                            <ArrowUp className="w-3 h-3" />
                          ) : (
                            <ArrowDown className="w-3 h-3" />
                          )
                        )}
                      </div>
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                      onClick={() => handleSort('race')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Race</span>
                        {sortBy === 'race' && (
                          sortOrder === 'asc' ? (
                            <ArrowUp className="w-3 h-3" />
                          ) : (
                            <ArrowDown className="w-3 h-3" />
                          )
                        )}
                      </div>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {subjects.map((subject) => (
                    <tr key={subject.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {subject.last_name}, {subject.first_name}
                          {subject.middle_name && ` ${subject.middle_name}`}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {subject.date_of_birth
                          ? format(new Date(subject.date_of_birth), 'MMM dd, yyyy')
                          : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {subject.sex || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {subject.race || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleShowDetails(subject.id)}
                            className="text-primary-600 hover:text-primary-900"
                            title="Show Details"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <Link
                            to={`/subjects/${subject.id}/edit`}
                            className="text-primary-600 hover:text-primary-900"
                            title="Edit"
                          >
                            <Edit className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleDelete(subject.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {pagination.pages > 1 && (
            <div className="mt-4 flex justify-center space-x-2">
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

      {/* Subject Details Modal */}
      <Modal
        isOpen={showDetailsModal}
        onClose={() => {
          setShowDetailsModal(false);
          setSelectedSubject(null);
        }}
        title="Subject Details"
        size="lg"
      >
        {loadingDetails ? (
          <div className="text-center py-8">Loading...</div>
        ) : selectedSubject ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <p className="text-sm text-gray-900">{selectedSubject.first_name || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Middle Name</label>
                <p className="text-sm text-gray-900">{selectedSubject.middle_name || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                <p className="text-sm text-gray-900">{selectedSubject.last_name || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                <p className="text-sm text-gray-900">
                  {selectedSubject.date_of_birth
                    ? format(new Date(selectedSubject.date_of_birth), 'MMM dd, yyyy')
                    : '-'}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sex</label>
                <p className="text-sm text-gray-900">{selectedSubject.sex || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Race</label>
                <p className="text-sm text-gray-900">{selectedSubject.race || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">SSN</label>
                <p className="text-sm text-gray-900">{selectedSubject.ssn || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">County</label>
                <p className="text-sm text-gray-900">{selectedSubject.county || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Zip</label>
                <p className="text-sm text-gray-900">{selectedSubject.zip || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Death Date</label>
                <p className="text-sm text-gray-900">
                  {selectedSubject.death_date
                    ? format(new Date(selectedSubject.death_date), 'MMM dd, yyyy')
                    : '-'}
                </p>
              </div>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
};

