import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { Login } from '../pages/Login';
import { Dashboard } from '../pages/Dashboard';
import { Subjects } from '../pages/Subjects';
import { SubjectForm } from '../pages/SubjectForm';
import { Studies } from '../pages/Studies';
import { StudyForm } from '../pages/StudyForm';
import { StudyDetail } from '../pages/StudyDetail';
import { SessionNotes } from '../pages/SessionNotes';
import { SessionNoteForm } from '../pages/SessionNoteForm';
import { Assessments } from '../pages/Assessments';
import { AssessmentForm } from '../pages/AssessmentForm';
import { CalendarPage } from '../pages/Calendar';
import { Admin } from '../pages/Admin';
import { Profile } from '../pages/Profile';
import App from '../App';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <App />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'subjects',
        element: <Subjects />,
      },
      {
        path: 'subjects/new',
        element: <SubjectForm />,
      },
      {
        path: 'subjects/:id/edit',
        element: <SubjectForm />,
      },
      {
        path: 'studies',
        element: <Studies />,
      },
      {
        path: 'studies/new',
        element: <StudyForm />,
      },
      {
        path: 'studies/:id/edit',
        element: <StudyForm />,
      },
      {
        path: 'studies/:id',
        element: <StudyDetail />,
      },
      {
        path: 'session-notes',
        element: <SessionNotes />,
      },
      {
        path: 'session-notes/new',
        element: <SessionNoteForm />,
      },
      {
        path: 'session-notes/:id/edit',
        element: <SessionNoteForm />,
      },
      {
        path: 'assessments',
        element: <Assessments />,
      },
      {
        path: 'assessments/new',
        element: <AssessmentForm />,
      },
      {
        path: 'assessments/:id/edit',
        element: <AssessmentForm />,
      },
      {
        path: 'calendar',
        element: <CalendarPage />,
      },
      {
        path: 'admin',
        element: <Admin />,
      },
      {
        path: 'profile',
        element: <Profile />,
      },
    ],
  },
]);

