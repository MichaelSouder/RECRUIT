import React, { useEffect, useState } from 'react';
import { sessionNotesApi, subjectsApi } from '../api/endpoints';
import { SessionNote, PaginatedResponse, Subject } from '../types';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Plus, Edit, Trash2, Calendar, Eye, ArrowUp, ArrowDown } from 'lucide-react';
import { format } from 'date-fns';
import { Link, useSearchParams } from 'react-router-dom';
import { useStudyStore } from '../store/studyStore';

export const SessionNotes: React.FC = () => {
  const { selectedStudy } = useStudyStore();
  const [notes, setNotes] = useState<SessionNote[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [selectedNote, setSelectedNote] = useState<SessionNote | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [sortBy, setSortBy] = useState<'subject' | 'date' | null>(null);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [searchParams, setSearchParams] = useSearchParams();
  const [pagination, setPagination] = useState({
    page: 1,
    size: 20,
    total: 0,
    pages: 0,
  });

  useEffect(() => {
    const subjectId = searchParams.get('subject_id');
    if (subjectId) {
      setSelectedSubjectId(parseInt(subjectId));
    }
  }, [searchParams]);

  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        const params: any = { limit: 1000 };
        if (selectedStudy) {
          params.study_id = selectedStudy.id;
        }
        const response = await subjectsApi.getAll(params);
        setSubjects(response.data.items);
        
        // Clear selected subject if it's no longer in the filtered list
        if (selectedSubjectId && !response.data.items.find((s: Subject) => s.id === selectedSubjectId)) {
          setSelectedSubjectId(null);
          setSearchParams({});
        }
      } catch (error) {
        console.error('Failed to fetch subjects:', error);
      }
    };
    fetchSubjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedStudy]);

  const fetchNotes = async () => {
    setLoading(true);
    try {
      const params: any = {
        skip: (pagination.page - 1) * pagination.size,
        limit: pagination.size,
      };
      if (selectedSubjectId) {
        params.subject_id = selectedSubjectId;
      }
      if (selectedStudy) {
        params.study_id = selectedStudy.id;
      }
      if (sortBy) {
        params.sort_by = sortBy;
        params.sort_order = sortOrder;
      }
      
      const response = await sessionNotesApi.getAll(params);
      const data: PaginatedResponse<SessionNote> = response.data;
      setNotes(data.items);
      setPagination({
        page: data.page,
        size: data.size,
        total: data.total,
        pages: data.pages,
      });
    } catch (error) {
      console.error('Failed to fetch session notes:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, [pagination.page, selectedSubjectId, selectedStudy, sortBy, sortOrder]);

  const handleSort = (column: 'subject' | 'date') => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
    setPagination({ ...pagination, page: 1 });
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this session note?')) return;
    try {
      await sessionNotesApi.delete(id);
      fetchNotes();
    } catch (error) {
      console.error('Failed to delete session note:', error);
    }
  };

  const handleShowDetails = async (id: number) => {
    setLoadingDetails(true);
    setShowDetailsModal(true);
    try {
      const response = await sessionNotesApi.getById(id);
      setSelectedNote(response.data);
    } catch (error) {
      console.error('Failed to fetch session note details:', error);
      alert('Failed to load session note details');
      setShowDetailsModal(false);
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleSubjectFilter = (subjectId: number | null) => {
    setSelectedSubjectId(subjectId);
    setPagination({ ...pagination, page: 1 });
    if (subjectId) {
      setSearchParams({ subject_id: subjectId.toString() });
    } else {
      setSearchParams({});
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Session Notes</h1>
          {selectedStudy && (
            <p className="text-sm text-gray-600 mt-1">
              Filtered by: <span className="font-medium">{selectedStudy.name}</span>
            </p>
          )}
        </div>
        <Link to="/session-notes/new">
          <Button className="flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Add Session Note</span>
          </Button>
        </Link>
      </div>

      <div className="card mb-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Subject
            </label>
            <select
              className="input"
              value={selectedSubjectId || ''}
              onChange={(e) => handleSubjectFilter(e.target.value ? parseInt(e.target.value) : null)}
            >
              <option value="">All Subjects</option>
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.last_name}, {subject.first_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : notes.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No session notes found</p>
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
                      onClick={() => handleSort('subject')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Subject</span>
                        {sortBy === 'subject' && (
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
                      onClick={() => handleSort('date')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Session Date</span>
                        {sortBy === 'date' && (
                          sortOrder === 'asc' ? (
                            <ArrowUp className="w-3 h-3" />
                          ) : (
                            <ArrowDown className="w-3 h-3" />
                          )
                        )}
                      </div>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Notes
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {notes.map((note) => {
                    const subject = subjects.find(s => s.id === note.subject_id);
                    return (
                      <tr key={note.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {subject ? `${subject.last_name}, ${subject.first_name}` : `Subject #${note.subject_id}`}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div className="flex items-center">
                            <Calendar className="w-4 h-4 mr-2" />
                            {format(new Date(note.session_date), 'MMM dd, yyyy')}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          <div className="max-w-md truncate">
                            {note.notes || <span className="text-gray-400">No notes</span>}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleShowDetails(note.id)}
                              className="text-primary-600 hover:text-primary-900"
                              title="Show Details"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <Link
                              to={`/session-notes/${note.id}/edit`}
                              className="text-primary-600 hover:text-primary-900"
                              title="Edit"
                            >
                              <Edit className="w-4 h-4" />
                            </Link>
                            <button
                              onClick={() => handleDelete(note.id)}
                              className="text-red-600 hover:text-red-900"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
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
                Page {pagination.page} of {pagination.pages} ({pagination.total} total)
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

      {/* Session Note Details Modal */}
      <Modal
        isOpen={showDetailsModal}
        onClose={() => {
          setShowDetailsModal(false);
          setSelectedNote(null);
        }}
        title="Session Note Details"
        size="lg"
      >
        {loadingDetails ? (
          <div className="text-center py-8">Loading...</div>
        ) : selectedNote ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                <p className="text-sm text-gray-900">
                  {(() => {
                    const subject = subjects.find(s => s.id === selectedNote.subject_id);
                    return subject ? `${subject.last_name}, ${subject.first_name}` : `Subject #${selectedNote.subject_id}`;
                  })()}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Session Date</label>
                <p className="text-sm text-gray-900">
                  {format(new Date(selectedNote.session_date), 'MMM dd, yyyy')}
                </p>
              </div>
            </div>
            {selectedNote.notes && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <p className="text-sm text-gray-900 whitespace-pre-wrap">{selectedNote.notes}</p>
              </div>
            )}
          </div>
        ) : null}
      </Modal>
    </div>
  );
};

