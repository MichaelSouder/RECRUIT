import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { studiesApi } from '../api/endpoints';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';

const studySchema = z.object({
  name: z.string().min(1, 'Study name is required'),
  description: z.string().optional(),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
  status: z.string().optional(),
  principal_investigator_id: z.number().optional().nullable(),
});

type StudyFormData = z.infer<typeof studySchema>;

interface Researcher {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

export const StudyForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;
  const [loading, setLoading] = useState(false);
  const [researchers, setResearchers] = useState<Researcher[]>([]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<StudyFormData>({
    resolver: zodResolver(studySchema),
    mode: 'onSubmit',
    reValidateMode: 'onChange',
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch researchers for PI dropdown
        const researchersRes = await studiesApi.getResearchers();
        setResearchers(researchersRes.data);

        // Fetch study data if editing
        if (isEdit && id) {
          const response = await studiesApi.getById(parseInt(id));
          const study = response.data;
          setValue('name', study.name);
          setValue('description', study.description || '');
          setValue('start_date', study.start_date || '');
          setValue('end_date', study.end_date || '');
          setValue('status', study.status || 'active');
          setValue('principal_investigator_id', study.principal_investigator_id || null);
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    };
    fetchData();
  }, [id, isEdit, setValue]);

  const onSubmit = async (data: StudyFormData) => {
    setLoading(true);
    try {
      // handleSubmit only calls this if validation passes, so data is valid
      const submitData: any = {
        name: data.name,
        description: data.description,
        start_date: data.start_date || undefined,
        end_date: data.end_date || undefined,
        status: data.status || 'active',
        principal_investigator_id: data.principal_investigator_id || undefined,
      };

      if (isEdit && id) {
        await studiesApi.update(parseInt(id), submitData);
      } else {
        await studiesApi.create(submitData);
      }
      navigate('/studies');
    } catch (error: any) {
      console.error('Failed to save study:', error);
      alert(error.response?.data?.detail || 'Failed to save study. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        {isEdit ? 'Edit Study' : 'Create New Study'}
      </h1>

      <form onSubmit={handleSubmit(onSubmit)} className="card space-y-6">
        <Input
          label="Study Name *"
          {...register('name')}
          error={errors.name?.message}
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            className="input min-h-[100px]"
            {...register('description')}
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="Start Date"
            type="date"
            {...register('start_date')}
            error={errors.start_date?.message}
          />
          <Input
            label="End Date"
            type="date"
            {...register('end_date')}
            error={errors.end_date?.message}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select className="input" {...register('status')}>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="paused">Paused</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Principal Investigator
            </label>
            <select
              className="input"
              {...register('principal_investigator_id', { valueAsNumber: true })}
            >
              <option value="">Select a PI...</option>
              {researchers.map((researcher) => (
                <option key={researcher.id} value={researcher.id}>
                  {researcher.full_name || researcher.email}
                </option>
              ))}
            </select>
            {errors.principal_investigator_id && (
              <p className="mt-1 text-sm text-red-600">{errors.principal_investigator_id.message}</p>
            )}
          </div>
        </div>

        <div className="flex space-x-4">
          <Button type="submit" isLoading={loading}>
            {isEdit ? 'Update Study' : 'Create Study'}
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/studies')}
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
};

