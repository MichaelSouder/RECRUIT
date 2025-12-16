export interface User {
  id: number;
  email: string;
  full_name: string | null;
  location: string | null;
  phone: string | null;
  is_active: boolean;
  is_superuser: boolean;
  role: string; // admin, researcher, viewer
}

export interface Subject {
  id: number;
  first_name: string;
  middle_name: string | null;
  last_name: string;
  date_of_birth: string | null;
  sex: string | null;
  ssn: string | null;
  race: string | null;
  ethnicity: string | null;
  death_date: string | null;
  county: string | null;
  zip: string | null;
  enrollment_status: string | null;
  created_at: string;
  updated_at: string;
  created_by: number | null;
}

export interface Study {
  id: number;
  name: string;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
  status: string;
  principal_investigator_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface SessionNote {
  id: number;
  subject_id: number;
  session_date: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  created_by: number | null;
}

export interface Assessment {
  id: number;
  subject_id: number;
  study_id: number | null;
  assessment_type: string;
  assessment_date: string;
  assessment_time: string | null;
  total_score: number | null;
  notes: string | null;
  data: any | null; // Flexible JSON data
  created_at: string;
  updated_at: string;
  created_by: number | null;
}

export interface AssessmentType {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
  min_score: string | null;
  max_score: string | null;
  fields: any | null; // JSON field definitions
  is_active: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface AuditLog {
  id: number;
  timestamp: string;
  user_id: number;
  user_email: string;
  user_full_name: string | null;
  action: string; // CREATE, UPDATE, DELETE, VIEW, EXPORT, LOGIN, LOGOUT
  entity_type: string;
  entity_id: number;
  entity_name: string | null;
  field_name: string | null;
  old_value: string | null;
  new_value: string | null;
  change_summary: string | null;
  ip_address: string | null;
  user_agent: string | null;
  session_id: string | null;
  additional_context: string | null;
  created_at: string;
}

