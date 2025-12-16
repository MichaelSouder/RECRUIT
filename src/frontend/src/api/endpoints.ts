import apiClient from './client';

// Auth endpoints
export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post('/api/v1/auth/login', { email, password }),
  loginWithPIV: (certificateId: string) =>
    apiClient.post('/api/v1/auth/login-piv', { certificate_id: certificateId }),
  register: (data: { email: string; password: string; full_name?: string }) =>
    apiClient.post('/api/v1/auth/register', data),
  getMe: () => apiClient.get('/api/v1/auth/me'),
  updateProfile: (data: { email?: string; full_name?: string }) =>
    apiClient.put('/api/v1/auth/me', data),
  changePassword: (data: { current_password: string; new_password: string }) =>
    apiClient.put('/api/v1/auth/me/password', data),
};

// Subjects endpoints
export const subjectsApi = {
  getAll: (params?: { skip?: number; limit?: number; search?: string; study_id?: number; sort_by?: string; sort_order?: string }) =>
    apiClient.get('/api/v1/subjects', { params }),
  getById: (id: number) => apiClient.get(`/api/v1/subjects/${id}`),
  create: (data: any) => {
    // Handle study_ids in the request body
    return apiClient.post('/api/v1/subjects', data);
  },
  update: (id: number, data: any) => apiClient.put(`/api/v1/subjects/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/subjects/${id}`),
};

// Studies endpoints
export const studiesApi = {
  getAll: (params?: { skip?: number; limit?: number; sort_by?: string; sort_order?: string }) =>
    apiClient.get('/api/v1/studies', { params }),
  getById: (id: number) => apiClient.get(`/api/v1/studies/${id}`),
  create: (data: any) => apiClient.post('/api/v1/studies', data),
  update: (id: number, data: any) => apiClient.put(`/api/v1/studies/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/studies/${id}`),
  getResearchers: () => apiClient.get('/api/v1/studies/researchers'),
};

// Session Notes endpoints
export const sessionNotesApi = {
  getAll: (params?: { skip?: number; limit?: number; subject_id?: number; study_id?: number; sort_by?: string; sort_order?: string }) =>
    apiClient.get('/api/v1/session-notes', { params }),
  getById: (id: number) => apiClient.get(`/api/v1/session-notes/${id}`),
  create: (data: any) => apiClient.post('/api/v1/session-notes', data),
  update: (id: number, data: any) => apiClient.put(`/api/v1/session-notes/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/session-notes/${id}`),
};

// Assessments endpoints
export const assessmentsApi = {
  getAll: (params?: { skip?: number; limit?: number; subject_id?: number; study_id?: number; assessment_type?: string; sort_by?: string; sort_order?: string }) =>
    apiClient.get('/api/v1/assessments', { params }),
  getById: (id: number) => apiClient.get(`/api/v1/assessments/${id}`),
  create: (data: any) => apiClient.post('/api/v1/assessments', data),
  update: (id: number, data: any) => apiClient.put(`/api/v1/assessments/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/assessments/${id}`),
  getTypes: () => apiClient.get('/api/v1/assessments/types/list'),
};

// Admin endpoints
export const usersApi = {
  getAll: () => apiClient.get('/api/v1/admin/users'),
  create: (data: any) => apiClient.post('/api/v1/admin/users', data),
  update: (id: number, data: any) => apiClient.put(`/api/v1/admin/users/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/admin/users/${id}`),
  getStudies: (id: number) => apiClient.get(`/api/v1/admin/users/${id}/studies`),
  addStudies: (id: number, studyIds: number[]) => apiClient.post(`/api/v1/admin/users/${id}/studies`, studyIds),
  removeStudy: (userId: number, studyId: number) => apiClient.delete(`/api/v1/admin/users/${userId}/studies/${studyId}`),
};

// Assessment Types endpoints
export const assessmentTypesApi = {
  getAll: (activeOnly?: boolean) => apiClient.get('/api/v1/assessment-types', { params: { active_only: activeOnly } }),
  getById: (id: number) => apiClient.get(`/api/v1/assessment-types/${id}`),
  create: (data: any) => apiClient.post('/api/v1/assessment-types', data),
  update: (id: number, data: any) => apiClient.put(`/api/v1/assessment-types/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/assessment-types/${id}`),
};

// Audit Trail endpoints
export const auditApi = {
  getAll: (params?: {
    skip?: number;
    limit?: number;
    start_date?: string;
    end_date?: string;
    user_id?: number;
    entity_type?: string;
    action?: string;
    entity_id?: number;
    search?: string;
  }) => apiClient.get('/api/v1/audit', { params }),
  getEntityTrail: (entityType: string, entityId: number) =>
    apiClient.get(`/api/v1/audit/entity/${entityType}/${entityId}`),
  export: (params?: {
    format?: 'csv' | 'json';
    start_date?: string;
    end_date?: string;
    user_id?: number;
    entity_type?: string;
    action?: string;
  }) => apiClient.get('/api/v1/audit/export', { params, responseType: 'blob' }),
};

