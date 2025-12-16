import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { sessionNotesApi, subjectsApi, studiesApi } from '../api/endpoints';
import { Subject, Study } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { useStudyStore } from '../store/studyStore';

const sessionNoteSchema = z.object({
  subject_id: z.number().min(1, 'Subject is required'),
  study_id: z.number().optional(),
  session_date: z.string().min(1, 'Session date is required'),
  notes: z.string().optional(),
});

type SessionNoteFormData = z.infer<typeof sessionNoteSchema>;

export const SessionNoteForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;
  const { selectedStudy } = useStudyStore();
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [studies, setStudies] = useState<Study[]>([]);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<SessionNoteFormData>({
    resolver: zodResolver(sessionNoteSchema),
    mode: 'onSubmit',
    reValidateMode: 'onChange',
    defaultValues: {
      study_id: selectedStudy?.id,
    },
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [subjectsRes, studiesRes] = await Promise.all([
          subjectsApi.getAll({ limit: 1000, study_id: selectedStudy?.id }),
          studiesApi.getAll({ limit: 1000 }),
        ]);
        setSubjects(subjectsRes.data.items);
        setStudies(studiesRes.data.items);

        if (isEdit && id) {
          const noteRes = await sessionNotesApi.getById(parseInt(id));
          const note = noteRes.data;
          setValue('subject_id', note.subject_id);
          setValue('study_id', note.study_id || undefined);
          setValue('session_date', note.session_date);
          setValue('notes', note.notes || '');
        } else if (selectedStudy) {
          setValue('study_id', selectedStudy.id);
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    };
    fetchData();
  }, [id, isEdit, setValue, selectedStudy]);

  const onSubmit = async (data: SessionNoteFormData) => {
    setLoading(true);
    try {
      // handleSubmit only calls this if validation passes, so data is valid
      const submitData: any = {
        subject_id: data.subject_id,
        study_id: data.study_id || undefined,
        session_date: data.session_date,
        notes: data.notes || undefined,
      };

      if (isEdit && id) {
        await sessionNotesApi.update(parseInt(id), submitData);
      } else {
        await sessionNotesApi.create(submitData);
      }
      navigate('/session-notes');
    } catch (error: any) {
      console.error('Failed to save session note:', error);
      alert(error.response?.data?.detail || 'Failed to save session note. Please try again.');
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        {isEdit ? 'Edit Session Note' : 'Create New Session Note'}
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
            <Input
              label="Session Date *"
              type="date"
              {...register('session_date')}
              error={errors.session_date?.message}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            className="input min-h-[200px]"
            {...register('notes')}
            placeholder="Enter session notes..."
          />
        </div>

        <div className="flex space-x-4">
          <Button type="submit" isLoading={loading}>
            {isEdit ? 'Update Session Note' : 'Create Session Note'}
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/session-notes')}
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
};


