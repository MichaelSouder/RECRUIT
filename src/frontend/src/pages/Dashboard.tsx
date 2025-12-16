import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, BookOpen, TrendingUp, FileText, ClipboardList } from 'lucide-react';
import { subjectsApi, studiesApi, assessmentsApi, sessionNotesApi } from '../api/endpoints';
import { useStudyStore } from '../store/studyStore';
import { Subject, Assessment } from '../types';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export const Dashboard: React.FC = () => {
  const { selectedStudy } = useStudyStore();
  const [stats, setStats] = useState({
    subjects: 0,
    studies: 0,
    activeStudies: 0,
    assessments: 0,
    sessionNotes: 0,
    loading: true,
  });
  const [demographicsData, setDemographicsData] = useState<{
    gender: { name: string; value: number }[];
    race: { name: string; value: number }[];
    ageGroups: { name: string; value: number }[];
  } | null>(null);
  const [assessmentTypesData, setAssessmentTypesData] = useState<{ name: string; value: number }[]>([]);
  const [enrollmentStats, setEnrollmentStats] = useState<{ enrolled: number; notEnrolled: number } | null>(null);
  const [chartsLoading, setChartsLoading] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      setStats(prev => ({ ...prev, loading: true }));
      try {
        if (selectedStudy) {
          // Fetch data for selected study only
          const [subjectsRes, assessmentsRes, notesRes] = await Promise.all([
            subjectsApi.getAll({ limit: 1, study_id: selectedStudy.id }),
            assessmentsApi.getAll({ limit: 1, study_id: selectedStudy.id }),
            sessionNotesApi.getAll({ limit: 1, study_id: selectedStudy.id }),
          ]);
          
          setStats({
            subjects: subjectsRes.data.total,
            studies: 1, // Only showing one study
            activeStudies: selectedStudy.status === 'active' ? 1 : 0,
            assessments: assessmentsRes.data.total,
            sessionNotes: notesRes.data.total,
            loading: false,
          });
        } else {
          // Fetch summary data across all studies
          const [subjectsRes, studiesRes, assessmentsRes, notesRes] = await Promise.all([
          subjectsApi.getAll({ limit: 1 }),
          studiesApi.getAll({ limit: 1000 }),
            assessmentsApi.getAll({ limit: 1 }),
            sessionNotesApi.getAll({ limit: 1 }),
        ]);
        
        const subjectsTotal = subjectsRes.data.total;
        const studiesTotal = studiesRes.data.total;
        const activeStudies = studiesRes.data.items.filter(
          (s: any) => s.status === 'active'
        ).length;

        setStats({
          subjects: subjectsTotal,
          studies: studiesTotal,
          activeStudies,
            assessments: assessmentsRes.data.total,
            sessionNotes: notesRes.data.total,
          loading: false,
        });
        }
      } catch (error) {
        console.error('Failed to fetch stats:', error);
        setStats(prev => ({ ...prev, loading: false }));
      }
    };

    fetchStats();
  }, [selectedStudy]);

  useEffect(() => {
    const fetchChartData = async () => {
      if (!selectedStudy) {
        setDemographicsData(null);
        setAssessmentTypesData([]);
        setEnrollmentStats(null);
        return;
      }

      setChartsLoading(true);
      try {
        // Fetch all subjects and assessments for the study
        const [subjectsRes, assessmentsRes] = await Promise.all([
          subjectsApi.getAll({ limit: 1000, study_id: selectedStudy.id }),
          assessmentsApi.getAll({ limit: 1000, study_id: selectedStudy.id }),
        ]);

        const subjects: Subject[] = subjectsRes.data.items;
        const assessments: Assessment[] = assessmentsRes.data.items;

        // Process demographics data
        const genderCount: Record<string, number> = {};
        const raceCount: Record<string, number> = {};
        const ageGroups: Record<string, number> = {
          '0-17': 0,
          '18-29': 0,
          '30-39': 0,
          '40-49': 0,
          '50-59': 0,
          '60-69': 0,
          '70+': 0,
        };

        subjects.forEach((subject) => {
          // Gender
          const gender = subject.sex || 'Unknown';
          genderCount[gender] = (genderCount[gender] || 0) + 1;

          // Race
          const race = subject.race || 'Unknown';
          raceCount[race] = (raceCount[race] || 0) + 1;

          // Age groups
          if (subject.date_of_birth) {
            const birthDate = new Date(subject.date_of_birth);
            const age = new Date().getFullYear() - birthDate.getFullYear();
            if (age < 18) ageGroups['0-17']++;
            else if (age < 30) ageGroups['18-29']++;
            else if (age < 40) ageGroups['30-39']++;
            else if (age < 50) ageGroups['40-49']++;
            else if (age < 60) ageGroups['50-59']++;
            else if (age < 70) ageGroups['60-69']++;
            else ageGroups['70+']++;
          }
        });

        const genderData = Object.entries(genderCount).map(([name, value]) => ({ name, value }));
        const raceData = Object.entries(raceCount).map(([name, value]) => ({ name, value }));
        const ageGroupsData = Object.entries(ageGroups)
          .filter(([_, value]) => value > 0)
          .map(([name, value]) => ({ name, value }));

        setDemographicsData({
          gender: genderData,
          race: raceData,
          ageGroups: ageGroupsData,
        });

        // Process assessment types data
        const assessmentTypeCount: Record<string, number> = {};
        assessments.forEach((assessment) => {
          const type = assessment.assessment_type || 'Unknown';
          assessmentTypeCount[type] = (assessmentTypeCount[type] || 0) + 1;
        });

        const assessmentTypesData = Object.entries(assessmentTypeCount)
          .map(([name, value]) => ({ name, value }))
          .sort((a, b) => b.value - a.value);

        setAssessmentTypesData(assessmentTypesData);

        // Calculate enrollment status
        let enrolled = 0;
        let notEnrolled = 0;
        subjects.forEach((subject) => {
          if (subject.enrollment_status === 'enrolled') {
            enrolled++;
          } else {
            notEnrolled++;
          }
        });
        setEnrollmentStats({ enrolled, notEnrolled });
      } catch (error) {
        console.error('Failed to fetch chart data:', error);
      } finally {
        setChartsLoading(false);
      }
    };

    fetchChartData();
  }, [selectedStudy]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        {selectedStudy && (
          <div className="text-sm text-gray-600">
            <span className="font-medium">Viewing:</span> {selectedStudy.name}
          </div>
        )}
      </div>
      
      {selectedStudy ? (
        // Study-specific dashboard
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-primary-100 rounded-lg">
              <Users className="w-6 h-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Subjects</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats.loading ? '...' : stats.subjects}
              </p>
            </div>
          </div>
          <Link
            to="/subjects"
            className="mt-4 text-sm text-primary-600 hover:text-primary-700"
          >
            View all →
          </Link>
        </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <ClipboardList className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Assessments</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stats.loading ? '...' : stats.assessments}
                </p>
              </div>
            </div>
            <Link
              to="/assessments"
              className="mt-4 text-sm text-primary-600 hover:text-primary-700"
            >
              View all →
            </Link>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <FileText className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Session Notes</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stats.loading ? '...' : stats.sessionNotes}
                </p>
              </div>
            </div>
            <Link
              to="/session-notes"
            className="mt-4 text-sm text-primary-600 hover:text-primary-700"
          >
            View all →
          </Link>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <BookOpen className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Study Status</p>
                <p className="text-2xl font-semibold text-gray-900 capitalize">
                  {selectedStudy.status}
                </p>
              </div>
            </div>
            <Link
              to={`/studies/${selectedStudy.id}`}
              className="mt-4 text-sm text-primary-600 hover:text-primary-700"
            >
              View details →
            </Link>
          </div>
        </div>
      ) : null}

      {selectedStudy && (
        // Charts section for study-specific dashboard
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Demographics Charts */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Demographics</h2>
            {chartsLoading ? (
              <div className="flex items-center justify-center h-64">
                <p className="text-gray-500">Loading demographics data...</p>
              </div>
            ) : demographicsData && demographicsData.gender.length > 0 ? (
              <div className="space-y-6">
                {/* Gender Distribution */}
                {demographicsData.gender.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Gender Distribution</h3>
                    <ResponsiveContainer width="100%" height={200}>
                      <PieChart>
                        <Pie
                          data={demographicsData.gender}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          outerRadius={70}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {demographicsData.gender.map((_entry, index) => {
                            const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
                            return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                          })}
                        </Pie>
                        <Tooltip />
                        <Legend 
                          verticalAlign="bottom" 
                          height={36}
                          formatter={(value, entry) => `${value} (${entry.payload?.value ?? 0})`}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Race Distribution */}
                {demographicsData.race.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Race Distribution</h3>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={demographicsData.race}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#3b82f6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Age Groups */}
                {demographicsData.ageGroups.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Age Distribution</h3>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={demographicsData.ageGroups}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#10b981" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-64">
                <p className="text-gray-500">No demographic data available</p>
              </div>
            )}
          </div>

          {/* Assessment Types Chart */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Assessment Types</h2>
            {chartsLoading ? (
              <div className="flex items-center justify-center h-64">
                <p className="text-gray-500">Loading assessment data...</p>
              </div>
            ) : assessmentTypesData.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={assessmentTypesData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={150} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" fill="#8b5cf6" name="Count" />
                  </BarChart>
                </ResponsiveContainer>
                {enrollmentStats && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Enrollment Status</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-green-50 rounded-lg p-4">
                        <p className="text-sm text-gray-600 mb-1">Enrolled</p>
                        <p className="text-2xl font-semibold text-green-700">{enrollmentStats.enrolled}</p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-sm text-gray-600 mb-1">Not Enrolled</p>
                        <p className="text-2xl font-semibold text-gray-700">{enrollmentStats.notEnrolled}</p>
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="flex items-center justify-center h-64">
                <p className="text-gray-500">No assessment data available</p>
              </div>
            )}
          </div>
        </div>
      )}

      {!selectedStudy && (
        // Summary dashboard (all studies)
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-primary-100 rounded-lg">
                <Users className="w-6 h-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Subjects</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stats.loading ? '...' : stats.subjects}
                </p>
              </div>
            </div>
            <Link
              to="/subjects"
              className="mt-4 text-sm text-primary-600 hover:text-primary-700"
            >
              View all →
            </Link>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <BookOpen className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Studies</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats.loading ? '...' : stats.studies}
              </p>
            </div>
          </div>
          <Link
            to="/studies"
            className="mt-4 text-sm text-primary-600 hover:text-primary-700"
          >
            View all →
          </Link>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Studies</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats.loading ? '...' : stats.activeStudies}
              </p>
            </div>
          </div>
        </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <ClipboardList className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Assessments</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stats.loading ? '...' : stats.assessments}
                </p>
              </div>
            </div>
            <Link
              to="/assessments"
              className="mt-4 text-sm text-primary-600 hover:text-primary-700"
            >
              View all →
            </Link>
      </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-orange-100 rounded-lg">
                <FileText className="w-6 h-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Session Notes</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stats.loading ? '...' : stats.sessionNotes}
                </p>
              </div>
            </div>
            <Link
              to="/session-notes"
              className="mt-4 text-sm text-primary-600 hover:text-primary-700"
            >
              View all →
            </Link>
          </div>
        </div>
      )}

      {selectedStudy && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="flex flex-wrap gap-4">
            <Link
              to="/subjects/new"
              className="btn btn-primary"
            >
              Add New Subject
            </Link>
            <Link
              to="/assessments/new"
              className="btn btn-secondary"
            >
              Create Assessment
            </Link>
            <Link
              to="/session-notes/new"
              className="btn btn-secondary"
            >
              Create Session Note
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

