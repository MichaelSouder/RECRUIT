import React, { useEffect } from 'react';
import { useStudyStore } from '../../store/studyStore';
import { Filter } from 'lucide-react';

export const StudySelector: React.FC = () => {
  const { studies, selectedStudy, fetchStudies, setSelectedStudy } = useStudyStore();

  useEffect(() => {
    fetchStudies();
    // Restore selected study from localStorage
    const savedStudyId = localStorage.getItem('selectedStudyId');
    if (savedStudyId && studies.length > 0) {
      const study = studies.find(s => s.id === parseInt(savedStudyId));
      if (study) {
        setSelectedStudy(study);
      }
    }
  }, [studies.length]);

  return (
    <div className="w-full min-w-0">
      <label className="block text-xs font-medium text-gray-700 mb-1.5">Study Filter</label>
      <div className="flex items-center space-x-2 bg-gray-50 rounded-lg px-2 py-1.5 border border-gray-200 min-w-0">
        <Filter className="w-4 h-4 text-gray-500 flex-shrink-0" />
        <div className="flex-1 min-w-0 relative">
          <select
            className="w-full bg-transparent border-none text-sm py-0.5 focus:outline-none focus:ring-0 cursor-pointer appearance-none pr-6 truncate"
            value={selectedStudy?.id || ''}
            onChange={(e) => {
              const studyId = e.target.value ? parseInt(e.target.value) : null;
              const study = studyId ? studies.find(s => s.id === studyId) || null : null;
              setSelectedStudy(study);
            }}
            style={{ 
              textOverflow: 'ellipsis',
            }}
            title={selectedStudy ? selectedStudy.name : 'Select a study'}
          >
            <option value="">All Studies</option>
            {studies.map((study) => {
              const displayText = study.status !== 'active' 
                ? `${study.name} (${study.status})`
                : study.name;
              return (
                <option key={study.id} value={study.id}>
                  {displayText}
                </option>
              );
            })}
          </select>
        </div>
        {selectedStudy && (
          <button
            onClick={() => setSelectedStudy(null)}
            className="text-xs text-gray-500 hover:text-gray-700 px-1 flex-shrink-0"
            title="Clear filter"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
};

