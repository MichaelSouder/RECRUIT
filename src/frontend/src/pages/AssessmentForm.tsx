import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { assessmentsApi, subjectsApi, studiesApi, assessmentTypesApi } from '../api/endpoints';
import { Subject, Study, AssessmentType } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { useStudyStore } from '../store/studyStore';
import { useAuthStore } from '../store/authStore';

type CustomField = {
  name: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'select' | 'textarea';
  required?: boolean;
  options?: string[];
};

const assessmentSchema = z.object({
  subject_id: z.number().min(1, 'Subject is required'),
  study_id: z.number().optional(),
  assessment_type: z.string().min(1, 'Assessment type is required'),
  assessment_date: z.string().min(1, 'Assessment date is required'),
  assessment_time: z.string().optional(),
  notes: z.string().optional(),
});

type AssessmentFormData = z.infer<typeof assessmentSchema>;

export const AssessmentForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;
  const { selectedStudy } = useStudyStore();
  const { user } = useAuthStore();
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [studies, setStudies] = useState<Study[]>([]);
  const [assessmentTypes, setAssessmentTypes] = useState<AssessmentType[]>([]);
  const [selectedAssessmentType, setSelectedAssessmentType] = useState<AssessmentType | null>(null);
  const [customFieldValues, setCustomFieldValues] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<AssessmentFormData>({
    resolver: zodResolver(assessmentSchema),
    mode: 'onSubmit',
    reValidateMode: 'onChange',
    defaultValues: {
      study_id: selectedStudy?.id,
    },
  });

  const watchedAssessmentType = watch('assessment_type');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [subjectsRes, studiesRes, assessmentTypesRes] = await Promise.all([
          subjectsApi.getAll({ limit: 1000, study_id: selectedStudy?.id }),
          studiesApi.getAll({ limit: 1000 }),
          assessmentTypesApi.getAll(true), // Only active types
        ]);
        setSubjects(subjectsRes.data.items);
        setStudies(studiesRes.data.items);
        setAssessmentTypes(assessmentTypesRes.data);

        if (isEdit && id) {
          const assessmentRes = await assessmentsApi.getById(parseInt(id));
          const assessment = assessmentRes.data;
          setValue('subject_id', assessment.subject_id);
          setValue('study_id', assessment.study_id || undefined);
          setValue('assessment_type', assessment.assessment_type);
          setValue('assessment_date', assessment.assessment_date);
          setValue('assessment_time', assessment.assessment_time || '');
          setValue('notes', assessment.notes || '');
          
          // Find and set selected assessment type first
          const type = assessmentTypesRes.data.find((t: { name: string }) => t.name === assessment.assessment_type);
          if (type) {
            setSelectedAssessmentType(type);
          }
          
          // Load custom field values from assessment.data after type is set
          if (assessment.data && typeof assessment.data === 'object') {
            setCustomFieldValues(assessment.data);
          }
        } else if (selectedStudy) {
          setValue('study_id', selectedStudy.id);
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    };
    fetchData();
  }, [id, isEdit, setValue, selectedStudy]);

  // Update selected assessment type when assessment_type changes
  useEffect(() => {
    if (watchedAssessmentType) {
      const type = assessmentTypes.find(t => t.name === watchedAssessmentType);
      setSelectedAssessmentType(type || null);
      // Reset custom field values when type changes
      if (!isEdit) {
        setCustomFieldValues({});
      }
    } else {
      setSelectedAssessmentType(null);
    }
  }, [watchedAssessmentType, assessmentTypes, isEdit]);

  const updateCustomFieldValue = (fieldName: string, value: any) => {
    setCustomFieldValues(prev => ({
      ...prev,
      [fieldName]: value,
    }));
  };

  const renderCustomField = (field: CustomField) => {
    const fieldValue = customFieldValues[field.name] || '';

    switch (field.type) {
      case 'text':
        return (
          <Input
            key={field.name}
            label={field.label}
            value={fieldValue}
            onChange={(e) => updateCustomFieldValue(field.name, e.target.value)}
            required={field.required}
          />
        );
      case 'number':
        return (
          <Input
            key={field.name}
            label={field.label}
            type="number"
            step="0.01"
            value={fieldValue}
            onChange={(e) => updateCustomFieldValue(field.name, e.target.value ? parseFloat(e.target.value) : null)}
            required={field.required}
          />
        );
      case 'date':
        return (
          <Input
            key={field.name}
            label={field.label}
            type="date"
            value={fieldValue}
            onChange={(e) => updateCustomFieldValue(field.name, e.target.value)}
            required={field.required}
          />
        );
      case 'textarea':
        return (
          <div key={field.name} className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label} {field.required && '*'}
            </label>
            <textarea
              className="input min-h-[100px]"
              value={fieldValue}
              onChange={(e) => updateCustomFieldValue(field.name, e.target.value)}
              required={field.required}
            />
          </div>
        );
      case 'select':
        return (
          <div key={field.name}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label} {field.required && '*'}
            </label>
            <select
              className="input"
              value={fieldValue}
              onChange={(e) => updateCustomFieldValue(field.name, e.target.value)}
              required={field.required}
            >
              <option value="">Select {field.label.toLowerCase()}...</option>
              {field.options?.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        );
      default:
        return null;
    }
  };

  const onSubmit = async (data: AssessmentFormData) => {
    setLoading(true);
    try {
      // handleSubmit only calls this if validation passes, so data is valid
      // Note: created_by is automatically set by the backend to current_user.id
      const submitData: any = {
        subject_id: data.subject_id,
        study_id: data.study_id || undefined,
        assessment_type: data.assessment_type,
        assessment_date: data.assessment_date,
        assessment_time: data.assessment_time || undefined,
        notes: data.notes || undefined,
        data: Object.keys(customFieldValues).length > 0 ? customFieldValues : undefined,
      };

      if (isEdit && id) {
        await assessmentsApi.update(parseInt(id), submitData);
      } else {
        await assessmentsApi.create(submitData);
      }
      navigate('/assessments');
    } catch (error: any) {
      console.error('Failed to save assessment:', error);
      alert(error.response?.data?.detail || 'Failed to save assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        {isEdit ? 'Edit Assessment' : 'Create New Assessment'}
      </h1>

      <form onSubmit={handleSubmit(onSubmit)} className="card space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subject *
            </label>
            <select
              className="input"
              {...register('subject_id', { valueAsNumber: true })}
            >
              <option value="">Select a subject...</option>
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.last_name}, {subject.first_name}
                </option>
              ))}
            </select>
            {errors.subject_id && (
              <p className="mt-1 text-sm text-red-600">{errors.subject_id.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Study
            </label>
            <select
              className="input"
              {...register('study_id', { valueAsNumber: true })}
            >
              <option value="">Select a study...</option>
              {studies.map((study) => (
                <option key={study.id} value={study.id}>
                  {study.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Assessment Type *
            </label>
            <select
              className="input"
              {...register('assessment_type')}
            >
              <option value="">Select assessment type...</option>
              {assessmentTypes.map((type) => (
                <option key={type.id} value={type.name}>
                  {type.display_name}
                </option>
              ))}
            </select>
            {errors.assessment_type && (
              <p className="mt-1 text-sm text-red-600">{errors.assessment_type.message}</p>
            )}
          </div>

          <div>
            <Input
              label="Assessment Date *"
              type="date"
              {...register('assessment_date')}
              error={errors.assessment_date?.message}
            />
          </div>

          <div>
            <Input
              label="Assessment Time"
              type="time"
              {...register('assessment_time')}
              error={errors.assessment_time?.message}
            />
          </div>

          <div>
            <Input
              label="Created By"
              value={user?.full_name || user?.email || 'Current User'}
              disabled
              helperText="This assessment will be associated with your account"
            />
          </div>
        </div>

        {/* Custom Fields Section - shows assessment type name */}
        {selectedAssessmentType?.fields && Array.isArray(selectedAssessmentType.fields) && selectedAssessmentType.fields.length > 0 && (
          <div className="border-t border-gray-200 pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {selectedAssessmentType.display_name}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {selectedAssessmentType.fields.map((field: CustomField) => renderCustomField(field))}
            </div>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            className="input min-h-[200px]"
            {...register('notes')}
            placeholder="Enter assessment notes..."
          />
        </div>

        <div className="flex space-x-4">
          <Button type="submit" isLoading={loading}>
            {isEdit ? 'Update Assessment' : 'Create Assessment'}
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/assessments')}
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
};

