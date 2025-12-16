import React, { useEffect, useState, useMemo } from 'react';
import { assessmentsApi, subjectsApi } from '../api/endpoints';
import { Assessment, PaginatedResponse, Subject } from '../types';
import { Modal } from '../components/ui/Modal';
import { useStudyStore } from '../store/studyStore';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';

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

const localizer = momentLocalizer(moment);

export const CalendarPage: React.FC = () => {
  const { selectedStudy } = useStudyStore();
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [selectedAssessment, setSelectedAssessment] = useState<Assessment | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        const params: any = { limit: 1000 };
        if (selectedStudy) {
          params.study_id = selectedStudy.id;
        }
        const response = await subjectsApi.getAll(params);
        setSubjects(response.data.items);
      } catch (error) {
        console.error('Failed to fetch subjects:', error);
      }
    };
    fetchSubjects();
  }, [selectedStudy]);

  const fetchCalendarAssessments = async () => {
    setLoading(true);
    try {
      const params: any = {
        limit: 1000,
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

      setAssessments(allAssessments);
    } catch (error) {
      console.error('Failed to fetch calendar assessments:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCalendarAssessments();
  }, [selectedSubjectId, selectedType, selectedStudy]);

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

  const calendarEvents = useMemo(() => {
    return assessments.map((assessment) => {
      const subject = subjects.find(s => s.id === assessment.subject_id);
      const subjectName = subject 
        ? `${subject.last_name}, ${subject.first_name}`
        : `Subject #${assessment.subject_id}`;
      const typeName = ASSESSMENT_TYPE_NAMES[assessment.assessment_type] || assessment.assessment_type;
      
      return {
        id: assessment.id,
        title: `${typeName} - ${subjectName}`,
        start: new Date(assessment.assessment_date),
        end: new Date(assessment.assessment_date),
        resource: assessment,
      };
    });
  }, [assessments, subjects]);

  // Get unique assessment types from assessments
  const availableTypes = useMemo(() => {
    const types = new Set(assessments.map(a => a.assessment_type));
    return Array.from(types).sort();
  }, [assessments]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Assessment Calendar</h1>
            {selectedStudy && (
              <p className="text-sm text-gray-600 mt-1">
                Filtered by: <span className="font-medium">{selectedStudy.name}</span>
              </p>
            )}
          </div>
        </div>

        {/* Filters */}
        <div className="card">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Subject
              </label>
              <select
                className="input"
                value={selectedSubjectId || ''}
                onChange={(e) => setSelectedSubjectId(e.target.value ? parseInt(e.target.value) : null)}
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
                onChange={(e) => setSelectedType(e.target.value || null)}
              >
                <option value="">All Types</option>
                {availableTypes.map((type) => (
                  <option key={type} value={type}>
                    {ASSESSMENT_TYPE_NAMES[type] || type}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Calendar View */}
        <div className="card p-0 overflow-hidden">
          {loading ? (
            <div className="text-center py-12">Loading calendar...</div>
          ) : assessments.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No assessments found</p>
            </div>
          ) : (
            <div className="p-4" style={{ height: '600px' }}>
              <Calendar
                localizer={localizer}
                events={calendarEvents}
                startAccessor="start"
                endAccessor="end"
                style={{ height: '100%' }}
                onSelectEvent={(event: any) => {
                  if (event.resource) {
                    handleShowDetails((event.resource as Assessment).id);
                  }
                }}
                eventPropGetter={(event: any) => {
                  const assessment = (event.resource as Assessment);
                  if (!assessment) {
                    return { className: 'bg-gray-100 text-gray-800' };
                  }
                  const typeColor = ASSESSMENT_TYPE_COLORS[assessment.assessment_type] || 'bg-gray-100 text-gray-800';
                  const [bgColor, textColor] = typeColor.split(' ');
                  
                  // Get border color based on assessment type
                  const borderColorMap: Record<string, string> = {
                    'bg-blue-100': '#3b82f6',
                    'bg-purple-100': '#9333ea',
                    'bg-red-100': '#ef4444',
                    'bg-indigo-100': '#6366f1',
                    'bg-green-100': '#10b981',
                    'bg-yellow-100': '#eab308',
                  };
                  
                  return {
                    className: `${bgColor} ${textColor} border-l-4 cursor-pointer hover:opacity-80`,
                    style: {
                      borderLeftColor: borderColorMap[bgColor] || '#6b7280',
                    },
                  };
                }}
                views={['month', 'week', 'day', 'agenda']}
                defaultView="month"
                popup
                showMultiDayTimes
              />
            </div>
          )}
        </div>

        {/* Assessment Details Modal */}
        {showDetailsModal && selectedAssessment && (
          <Modal
            isOpen={showDetailsModal}
            onClose={() => {
              setShowDetailsModal(false);
              setSelectedAssessment(null);
            }}
            title="Assessment Details"
          >
            {loadingDetails ? (
              <div className="text-center py-8">Loading...</div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Subject</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {(() => {
                      const subject = subjects.find(s => s.id === selectedAssessment.subject_id);
                      return subject 
                        ? `${subject.last_name}, ${subject.first_name}`
                        : `Subject #${selectedAssessment.subject_id}`;
                    })()}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Assessment Type</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {ASSESSMENT_TYPE_NAMES[selectedAssessment.assessment_type] || selectedAssessment.assessment_type}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Date</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {new Date(selectedAssessment.assessment_date).toLocaleDateString()}
                    {selectedAssessment.assessment_time && (
                      <span className="ml-2 text-gray-600">
                        at {new Date(`2000-01-01T${selectedAssessment.assessment_time}`).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    )}
                  </p>
                </div>
                {selectedAssessment.notes && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Notes</label>
                    <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">
                      {selectedAssessment.notes}
                    </p>
                  </div>
                )}
              </div>
            )}
          </Modal>
        )}
      </div>
    </div>
  );
};

