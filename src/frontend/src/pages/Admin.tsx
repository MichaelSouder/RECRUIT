import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { usersApi, studiesApi, assessmentTypesApi, auditApi } from '../api/endpoints';
import { User, Study, AssessmentType, AuditLog, PaginatedResponse } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Plus, Edit, Trash2, Users, BookOpen, Settings, X, Eye, FileText, Download, Search, Filter, ArrowUp, ArrowDown } from 'lucide-react';
import { Modal } from '../components/ui/Modal';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';

const customFieldSchema = z.object({
  name: z.string().min(1, 'Field name is required').regex(/^[a-z0-9_]+$/, 'Field name must be lowercase alphanumeric with underscores'),
  label: z.string().min(1, 'Field label is required'),
  type: z.enum(['text', 'number', 'date', 'select', 'textarea']),
  required: z.boolean().optional(),
  options: z.array(z.string()).optional(), // For select type
});


// Schema - completely lenient, all validation done manually
// This prevents zod from showing errors before we want them
const assessmentTypeSchema = z.object({
  name: z.string().optional(),
  display_name: z.string().optional(),
  description: z.string().optional(),
  is_active: z.string().optional(),
  fields: z.array(customFieldSchema).optional(),
});

type AssessmentTypeFormData = z.infer<typeof assessmentTypeSchema>;

export const Admin: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'users' | 'studies' | 'assessment-types' | 'audit-trail'>('users');
  const [users, setUsers] = useState<User[]>([]);
  const [studies, setStudies] = useState<Study[]>([]);
  const [assessmentTypes, setAssessmentTypes] = useState<AssessmentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [studiesSortBy, setStudiesSortBy] = useState<'name' | 'status' | 'start_date' | null>(null);
  const [studiesSortOrder, setStudiesSortOrder] = useState<'asc' | 'desc'>('asc');
  const [showUserForm, setShowUserForm] = useState(false);
  const [showAssessmentTypeForm, setShowAssessmentTypeForm] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [editingAssessmentType, setEditingAssessmentType] = useState<AssessmentType | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showUserDetailsModal, setShowUserDetailsModal] = useState(false);
  
  // Audit trail state
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [auditLogsTotal, setAuditLogsTotal] = useState(0);
  const [auditLogsPage, setAuditLogsPage] = useState(1);
  const [auditLogsPages, setAuditLogsPages] = useState(0);
  const [auditFilters, setAuditFilters] = useState({
    search: '',
    entity_type: '',
    action: '',
    start_date: '',
    end_date: '',
  });

  useEffect(() => {
    fetchData();
  }, [activeTab, studiesSortBy, studiesSortOrder]);

  const handleStudiesSort = (column: 'name' | 'status' | 'start_date') => {
    if (studiesSortBy === column) {
      setStudiesSortOrder(studiesSortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setStudiesSortBy(column);
      setStudiesSortOrder('asc');
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'users') {
        const response = await usersApi.getAll();
        setUsers(response.data);
      } else if (activeTab === 'studies') {
        const params: any = { limit: 1000 };
        if (studiesSortBy) {
          params.sort_by = studiesSortBy;
          params.sort_order = studiesSortOrder;
        }
        const response = await studiesApi.getAll(params);
        setStudies(response.data.items);
      } else if (activeTab === 'assessment-types') {
        const response = await assessmentTypesApi.getAll();
        setAssessmentTypes(response.data);
      } else if (activeTab === 'audit-trail') {
        await fetchAuditLogs();
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAuditLogs = async (page: number = 1) => {
    setLoading(true);
    try {
      const params: any = {
        skip: (page - 1) * 100,
        limit: 100,
      };
      
      if (auditFilters.search) params.search = auditFilters.search;
      if (auditFilters.entity_type) params.entity_type = auditFilters.entity_type;
      if (auditFilters.action) params.action = auditFilters.action;
      if (auditFilters.start_date) params.start_date = auditFilters.start_date;
      if (auditFilters.end_date) params.end_date = auditFilters.end_date;
      
      const response = await auditApi.getAll(params);
      const data: PaginatedResponse<AuditLog> = response.data;
      setAuditLogs(data.items);
      setAuditLogsTotal(data.total);
      setAuditLogsPage(data.page);
      setAuditLogsPages(data.pages);
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportAuditLogs = async (format: 'csv' | 'json') => {
    try {
      const params: any = { format };
      if (auditFilters.start_date) params.start_date = auditFilters.start_date;
      if (auditFilters.end_date) params.end_date = auditFilters.end_date;
      if (auditFilters.entity_type) params.entity_type = auditFilters.entity_type;
      if (auditFilters.action) params.action = auditFilters.action;
      
      const response = await auditApi.export(params);
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_logs.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to export audit logs:', error);
      alert('Failed to export audit logs');
    }
  };

  const handleDeleteUser = async (id: number) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    try {
      await usersApi.delete(id);
      fetchData();
    } catch (error) {
      console.error('Failed to delete user:', error);
      alert('Failed to delete user');
    }
  };

  const handleDeleteAssessmentType = async (id: number) => {
    if (!confirm('Are you sure you want to delete this assessment type?')) return;
    try {
      await assessmentTypesApi.delete(id);
      fetchData();
    } catch (error) {
      console.error('Failed to delete assessment type:', error);
      alert('Failed to delete assessment type');
    }
  };

  const handleDeleteStudy = async (id: number) => {
    if (!confirm('Are you sure you want to delete this study? This action cannot be undone.')) return;
    try {
      await studiesApi.delete(id);
      fetchData();
    } catch (error) {
      console.error('Failed to delete study:', error);
      alert('Failed to delete study');
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-800';
      case 'researcher':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const navigate = useNavigate();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Admin Panel</h1>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('users')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'users'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Users className="w-5 h-5" />
              <span>Users</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('studies')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'studies'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <BookOpen className="w-5 h-5" />
              <span>Studies</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('assessment-types')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'assessment-types'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Settings className="w-5 h-5" />
              <span>Assessment Types</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('audit-trail')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'audit-trail'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <FileText className="w-5 h-5" />
              <span>Audit Trail</span>
            </div>
          </button>
        </nav>
      </div>

      {/* Content */}
      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <>
          {activeTab === 'users' && (
            <div>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <h2 className="text-2xl font-semibold text-gray-900">User Management</h2>
                <Button 
                  onClick={() => { setEditingUser(null); setShowUserForm(true); }}
                  className="whitespace-nowrap flex items-center"
                >
                  <Plus className="w-4 h-4 mr-2 flex-shrink-0" />
                  <span>Add User</span>
                </Button>
              </div>
              <div className="card overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {users.map((user) => (
                      <tr key={user.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {user.email}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {user.full_name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleColor(user.role || 'viewer')}`}>
                            {user.role || 'viewer'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm font-medium">
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => {
                                setSelectedUser(user);
                                setShowUserDetailsModal(true);
                              }}
                              className="text-primary-600 hover:text-primary-900 p-1 rounded hover:bg-primary-50 transition-colors"
                              title="Show Details"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => { setEditingUser(user); setShowUserForm(true); }}
                              className="text-primary-600 hover:text-primary-900 p-1 rounded hover:bg-primary-50 transition-colors"
                              title="Edit"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteUser(user.id)}
                              className="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50 transition-colors"
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
          )}

          {activeTab === 'studies' && (
            <div>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <h2 className="text-2xl font-semibold text-gray-900">Study Management</h2>
                <Button 
                  className="whitespace-nowrap flex items-center"
                  onClick={() => navigate('/studies/new', { state: { fromAdmin: true } })}
                >
                  <Plus className="w-4 h-4 mr-2 flex-shrink-0" />
                  <span>Add Study</span>
                </Button>
              </div>
              <div className="card overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th 
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                        onClick={() => handleStudiesSort('name')}
                      >
                        <div className="flex items-center space-x-1">
                          <span>Name</span>
                          {studiesSortBy === 'name' && (
                            studiesSortOrder === 'asc' ? (
                              <ArrowUp className="w-3 h-3" />
                            ) : (
                              <ArrowDown className="w-3 h-3" />
                            )
                          )}
                        </div>
                      </th>
                      <th 
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                        onClick={() => handleStudiesSort('status')}
                      >
                        <div className="flex items-center space-x-1">
                          <span>Status</span>
                          {studiesSortBy === 'status' && (
                            studiesSortOrder === 'asc' ? (
                              <ArrowUp className="w-3 h-3" />
                            ) : (
                              <ArrowDown className="w-3 h-3" />
                            )
                          )}
                        </div>
                      </th>
                      <th 
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                        onClick={() => handleStudiesSort('start_date')}
                      >
                        <div className="flex items-center space-x-1">
                          <span>Start Date</span>
                          {studiesSortBy === 'start_date' && (
                            studiesSortOrder === 'asc' ? (
                              <ArrowUp className="w-3 h-3" />
                            ) : (
                              <ArrowDown className="w-3 h-3" />
                            )
                          )}
                        </div>
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        End Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Description
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {studies.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-6 py-8 text-center text-sm text-gray-500">
                          No studies found. Create one to get started.
                        </td>
                      </tr>
                    ) : (
                      studies.map((study) => (
                        <tr key={study.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{study.name}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              study.status === 'active' ? 'bg-green-100 text-green-800' :
                              study.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                              study.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {study.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {study.start_date ? format(new Date(study.start_date), 'MMM dd, yyyy') : '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {study.end_date ? format(new Date(study.end_date), 'MMM dd, yyyy') : '-'}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500">
                            <div className="max-w-xs truncate" title={study.description || undefined}>
                              {study.description || '-'}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => navigate(`/studies/${study.id}`, { state: { fromAdmin: true } })}
                                className="text-primary-600 hover:text-primary-900 p-1 rounded hover:bg-primary-50 transition-colors"
                                title="Show Details"
                              >
                                <Eye className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => navigate(`/studies/${study.id}/edit`, { state: { fromAdmin: true } })}
                                className="text-primary-600 hover:text-primary-900 p-1 rounded hover:bg-primary-50 transition-colors"
                                title="Edit"
                              >
                                <Edit className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleDeleteStudy(study.id)}
                                className="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50 transition-colors"
                                title="Delete"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'assessment-types' && (
            <div>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <h2 className="text-2xl font-semibold text-gray-900">Assessment Types</h2>
                <Button 
                  onClick={() => { setEditingAssessmentType(null); setShowAssessmentTypeForm(true); }}
                  className="whitespace-nowrap flex items-center"
                >
                  <Plus className="w-4 h-4 mr-2 flex-shrink-0" />
                  <span>Add Assessment Type</span>
                </Button>
              </div>
              <div className="card overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Display Name</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {assessmentTypes.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-6 py-8 text-center text-sm text-gray-500">
                          No assessment types found. Create one to get started.
                        </td>
                      </tr>
                    ) : (
                      assessmentTypes.map((type) => (
                        <tr key={type.id} className="hover:bg-gray-50">
                          <td className="px-4 py-4 text-sm font-medium text-gray-900">
                            <code className="text-xs bg-gray-100 px-2 py-1 rounded">{type.name}</code>
                          </td>
                          <td className="px-4 py-4 text-sm text-gray-700 font-medium">
                            {type.display_name}
                          </td>
                          <td className="px-4 py-4 text-sm text-gray-500 max-w-xs">
                            <div className="truncate" title={type.description || undefined}>
                              {type.description || '-'}
                            </div>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              type.is_active === 'true' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                            }`}>
                              {type.is_active === 'true' ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-4 py-4 text-sm font-medium">
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => { setEditingAssessmentType(type); setShowAssessmentTypeForm(true); }}
                                className="text-primary-600 hover:text-primary-900 p-1 rounded hover:bg-primary-50 transition-colors"
                                title="Edit"
                              >
                                <Edit className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleDeleteAssessmentType(type.id)}
                                className="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50 transition-colors"
                                title="Delete"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'audit-trail' && (
            <div>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <h2 className="text-2xl font-semibold text-gray-900">Audit Trail</h2>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="secondary"
                    onClick={() => handleExportAuditLogs('csv')}
                    className="flex items-center"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export CSV
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => handleExportAuditLogs('json')}
                    className="flex items-center"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export JSON
                  </Button>
                </div>
              </div>

              {/* Filters */}
              <div className="card mb-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <Input
                        type="text"
                        placeholder="Search..."
                        value={auditFilters.search}
                        onChange={(e) => setAuditFilters({ ...auditFilters, search: e.target.value })}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Entity Type</label>
                    <select
                      value={auditFilters.entity_type}
                      onChange={(e) => setAuditFilters({ ...auditFilters, entity_type: e.target.value })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    >
                      <option value="">All</option>
                      <option value="subject">Subject</option>
                      <option value="study">Study</option>
                      <option value="assessment">Assessment</option>
                      <option value="session_note">Session Note</option>
                      <option value="user">User</option>
                      <option value="assessment_type">Assessment Type</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Action</label>
                    <select
                      value={auditFilters.action}
                      onChange={(e) => setAuditFilters({ ...auditFilters, action: e.target.value })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    >
                      <option value="">All</option>
                      <option value="CREATE">Create</option>
                      <option value="UPDATE">Update</option>
                      <option value="DELETE">Delete</option>
                      <option value="VIEW">View</option>
                      <option value="EXPORT">Export</option>
                      <option value="LOGIN">Login</option>
                      <option value="LOGOUT">Logout</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                    <Input
                      type="date"
                      value={auditFilters.start_date}
                      onChange={(e) => setAuditFilters({ ...auditFilters, start_date: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                    <Input
                      type="date"
                      value={auditFilters.end_date}
                      onChange={(e) => setAuditFilters({ ...auditFilters, end_date: e.target.value })}
                    />
                  </div>
                </div>
                <div className="mt-4">
                  <Button
                    onClick={() => fetchAuditLogs(1)}
                    className="flex items-center"
                  >
                    <Filter className="w-4 h-4 mr-2" />
                    Apply Filters
                  </Button>
                </div>
              </div>

              {/* Audit Logs Table */}
              <div className="card overflow-x-auto">
                {loading ? (
                  <div className="text-center py-8">
                    <p className="text-gray-500">Loading audit logs...</p>
                  </div>
                ) : (
                  <>
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Timestamp
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            User
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Action
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Entity
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Summary
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            IP Address
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {auditLogs.length === 0 ? (
                          <tr>
                            <td colSpan={6} className="px-6 py-8 text-center text-sm text-gray-500">
                              No audit logs found.
                            </td>
                          </tr>
                        ) : (
                          auditLogs.map((log) => (
                            <tr key={log.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {format(new Date(log.timestamp), 'MMM dd, yyyy HH:mm:ss')}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm text-gray-900">{log.user_full_name || log.user_email}</div>
                                <div className="text-sm text-gray-500">{log.user_email}</div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                  log.action === 'CREATE' ? 'bg-green-100 text-green-800' :
                                  log.action === 'UPDATE' ? 'bg-blue-100 text-blue-800' :
                                  log.action === 'DELETE' ? 'bg-red-100 text-red-800' :
                                  log.action === 'VIEW' ? 'bg-gray-100 text-gray-800' :
                                  log.action === 'EXPORT' ? 'bg-purple-100 text-purple-800' :
                                  'bg-yellow-100 text-yellow-800'
                                }`}>
                                  {log.action}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm text-gray-900">{log.entity_type}</div>
                                <div className="text-sm text-gray-500">
                                  {log.entity_name || `ID: ${log.entity_id}`}
                                </div>
                                {log.field_name && (
                                  <div className="text-xs text-gray-400">Field: {log.field_name}</div>
                                )}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-500">
                                <div className="max-w-xs truncate" title={log.change_summary || undefined}>
                                  {log.change_summary || '-'}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {log.ip_address || '-'}
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                    
                    {/* Pagination */}
                    {auditLogsPages > 1 && (
                      <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                        <div className="text-sm text-gray-700">
                          Showing page {auditLogsPage} of {auditLogsPages} ({auditLogsTotal} total)
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            variant="secondary"
                            onClick={() => fetchAuditLogs(auditLogsPage - 1)}
                            disabled={auditLogsPage === 1}
                          >
                            Previous
                          </Button>
                          <Button
                            variant="secondary"
                            onClick={() => fetchAuditLogs(auditLogsPage + 1)}
                            disabled={auditLogsPage === auditLogsPages}
                          >
                            Next
                          </Button>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          )}
        </>
      )}

      {/* User Form Modal - simplified for now */}
      {showUserForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">
              {editingUser ? 'Edit User' : 'Create User'}
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              User form implementation needed. This is a placeholder.
            </p>
            <div className="flex justify-end space-x-2">
              <Button variant="secondary" onClick={() => { setShowUserForm(false); setEditingUser(null); }}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Assessment Type Form Modal */}
      {showAssessmentTypeForm && (
        <AssessmentTypeFormModal
          assessmentType={editingAssessmentType}
          onClose={() => {
            setShowAssessmentTypeForm(false);
            setEditingAssessmentType(null);
          }}
          onSuccess={() => {
            setShowAssessmentTypeForm(false);
            setEditingAssessmentType(null);
            fetchData();
          }}
        />
      )}

      {/* User Details Modal */}
      <Modal
        isOpen={showUserDetailsModal}
        onClose={() => {
          setShowUserDetailsModal(false);
          setSelectedUser(null);
        }}
        title="User Details"
        size="md"
      >
        {selectedUser ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <p className="text-sm text-gray-900">{selectedUser.full_name || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <p className="text-sm text-gray-900">{selectedUser.email}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                <p className="text-sm text-gray-900">{selectedUser.location || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <p className="text-sm text-gray-900">{selectedUser.phone || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <p className="text-sm text-gray-900">{selectedUser.role || 'viewer'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <p className="text-sm text-gray-900">
                  {selectedUser.is_active ? 'Active' : 'Inactive'}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Superuser</label>
                <p className="text-sm text-gray-900">
                  {selectedUser.is_superuser ? 'Yes' : 'No'}
                </p>
              </div>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
};

// Custom Field Type
type CustomField = {
  name: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'select' | 'textarea';
  required?: boolean;
  options?: string[];
};

// Assessment Type Form Modal Component
const AssessmentTypeFormModal: React.FC<{
  assessmentType: AssessmentType | null;
  onClose: () => void;
  onSuccess: () => void;
}> = ({ assessmentType, onClose, onSuccess }) => {
  const isEdit = !!assessmentType;
  const [loading, setLoading] = useState(false);
  const [error, setFormError] = useState<string | null>(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [showNameError, setShowNameError] = useState(false);
  const [showDisplayNameError, setShowDisplayNameError] = useState(false);
  const [customFields, setCustomFields] = useState<CustomField[]>(
    assessmentType?.fields ? (Array.isArray(assessmentType.fields) ? assessmentType.fields : []) : []
  );

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
    clearErrors,
    watch,
    getValues,
    reset,
  } = useForm<AssessmentTypeFormData>({
    // Don't use zodResolver - we'll handle all validation manually
    mode: 'onSubmit', // Only validate on submit
    reValidateMode: 'onChange', // Re-validate on change after first submit
    defaultValues: assessmentType
      ? {
          name: assessmentType.name,
          display_name: assessmentType.display_name,
          description: assessmentType.description || '',
          is_active: assessmentType.is_active || 'true',
          fields: assessmentType.fields ? (Array.isArray(assessmentType.fields) ? assessmentType.fields : []) : [],
        }
      : {
          name: '',
          display_name: '',
          description: '',
          is_active: 'true',
          fields: [],
        },
  });

  // Reset form state when modal opens/closes or assessmentType changes
  React.useEffect(() => {
    setHasSubmitted(false);
    setShowNameError(false);
    setShowDisplayNameError(false);
    setFormError(null);
    clearErrors();
    
    if (assessmentType) {
      reset({
        name: assessmentType.name,
        display_name: assessmentType.display_name,
        description: assessmentType.description || '',
        is_active: assessmentType.is_active || 'true',
        fields: assessmentType.fields ? (Array.isArray(assessmentType.fields) ? assessmentType.fields : []) : [],
      });
      setCustomFields(assessmentType.fields ? (Array.isArray(assessmentType.fields) ? assessmentType.fields : []) : []);
    } else {
      reset({
        name: '',
        display_name: '',
        description: '',
        is_active: 'true',
        fields: [],
      });
      setCustomFields([]);
    }
  }, [assessmentType, reset, clearErrors]);

  // Watch fields to clear errors when they become valid
  const displayName = watch('display_name');
  const name = watch('name');
  
  // Control error visibility - hide errors when fields become valid (backup to onChange)
  React.useEffect(() => {
    if (!hasSubmitted) {
      setShowNameError(false);
      setShowDisplayNameError(false);
      return;
    }
    
    // Hide name error if field is valid
    if (!isEdit && name) {
      const trimmed = String(name).trim();
      if (trimmed.length > 0 && /^[a-z0-9_-]+$/.test(trimmed)) {
        clearErrors('name');
        setShowNameError(false);
      }
    }
    
    // Hide display_name error if field has content
    if (displayName) {
      const trimmed = String(displayName).trim();
      if (trimmed.length > 0) {
        clearErrors('display_name');
        setShowDisplayNameError(false);
      }
    }
  }, [name, displayName, hasSubmitted, isEdit, clearErrors]);

  const addCustomField = () => {
    setCustomFields([...customFields, { name: '', label: '', type: 'text', required: false }]);
  };

  const removeCustomField = (index: number) => {
    setCustomFields(customFields.filter((_, i) => i !== index));
  };

  const updateCustomField = (index: number, field: Partial<CustomField>) => {
    const updated = [...customFields];
    updated[index] = { ...updated[index], ...field };
    setCustomFields(updated);
  };

  const addOptionToField = (fieldIndex: number) => {
    const updated = [...customFields];
    if (!updated[fieldIndex].options) {
      updated[fieldIndex].options = [];
    }
    updated[fieldIndex].options = [...updated[fieldIndex].options, ''];
    setCustomFields(updated);
  };

  const updateFieldOption = (fieldIndex: number, optionIndex: number, value: string) => {
    const updated = [...customFields];
    if (updated[fieldIndex].options) {
      updated[fieldIndex].options![optionIndex] = value;
      setCustomFields(updated);
    }
  };

  const removeFieldOption = (fieldIndex: number, optionIndex: number) => {
    const updated = [...customFields];
    if (updated[fieldIndex].options) {
      updated[fieldIndex].options = updated[fieldIndex].options!.filter((_, i) => i !== optionIndex);
      setCustomFields(updated);
    }
  };

  const onSubmit = async (_data: AssessmentTypeFormData) => {
    // Set hasSubmitted first so error clearing works
    setHasSubmitted(true);
    setLoading(true);
    setFormError(null);
    
    // Get current form values directly from form state - this is the source of truth
    const formValues = getValues();
    const currentName = formValues.name || '';
    const currentDisplayName = formValues.display_name || '';
    
    // Clear any existing manual errors first
    clearErrors('name');
    clearErrors('display_name');
    setShowNameError(false);
    setShowDisplayNameError(false);
    
    // Manual validation for name when creating
    if (!isEdit) {
      const trimmedName = String(currentName).trim();
      if (!trimmedName || trimmedName.length === 0) {
        setError('name', { type: 'manual', message: 'Name is required' });
        setShowNameError(true);
        setFormError('Name is required');
        setLoading(false);
        return;
      }
      // Validate name format
      if (!/^[a-z0-9_-]+$/.test(trimmedName)) {
        setError('name', { type: 'manual', message: 'Name must be lowercase alphanumeric with underscores or hyphens only' });
        setShowNameError(true);
        setFormError('Name must be lowercase alphanumeric with underscores or hyphens only');
        setLoading(false);
        return;
      }
    }
    
    // Manual validation for display_name
    const trimmedDisplayName = String(currentDisplayName).trim();
    if (!trimmedDisplayName || trimmedDisplayName.length === 0) {
      setError('display_name', { type: 'manual', message: 'Display name is required' });
      setShowDisplayNameError(true);
      setFormError('Display name is required');
      setLoading(false);
      return;
    }
    
    // Validate custom fields before submission
    const invalidFields = customFields.filter(f => {
      if (!f.name || f.name.trim() === '') return true;
      if (!f.label || f.label.trim() === '') return true;
      if (f.type === 'select' && (!f.options || f.options.length === 0 || f.options.some(opt => !opt || opt.trim() === ''))) {
        return true;
      }
      // Validate field name format
      if (!/^[a-z0-9_]+$/.test(f.name)) return true;
      return false;
    });

    if (invalidFields.length > 0) {
      setFormError('Please complete all custom fields. Field names must be lowercase alphanumeric with underscores only. Select fields must have at least one option.');
      setLoading(false);
      return;
    }

    try {
      // Validate custom fields
      const validFields = customFields.filter(f => f.name && f.label);
      const fieldsData = validFields.length > 0 ? validFields : undefined;

      if (isEdit && assessmentType) {
        // Update existing
        const updateData: any = {
          display_name: trimmedDisplayName,
          description: formValues.description || '',
          is_active: formValues.is_active || 'true',
          fields: fieldsData,
        };
        await assessmentTypesApi.update(assessmentType.id, updateData);
      } else {
        // Create new - use validated/trimmed values
        const createData: any = {
          name: String(currentName).trim(),
          display_name: trimmedDisplayName,
          description: formValues.description || '',
          is_active: formValues.is_active || 'true',
          fields: fieldsData,
        };
        await assessmentTypesApi.create(createData);
      }
      onSuccess();
    } catch (err: any) {
      console.error('Failed to save assessment type:', err);
      setFormError(err.response?.data?.detail || 'Failed to save assessment type. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center z-10">
          <h3 className="text-xl font-semibold text-gray-900">
            {isEdit ? 'Edit Assessment Type' : 'Create Assessment Type'}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {!isEdit && (
              <div className="md:col-span-2">
                <Input
                  label="Name (identifier) *"
                  {...register('name', {
                    onChange: (e) => {
                      // Clear error when user types valid input
                      if (hasSubmitted) {
                        const value = e.target.value;
                        const trimmed = String(value).trim();
                        if (trimmed.length > 0 && /^[a-z0-9_-]+$/.test(trimmed)) {
                          clearErrors('name');
                          setShowNameError(false);
                        }
                      }
                    }
                  })}
                  error={showNameError && errors.name ? errors.name.message : undefined}
                  disabled={isEdit}
                  placeholder="e.g., moca, dass21, custom_test"
                  helperText="Lowercase, alphanumeric, underscores or hyphens only"
                  className="w-full"
                />
              </div>
            )}

            <div className="md:col-span-2">
              <Input
                label="Display Name *"
                {...register('display_name', {
                  onChange: (e) => {
                    // Clear error when user types valid input
                    if (hasSubmitted) {
                      const value = e.target.value;
                      const trimmed = String(value).trim();
                      if (trimmed.length > 0) {
                        clearErrors('display_name');
                        setShowDisplayNameError(false);
                      }
                    }
                  }
                })}
                error={showDisplayNameError && errors.display_name ? errors.display_name.message : undefined}
                placeholder="e.g., MoCA, DASS-21, Custom Test"
                helperText="The human-readable name for this assessment type"
                className="w-full"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                {...register('description')}
                className="input min-h-[100px]"
                placeholder="Brief description of this assessment type..."
              />
              {errors.description && (
                <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
              )}
            </div>


            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                {...register('is_active')}
                className="input"
              >
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            </div>
          </div>

          {/* Custom Fields Section */}
          <div className="md:col-span-2 border-t border-gray-200 pt-6">
            <div className="flex justify-between items-start mb-4 gap-4">
              <div className="flex-1 min-w-0">
                <h4 className="text-lg font-semibold text-gray-900">Custom Fields</h4>
                <p className="text-sm text-gray-500 mt-1 break-words">
                  Define additional fields that will appear when creating assessments of this type
                </p>
              </div>
              <Button
                type="button"
                variant="secondary"
                onClick={addCustomField}
                className="flex items-center space-x-2 flex-shrink-0"
              >
                <Plus className="w-4 h-4 flex-shrink-0" />
                <span>Add Field</span>
              </Button>
            </div>

            {customFields.length === 0 ? (
              <div className="text-center py-8 text-gray-500 text-sm">
                No custom fields defined. Click "Add Field" to create one.
              </div>
            ) : (
              <div className="space-y-4">
                {customFields.map((field, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                      <div className="md:col-span-3">
                        <Input
                          label="Field Name *"
                          value={field.name}
                          onChange={(e) => updateCustomField(index, { name: e.target.value })}
                          placeholder="e.g., score, notes, result"
                          helperText="Lowercase, alphanumeric, underscores only"
                          className="w-full"
                        />
                      </div>
                      <div className="md:col-span-3">
                        <Input
                          label="Field Label *"
                          value={field.label}
                          onChange={(e) => updateCustomField(index, { label: e.target.value })}
                          placeholder="e.g., Score, Notes, Result"
                          className="w-full"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1 whitespace-nowrap">
                          Field Type *
                        </label>
                        <select
                          value={field.type}
                          onChange={(e) => updateCustomField(index, { type: e.target.value as CustomField['type'] })}
                          className="input w-full"
                        >
                          <option value="text">Text</option>
                          <option value="number">Number</option>
                          <option value="date">Date</option>
                          <option value="textarea">Textarea</option>
                          <option value="select">Select</option>
                        </select>
                      </div>
                      <div className="md:col-span-2 flex items-end">
                        <label className="flex items-center space-x-2 cursor-pointer whitespace-nowrap">
                          <input
                            type="checkbox"
                            checked={field.required || false}
                            onChange={(e) => updateCustomField(index, { required: e.target.checked })}
                            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 flex-shrink-0"
                          />
                          <span className="text-sm text-gray-700">Required</span>
                        </label>
                      </div>
                      <div className="md:col-span-2 flex items-end justify-end">
                        <Button
                          type="button"
                          variant="danger"
                          onClick={() => removeCustomField(index)}
                          className="flex items-center space-x-1 whitespace-nowrap"
                        >
                          <Trash2 className="w-4 h-4 flex-shrink-0" />
                          <span>Remove</span>
                        </Button>
                      </div>
                    </div>

                    {/* Options for select type */}
                    {field.type === 'select' && (
                      <div className="mt-4 pt-4 border-t border-gray-300">
                        <div className="flex justify-between items-center mb-2 gap-2">
                          <label className="text-sm font-medium text-gray-700 whitespace-nowrap">Options</label>
                          <Button
                            type="button"
                            variant="secondary"
                            onClick={() => addOptionToField(index)}
                            className="text-xs py-1 px-2 flex items-center space-x-1 whitespace-nowrap"
                          >
                            <Plus className="w-3 h-3 flex-shrink-0" />
                            <span>Add Option</span>
                          </Button>
                        </div>
                        {field.options && field.options.length > 0 ? (
                          <div className="space-y-2">
                            {field.options.map((option, optIndex) => (
                              <div key={optIndex} className="flex items-center space-x-2 gap-2">
                                <Input
                                  value={option}
                                  onChange={(e) => updateFieldOption(index, optIndex, e.target.value)}
                                  placeholder={`Option ${optIndex + 1}`}
                                  className="flex-1 min-w-0"
                                />
                                <Button
                                  type="button"
                                  variant="danger"
                                  onClick={() => removeFieldOption(index, optIndex)}
                                  className="px-2 flex-shrink-0"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-gray-500 break-words">No options defined. Add at least one option.</p>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" isLoading={loading}>
              {isEdit ? 'Update Assessment Type' : 'Create Assessment Type'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

