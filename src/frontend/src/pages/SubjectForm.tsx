import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { subjectsApi, studiesApi } from '../api/endpoints';
import { Study } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { useStudyStore } from '../store/studyStore';

const subjectSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  middle_name: z.string().optional(),
  last_name: z.string().min(1, 'Last name is required'),
  date_of_birth: z.string().optional(),
  sex: z.string().optional(),
  ssn: z.string().optional(),
  race: z.string().optional(),
  ethnicity: z.string().optional(),
  county: z.string().optional(),
  zip: z.string().optional(),
  enrollment_status: z.string().optional(),
  study_ids: z.array(z.number()).optional(),
});

type SubjectFormData = z.infer<typeof subjectSchema>;

export const SubjectForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;
  const { selectedStudy } = useStudyStore();
  const [studies, setStudies] = useState<Study[]>([]);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<SubjectFormData>({
    resolver: zodResolver(subjectSchema),
    mode: 'onSubmit',
    reValidateMode: 'onChange',
    defaultValues: {
      study_ids: selectedStudy ? [selectedStudy.id] : [],
      enrollment_status: 'not_enrolled',
    },
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const studiesRes = await studiesApi.getAll({ limit: 1000 });
        setStudies(studiesRes.data.items);

        if (isEdit && id) {
          const subjectRes = await subjectsApi.getById(parseInt(id));
          const subject = subjectRes.data;
          setValue('first_name', subject.first_name);
          setValue('last_name', subject.last_name);
          setValue('middle_name', subject.middle_name || '');
          setValue('date_of_birth', subject.date_of_birth || '');
          setValue('sex', subject.sex || '');
          setValue('ssn', subject.ssn || '');
          setValue('race', subject.race || '');
          setValue('ethnicity', subject.ethnicity || '');
          setValue('county', subject.county || '');
          setValue('zip', subject.zip || '');
          setValue('enrollment_status', subject.enrollment_status || 'not_enrolled');
        } else if (selectedStudy) {
          setValue('study_ids', [selectedStudy.id]);
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    };
    fetchData();
  }, [id, isEdit, setValue, selectedStudy]);

  const onSubmit = async (data: SubjectFormData) => {
    setLoading(true);
    try {
      // handleSubmit only calls this if validation passes, so data is valid
      const submitData: any = {
        first_name: data.first_name,
        last_name: data.last_name,
        middle_name: data.middle_name || undefined,
        date_of_birth: data.date_of_birth || undefined,
        sex: data.sex || undefined,
        ssn: data.ssn || undefined,
        race: data.race || undefined,
        ethnicity: data.ethnicity || undefined,
        county: data.county || undefined,
        zip: data.zip || undefined,
        enrollment_status: data.enrollment_status || undefined,
      };

      if (isEdit && id) {
        await subjectsApi.update(parseInt(id), submitData);
      } else {
        // Include study_ids in the create request
        const createData = {
          ...submitData,
          study_ids: data.study_ids || [],
        };
        await subjectsApi.create(createData);
      }
      navigate('/subjects');
    } catch (error: any) {
      console.error('Failed to save subject:', error);
      alert(error.response?.data?.detail || 'Failed to save subject. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const selectedStudyIds = watch('study_ids') || [];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        {isEdit ? 'Edit Subject' : 'Create New Subject'}
      </h1>

      <form onSubmit={handleSubmit(onSubmit)} className="card space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="First Name *"
            {...register('first_name')}
            error={errors.first_name?.message}
          />
          <Input
            label="Last Name *"
            {...register('last_name')}
            error={errors.last_name?.message}
          />
          <Input
            label="Middle Name"
            {...register('middle_name')}
            error={errors.middle_name?.message}
          />
          <Input
            label="Date of Birth"
            type="date"
            {...register('date_of_birth')}
            error={errors.date_of_birth?.message}
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sex
            </label>
            <select className="input" {...register('sex')}>
              <option value="">Select...</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
          <Input
            label="SSN"
            {...register('ssn')}
            placeholder="XXX-XX-XXXX"
            error={errors.ssn?.message}
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Race <span className="text-gray-500 text-xs">(FDA Required)</span>
            </label>
            <select className="input" {...register('race')}>
              <option value="">Select...</option>
              <option value="American Indian or Alaska Native">American Indian or Alaska Native</option>
              <option value="Asian">Asian</option>
              <option value="Black or African American">Black or African American</option>
              <option value="Native Hawaiian or Other Pacific Islander">Native Hawaiian or Other Pacific Islander</option>
              <option value="White">White</option>
              <option value="More than one race">More than one race</option>
              <option value="Unknown or not reported">Unknown or not reported</option>
            </select>
            {errors.race && (
              <p className="mt-1 text-sm text-red-600">{errors.race.message}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ethnicity <span className="text-gray-500 text-xs">(FDA Required)</span>
            </label>
            <select className="input" {...register('ethnicity')}>
              <option value="">Select...</option>
              <option value="Hispanic or Latino">Hispanic or Latino</option>
              <option value="Not Hispanic or Latino">Not Hispanic or Latino</option>
              <option value="Unknown or not reported">Unknown or not reported</option>
            </select>
            {errors.ethnicity && (
              <p className="mt-1 text-sm text-red-600">{errors.ethnicity.message}</p>
            )}
          </div>
          <Input
            label="County"
            {...register('county')}
            error={errors.county?.message}
          />
          <Input
            label="ZIP Code"
            {...register('zip')}
            error={errors.zip?.message}
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Enrollment Status
            </label>
            <select className="input" {...register('enrollment_status')}>
              <option value="not_enrolled">Not Enrolled</option>
              <option value="enrolled">Enrolled</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Studies
          </label>
          <div className="space-y-2 max-h-40 overflow-y-auto border rounded p-2">
            {studies.map((study) => (
              <label key={study.id} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={selectedStudyIds.includes(study.id)}
                  onChange={(e) => {
                    const current = selectedStudyIds;
                    if (e.target.checked) {
                      setValue('study_ids', [...current, study.id]);
                    } else {
                      setValue('study_ids', current.filter(id => id !== study.id));
                    }
                  }}
                />
                <span className="text-sm">{study.name}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="flex space-x-4">
          <Button type="submit" isLoading={loading}>
            {isEdit ? 'Update Subject' : 'Create Subject'}
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/subjects')}
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
};

