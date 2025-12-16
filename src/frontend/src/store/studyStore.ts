import { create } from 'zustand';
import { Study } from '../types';
import { studiesApi } from '../api/endpoints';

interface StudyState {
  studies: Study[];
  selectedStudy: Study | null;
  isLoading: boolean;
  fetchStudies: () => Promise<void>;
  setSelectedStudy: (study: Study | null) => void;
}

export const useStudyStore = create<StudyState>((set) => ({
  studies: [],
  selectedStudy: null,
  isLoading: false,

  fetchStudies: async () => {
    set({ isLoading: true });
    try {
      const response = await studiesApi.getAll({ limit: 1000 });
      set({ studies: response.data.items, isLoading: false });
    } catch (error) {
      console.error('Failed to fetch studies:', error);
      set({ isLoading: false });
    }
  },

  setSelectedStudy: (study: Study | null) => {
    set({ selectedStudy: study });
    if (study) {
      localStorage.setItem('selectedStudyId', study.id.toString());
    } else {
      localStorage.removeItem('selectedStudyId');
    }
  },
}));

// Initialize selected study from localStorage
const savedStudyId = localStorage.getItem('selectedStudyId');
if (savedStudyId) {
  // Will be set after studies are loaded
}


