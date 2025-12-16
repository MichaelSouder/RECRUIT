import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../ui/Button';
import { LogOut, User } from 'lucide-react';

export const Header: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) return null;

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-end px-6 sticky top-0 z-40">
      <div className="flex items-center space-x-4">
        <Link
          to="/profile"
          className="flex items-center space-x-2 text-sm text-gray-700 hover:text-primary-600 transition-colors cursor-pointer"
        >
          <User className="w-4 h-4 flex-shrink-0" />
          <span className="truncate max-w-[200px]">{user?.full_name || user?.email}</span>
        </Link>
        <Button 
          variant="secondary" 
          onClick={handleLogout} 
          className="flex items-center space-x-2"
        >
          <LogOut className="w-4 h-4" />
          <span>Logout</span>
        </Button>
      </div>
    </header>
  );
};

