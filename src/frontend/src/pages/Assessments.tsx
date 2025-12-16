import React, { useEffect, useState } from 'react';
import { assessmentsApi, subjectsApi, studiesApi } from '../api/endpoints';
import { Assessment, PaginatedResponse, Subject, Study } from '../types';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Plus, Edit, Trash2, Eye, Download, ArrowUp, ArrowDown } from 'lucide-react';
import { format } from 'date-fns';
import { Link, useSearchParams } from 'react-router-dom';
import { useStudyStore } from '../store/studyStore';

const ASSESSMENT_TYPE_NAMES: Record<string, string> = {
  moca: 'MoCA',
  nihcog: 'NIH Toolbox',
  dass21: 'DASS-21',
  pssqi: 'PSSQI',
  vision: 'Vision Acuity',
  balance: 'Balance Test',
};

const ASSESSMENT_TYPE_COLORS: Record<string, string> = {
  moca: 'bg-blue-100 text-blue-800',
  nihcog: 'bg-purple-100 text-purple-800',
  dass21: 'bg-red-100 text-red-800',
  pssqi: 'bg-indigo-100 text-indigo-800',
  vision: 'bg-green-100 text-green-800',
  balance: 'bg-yellow-100 text-yellow-800',
};

export const Assessments: React.FC = () => {
  const { selectedStudy } = useStudyStore();
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [studies, setStudies] = useState<Study[]>([]);
  const [assessmentTypes, setAssessmentTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [selectedAssessment, setSelectedAssessment] = useState<Assessment | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const [sortBy, setSortBy] = useState<'subject' | 'date' | null>(null);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [pagination, setPagination] = useState({
    page: 1,
    size: 20,
    total: 0,
    pages: 0,
  });

  useEffect(() => {
    const subjectId = searchParams.get('subject_id');
    const type = searchParams.get('type');
    if (subjectId) {
      setSelectedSubjectId(parseInt(subjectId));
    }
    if (type) {
      setSelectedType(type);
    }
  }, [searchParams]);

  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        const response = await subjectsApi.getAll({ limit: 1000 });
        setSubjects(response.data.items);
      } catch (error) {
        console.error('Failed to fetch subjects:', error);
      }
    };
    const fetchStudies = async () => {
      try {
        const response = await studiesApi.getAll({ limit: 1000 });
        setStudies(response.data.items);
      } catch (error) {
        console.error('Failed to fetch studies:', error);
      }
    };
    fetchSubjects();
    fetchStudies();
  }, []);

  useEffect(() => {
    const fetchTypes = async () => {
      try {
        const response = await assessmentsApi.getTypes();
        setAssessmentTypes(response.data);
      } catch (error) {
        console.error('Failed to fetch assessment types:', error);
      }
    };
    fetchTypes();
  }, []);

  const fetchAssessments = async () => {
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
      if (selectedType) {
        params.assessment_type = selectedType;
      }
      if (sortBy) {
        params.sort_by = sortBy;
        params.sort_order = sortOrder;
      }
      
      const response = await assessmentsApi.getAll(params);
      const data: PaginatedResponse<Assessment> = response.data;
      setAssessments(data.items);
      setPagination({
        page: data.page,
        size: data.size,
        total: data.total,
        pages: data.pages,
      });
    } catch (error) {
      console.error('Failed to fetch assessments:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssessments();
  }, [pagination.page, selectedSubjectId, selectedType, selectedStudy, sortBy, sortOrder]);


  const handleSort = (column: 'subject' | 'date') => {
    if (sortBy === column) {
      // Toggle sort order if clicking the same column
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // Set new column and default to descending
      setSortBy(column);
      setSortOrder('desc');
    }
    setPagination({ ...pagination, page: 1 }); // Reset to first page when sorting
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this assessment?')) return;
    try {
      await assessmentsApi.delete(id);
      fetchAssessments();
    } catch (error) {
      console.error('Failed to delete assessment:', error);
    }
  };

  const handleShowDetails = async (id: number) => {
    setLoadingDetails(true);
    setShowDetailsModal(true);
    try {
      const response = await assessmentsApi.getById(id);
      setSelectedAssessment(response.data);
    } catch (error) {
      console.error('Failed to fetch assessment details:', error);
      alert('Failed to load assessment details');
      setShowDetailsModal(false);
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleFilter = (subjectId: number | null, type: string | null) => {
    setSelectedSubjectId(subjectId);
    setSelectedType(type);
    setPagination({ ...pagination, page: 1 });
    const params: any = {};
    if (subjectId) params.subject_id = subjectId.toString();
    if (type) params.type = type;
    setSearchParams(params);
  };

  const downloadJSON = async () => {
    try {
      console.log('Starting JSON download...');
      // Fetch all assessments matching current filters (not paginated)
      const params: any = {
        limit: 1000, // Backend max limit
        skip: 0,
      };
      if (selectedSubjectId) {
        params.subject_id = selectedSubjectId;
      }
      if (selectedStudy) {
        params.study_id = selectedStudy.id;
      }
      if (selectedType) {
        params.assessment_type = selectedType;
      }

      // Fetch all pages if needed
      let allAssessments: Assessment[] = [];
      let hasMore = true;
      let skip = 0;
      
      while (hasMore) {
        params.skip = skip;
        const response = await assessmentsApi.getAll(params);
        const data: PaginatedResponse<Assessment> = response.data;
        allAssessments = [...allAssessments, ...data.items];
        
        if (data.items.length < params.limit || allAssessments.length >= data.total) {
          hasMore = false;
        } else {
          skip += params.limit;
        }
      }

      // Enrich with subject names
      const enrichedData = allAssessments.map(assessment => {
        const subject = subjects.find(s => s.id === assessment.subject_id);
        const study = studies.find(s => s.id === assessment.study_id);
        return {
          id: assessment.id,
          subject_id: assessment.subject_id,
          subject_name: subject ? `${subject.last_name}, ${subject.first_name}` : null,
          study_id: assessment.study_id,
          study_name: study ? study.name : null,
          assessment_type: assessment.assessment_type,
          assessment_type_display: ASSESSMENT_TYPE_NAMES[assessment.assessment_type] || assessment.assessment_type,
          assessment_date: assessment.assessment_date,
          total_score: assessment.total_score,
          notes: assessment.notes,
          data: assessment.data,
          created_at: assessment.created_at,
          updated_at: assessment.updated_at,
        };
      });

      const dataStr = JSON.stringify(enrichedData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const a = document.createElement('a');
      a.href = url;
      const filename = `assessments_${format(new Date(), 'yyyy-MM-dd')}.json`;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      console.log(`Downloaded ${allAssessments.length} assessments as JSON`);
    } catch (error) {
      console.error('Failed to export assessments:', error);
      alert(`Failed to export assessments: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const downloadCSV = async () => {
    try {
      console.log('Starting CSV download...');
      // Fetch all assessments matching current filters (not paginated)
      const params: any = {
        limit: 1000, // Backend max limit
        skip: 0,
      };
      if (selectedSubjectId) {
        params.subject_id = selectedSubjectId;
      }
      if (selectedStudy) {
        params.study_id = selectedStudy.id;
      }
      if (selectedType) {
        params.assessment_type = selectedType;
      }

      // Fetch all pages if needed
      let allAssessments: Assessment[] = [];
      let hasMore = true;
      let skip = 0;
      
      while (hasMore) {
        params.skip = skip;
        const response = await assessmentsApi.getAll(params);
        const data: PaginatedResponse<Assessment> = response.data;
        allAssessments = [...allAssessments, ...data.items];
        
        if (data.items.length < params.limit || allAssessments.length >= data.total) {
          hasMore = false;
        } else {
          skip += params.limit;
        }
      }

      // Helper function to escape CSV values
      const escapeCSV = (value: any): string => {
        if (value === null || value === undefined) return '';
        const str = String(value);
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
          return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
      };

      // Create CSV content
      let csvContent = 'ID,Subject ID,Subject Name,Study ID,Study Name,Assessment Type,Assessment Type Display,Assessment Date,Total Score,Notes,Additional Data,Created At,Updated At\n';
      
      allAssessments.forEach(assessment => {
        const subject = subjects.find(s => s.id === assessment.subject_id);
        const study = studies.find(s => s.id === assessment.study_id);
        const subjectName = subject ? `${subject.last_name}, ${subject.first_name}` : '';
        const studyName = study ? study.name : '';
        const assessmentTypeDisplay = ASSESSMENT_TYPE_NAMES[assessment.assessment_type] || assessment.assessment_type;
        const additionalData = assessment.data ? JSON.stringify(assessment.data) : '';
        
        csvContent += `${assessment.id},${assessment.subject_id},${escapeCSV(subjectName)},${assessment.study_id || ''},${escapeCSV(studyName)},${escapeCSV(assessment.assessment_type)},${escapeCSV(assessmentTypeDisplay)},${escapeCSV(assessment.assessment_date)},${assessment.total_score || ''},${escapeCSV(assessment.notes)},${escapeCSV(additionalData)},${escapeCSV(assessment.created_at)},${escapeCSV(assessment.updated_at)}\n`;
      });

      const dataBlob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(dataBlob);
      const a = document.createElement('a');
      a.href = url;
      const filename = `assessments_${format(new Date(), 'yyyy-MM-dd')}.csv`;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      console.log(`Downloaded ${allAssessments.length} assessments as CSV`);
    } catch (error) {
      console.error('Failed to export assessments:', error);
      alert(`Failed to export assessments: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Assessments</h1>
          {selectedStudy && (
            <p className="text-sm text-gray-600 mt-1">
              Filtered by: <span className="font-medium">{selectedStudy.name}</span>
            </p>
          )}
        </div>
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Button
              variant="secondary"
              onClick={() => setShowDownloadMenu(!showDownloadMenu)}
              className="flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </Button>
            {showDownloadMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowDownloadMenu(false)}
                />
                <div 
                  className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-20 border border-gray-200"
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      downloadCSV();
                      setShowDownloadMenu(false);
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Download as CSV
                  </button>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      downloadJSON();
                      setShowDownloadMenu(false);
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Download as JSON
                  </button>
                </div>
              </>
            )}
          </div>
          <Link to="/assessments/new">
            <Button className="flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Add Assessment</span>
            </Button>
          </Link>
        </div>
      </div>

      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Subject
            </label>
            <select
              className="input"
              value={selectedSubjectId || ''}
              onChange={(e) => handleFilter(e.target.value ? parseInt(e.target.value) : null, selectedType)}
            >
              <option value="">All Subjects</option>
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.last_name}, {subject.first_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Assessment Type
            </label>
            <select
              className="input"
              value={selectedType || ''}
              onChange={(e) => handleFilter(selectedSubjectId, e.target.value || null)}
            >
              <option value="">All Types</option>
              {assessmentTypes.map((type) => (
                <option key={type} value={type}>
                  {ASSESSMENT_TYPE_NAMES[type] || type}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : assessments.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No assessments found</p>
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
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                      onClick={() => handleSort('date')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Date</span>
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
                  {assessments.map((assessment) => {
                    const subject = subjects.find(s => s.id === assessment.subject_id);
                    return (
                      <tr key={assessment.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {subject ? `${subject.last_name}, ${subject.first_name}` : `Subject #${assessment.subject_id}`}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${ASSESSMENT_TYPE_COLORS[assessment.assessment_type] || 'bg-gray-100 text-gray-800'}`}>
                            {ASSESSMENT_TYPE_NAMES[assessment.assessment_type] || assessment.assessment_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {format(new Date(assessment.assessment_date), 'MMM dd, yyyy')}
                          {assessment.assessment_time && (
                            <span className="ml-1 text-gray-400">
                              {new Date(`2000-01-01T${assessment.assessment_time}`).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          <div className="max-w-md truncate">
                            {assessment.notes || <span className="text-gray-400">No notes</span>}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleShowDetails(assessment.id)}
                              className="text-primary-600 hover:text-primary-900"
                              title="Show Details"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <Link
                              to={`/assessments/${assessment.id}/edit`}
                              className="text-primary-600 hover:text-primary-900"
                              title="Edit"
                            >
                              <Edit className="w-4 h-4" />
                            </Link>
                            <button
                              onClick={() => handleDelete(assessment.id)}
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

      {/* Assessment Details Modal */}
      <Modal
        isOpen={showDetailsModal}
        onClose={() => {
          setShowDetailsModal(false);
          setSelectedAssessment(null);
        }}
        title="Assessment Details"
        size="lg"
      >
        {loadingDetails ? (
          <div className="text-center py-8">Loading...</div>
        ) : selectedAssessment ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                <p className="text-sm text-gray-900">
                  {(() => {
                    const subject = subjects.find(s => s.id === selectedAssessment.subject_id);
                    return subject ? `${subject.last_name}, ${subject.first_name}` : `Subject #${selectedAssessment.subject_id}`;
                  })()}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Study</label>
                <p className="text-sm text-gray-900">
                  {selectedAssessment.study_id
                    ? (() => {
                        const study = studies.find(s => s.id === selectedAssessment.study_id);
                        return study ? study.name : `Study #${selectedAssessment.study_id}`;
                      })()
                    : '-'}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Assessment Type</label>
                <p className="text-sm text-gray-900">
                  {ASSESSMENT_TYPE_NAMES[selectedAssessment.assessment_type] || selectedAssessment.assessment_type}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Assessment Date</label>
                <p className="text-sm text-gray-900">
                  {format(new Date(selectedAssessment.assessment_date), 'MMM dd, yyyy')}
                  {selectedAssessment.assessment_time && (
                    <span className="ml-2 text-gray-600">
                      at {new Date(`2000-01-01T${selectedAssessment.assessment_time}`).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  )}
                </p>
              </div>
              {selectedAssessment.total_score !== null && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Total Score</label>
                  <p className="text-sm text-gray-900 font-semibold">{selectedAssessment.total_score.toFixed(1)}</p>
                </div>
              )}
            </div>
            {selectedAssessment.notes && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <p className="text-sm text-gray-900 whitespace-pre-wrap">{selectedAssessment.notes}</p>
              </div>
            )}
            {selectedAssessment.data && typeof selectedAssessment.data === 'object' && Object.keys(selectedAssessment.data).length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Additional Data</label>
                <div className="bg-gray-50 rounded-lg p-4">
                  <pre className="text-sm text-gray-900 whitespace-pre-wrap">
                    {JSON.stringify(selectedAssessment.data, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        ) : null}
      </Modal>
    </div>
  );
};

