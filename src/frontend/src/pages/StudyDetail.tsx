import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { studiesApi, subjectsApi, sessionNotesApi, assessmentsApi } from '../api/endpoints';
import { Study, Subject, SessionNote, Assessment, User } from '../types';
import { Button } from '../components/ui/Button';
import { format } from 'date-fns';
import { Edit, Users, FileText, BarChart3, Download, User as UserIcon } from 'lucide-react';

export const StudyDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [study, setStudy] = useState<Study | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [sessionNotes, setSessionNotes] = useState<SessionNote[]>([]);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [principalInvestigator, setPrincipalInvestigator] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      console.log('StudyDetail: id from params:', id);
      if (!id) {
        setError('Study ID is missing');
        setLoading(false);
        return;
      }
      
      setLoading(true);
      setError(null);
      try {
        const studyId = parseInt(id);
        if (isNaN(studyId)) {
          setError('Invalid study ID');
          setLoading(false);
          return;
        }
        console.log('StudyDetail: fetching study with ID:', studyId);

        // Fetch study first - this is critical, so if it fails, we show error
        const studyRes = await studiesApi.getById(studyId);
        setStudy(studyRes.data);

        // Fetch Principal Investigator if assigned
        if (studyRes.data.principal_investigator_id) {
          try {
            const researchersRes = await studiesApi.getResearchers();
            const pi = researchersRes.data.find((r: User) => r.id === studyRes.data.principal_investigator_id);
            if (pi) {
              setPrincipalInvestigator(pi);
            }
          } catch (error) {
            console.error('Failed to fetch Principal Investigator:', error);
          }
        }

        // Fetch all related data with pagination (max 1000 per request)
        // Use Promise.allSettled so one failure doesn't break everything
        const [subjectsResult, notesResult, assessmentsResult] = await Promise.allSettled([
          subjectsApi.getAll({ study_id: studyId, limit: 1000 }),
          sessionNotesApi.getAll({ study_id: studyId, limit: 1000 }),
          assessmentsApi.getAll({ study_id: studyId, limit: 1000 }),
        ]);

        // Handle subjects
        if (subjectsResult.status === 'fulfilled') {
          setSubjects(subjectsResult.value.data.items);
        } else {
          console.error('Failed to fetch subjects:', subjectsResult.reason);
          setSubjects([]);
        }

        // Handle session notes
        if (notesResult.status === 'fulfilled') {
          setSessionNotes(notesResult.value.data.items);
        } else {
          console.error('Failed to fetch session notes:', notesResult.reason);
          setSessionNotes([]);
        }

        // Handle assessments
        if (assessmentsResult.status === 'fulfilled') {
          setAssessments(assessmentsResult.value.data.items);
        } else {
          console.error('Failed to fetch assessments:', assessmentsResult.reason);
          setAssessments([]);
        }
      } catch (error: any) {
        console.error('Failed to fetch study data:', error);
        console.error('Error response:', error.response);
        console.error('Error response data:', error.response?.data);
        let errorMessage = 'Failed to load study data. Please try again.';
        
        if (error.response?.status === 404) {
          errorMessage = 'Study not found. It may have been deleted or you may not have access to it.';
        } else if (error.response?.status === 403) {
          errorMessage = 'You do not have permission to view this study.';
        } else if (error.response?.data) {
          // Handle different error response formats
          const errorData = error.response.data;
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            // Handle validation errors array
            errorMessage = errorData.detail.map((err: any) => {
              if (typeof err === 'string') return err;
              if (err.msg) return err.msg;
              return JSON.stringify(err);
            }).join(', ');
          } else if (typeof errorData.detail === 'object') {
            errorMessage = errorData.detail.msg || JSON.stringify(errorData.detail);
          } else if (typeof errorData === 'string') {
            errorMessage = errorData;
          }
        } else if (error.message) {
          errorMessage = String(error.message);
        }
        
        // Ensure errorMessage is always a string
        setError(String(errorMessage));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  if (error || !study) {
    // Ensure error is always a string
    const errorMessage = typeof error === 'string' ? error : 
                        error ? String(error) : 
                        'The study you are looking for does not exist.';
    
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card text-center py-12">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Study Not Found</h2>
          <p className="text-gray-600 mb-4">{errorMessage}</p>
          <Link to="/studies">
            <Button variant="secondary">Back to Studies</Button>
          </Link>
        </div>
      </div>
    );
  }

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

  const downloadJSON = () => {
    if (!study) return;

    const studyData = {
      study: {
        id: study.id,
        name: study.name,
        description: study.description,
        start_date: study.start_date,
        end_date: study.end_date,
        status: study.status,
        principal_investigator_id: study.principal_investigator_id,
        created_at: study.created_at,
        updated_at: study.updated_at,
      },
      subjects: subjects.map(subject => ({
        id: subject.id,
        first_name: subject.first_name,
        middle_name: subject.middle_name,
        last_name: subject.last_name,
        date_of_birth: subject.date_of_birth,
        sex: subject.sex,
        ssn: subject.ssn,
        race: subject.race,
        death_date: subject.death_date,
        county: subject.county,
        zip: subject.zip,
        created_at: subject.created_at,
        updated_at: subject.updated_at,
      })),
      session_notes: sessionNotes.map(note => ({
        id: note.id,
        subject_id: note.subject_id,
        session_date: note.session_date,
        notes: note.notes,
        created_at: note.created_at,
        updated_at: note.updated_at,
        created_by: note.created_by,
      })),
      assessments: assessments.map(assessment => ({
        id: assessment.id,
        subject_id: assessment.subject_id,
        study_id: assessment.study_id,
        assessment_type: assessment.assessment_type,
        assessment_date: assessment.assessment_date,
        total_score: assessment.total_score,
        notes: assessment.notes,
        data: assessment.data,
        created_at: assessment.created_at,
        updated_at: assessment.updated_at,
        created_by: assessment.created_by,
      })),
      export_date: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(studyData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${study.name.replace(/[^a-z0-9]/gi, '_')}_${format(new Date(), 'yyyy-MM-dd')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadCSV = () => {
    if (!study) return;

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
    let csvContent = `Study: ${study.name}\n`;
    csvContent += `Description: ${study.description || ''}\n`;
    csvContent += `Status: ${study.status}\n`;
    csvContent += `Start Date: ${study.start_date || ''}\n`;
    csvContent += `End Date: ${study.end_date || ''}\n`;
    csvContent += `\n`;

    // Subjects CSV
    csvContent += `=== SUBJECTS ===\n`;
    csvContent += `ID,First Name,Middle Name,Last Name,Date of Birth,Sex,SSN,Race,Death Date,County,Zip\n`;
    subjects.forEach(subject => {
      csvContent += `${subject.id},${escapeCSV(subject.first_name)},${escapeCSV(subject.middle_name)},${escapeCSV(subject.last_name)},${escapeCSV(subject.date_of_birth)},${escapeCSV(subject.sex)},${escapeCSV(subject.ssn)},${escapeCSV(subject.race)},${escapeCSV(subject.death_date)},${escapeCSV(subject.county)},${escapeCSV(subject.zip)}\n`;
    });
    csvContent += `\n`;

    // Session Notes CSV
    csvContent += `=== SESSION NOTES ===\n`;
    csvContent += `ID,Subject ID,Session Date,Notes\n`;
    sessionNotes.forEach(note => {
      csvContent += `${note.id},${note.subject_id},${escapeCSV(note.session_date)},${escapeCSV(note.notes)}\n`;
    });
    csvContent += `\n`;

    // Assessments CSV
    csvContent += `=== ASSESSMENTS ===\n`;
    csvContent += `ID,Subject ID,Study ID,Assessment Type,Assessment Date,Total Score,Notes,Additional Data\n`;
    assessments.forEach(assessment => {
      const additionalData = assessment.data ? JSON.stringify(assessment.data) : '';
      csvContent += `${assessment.id},${assessment.subject_id},${escapeCSV(assessment.study_id)},${escapeCSV(assessment.assessment_type)},${escapeCSV(assessment.assessment_date)},${escapeCSV(assessment.total_score)},${escapeCSV(assessment.notes)},${escapeCSV(additionalData)}\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${study.name.replace(/[^a-z0-9]/gi, '_')}_${format(new Date(), 'yyyy-MM-dd')}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{study.name}</h1>
          <span className={`mt-2 inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(study.status)}`}>
            {study.status}
          </span>
        </div>
        <div className="flex space-x-2">
          <div className="relative">
            <Button 
              variant="secondary" 
              className="flex items-center space-x-2"
              onClick={() => setShowDownloadMenu(!showDownloadMenu)}
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
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
                  <button
                    onClick={() => {
                      downloadJSON();
                      setShowDownloadMenu(false);
                    }}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-t-lg"
                  >
                    Download as JSON
                  </button>
                  <button
                    onClick={() => {
                      downloadCSV();
                      setShowDownloadMenu(false);
                    }}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-b-lg"
                  >
                    Download as CSV
                  </button>
                </div>
              </>
            )}
          </div>
          <Link to={`/studies/${study.id}/edit`}>
            <Button className="flex items-center space-x-2">
              <Edit className="w-4 h-4" />
              <span>Edit Study</span>
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center mb-2">
            <Users className="w-5 h-5 text-primary-600 mr-2" />
            <h3 className="text-lg font-semibold">Subjects</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900">{subjects.length}</p>
        </div>

        <div className="card">
          <div className="flex items-center mb-2">
            <FileText className="w-5 h-5 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold">Session Notes</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900">{sessionNotes.length}</p>
        </div>

        <div className="card">
          <div className="flex items-center mb-2">
            <BarChart3 className="w-5 h-5 text-purple-600 mr-2" />
            <h3 className="text-lg font-semibold">Assessments</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900">{assessments.length}</p>
        </div>
      </div>

      {study.description && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Description</h2>
          <p className="text-gray-700">{study.description}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Study Dates</h3>
          <div className="space-y-2 text-sm">
            {study.start_date && (
              <p>
                <span className="font-medium">Start:</span>{' '}
                {format(new Date(study.start_date), 'MMMM dd, yyyy')}
              </p>
            )}
            {study.end_date && (
              <p>
                <span className="font-medium">End:</span>{' '}
                {format(new Date(study.end_date), 'MMMM dd, yyyy')}
              </p>
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Principal Investigator</h3>
          {principalInvestigator ? (
            <div className="flex items-center space-x-3">
              <UserIcon className="w-5 h-5 text-primary-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">{principalInvestigator.full_name || principalInvestigator.email}</p>
                <p className="text-xs text-gray-500">{principalInvestigator.email}</p>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-500">No Principal Investigator assigned</p>
          )}
        </div>
      </div>

      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Subjects in this Study</h2>
          <Link to="/subjects">
            <Button variant="secondary" className="text-sm">
              View All Subjects
            </Button>
          </Link>
        </div>
        {subjects.length === 0 ? (
          <p className="text-gray-500">No subjects in this study</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">DOB</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sex</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {subjects.slice(0, 10).map((subject) => (
                  <tr key={subject.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {subject.last_name}, {subject.first_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {subject.date_of_birth ? format(new Date(subject.date_of_birth), 'MMM dd, yyyy') : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {subject.sex || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {subjects.length > 10 && (
              <p className="mt-4 text-sm text-gray-500 text-center">
                Showing 10 of {subjects.length} subjects
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};


