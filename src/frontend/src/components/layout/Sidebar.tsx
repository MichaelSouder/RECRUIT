import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { StudySelector } from './StudySelector';
import {
  LayoutDashboard,
  Users,
  BookOpen,
  FileText,
  BarChart3,
  Calendar,
  Settings,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const { user } = useAuthStore();
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Set/clear admin context in sessionStorage based on current route
  useEffect(() => {
    if (location.pathname === '/admin') {
      sessionStorage.setItem('fromAdmin', 'true');
    } else if (location.pathname.startsWith('/studies') && (location.state as any)?.fromAdmin) {
      sessionStorage.setItem('fromAdmin', 'true');
    } else if (!location.pathname.startsWith('/studies') && !location.pathname.startsWith('/admin')) {
      sessionStorage.removeItem('fromAdmin');
    }
  }, [location.pathname, location.state]);

  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/subjects', label: 'Subjects', icon: Users },
    { to: '/studies', label: 'Studies', icon: BookOpen },
    { to: '/session-notes', label: 'Session Notes', icon: FileText },
    { to: '/assessments', label: 'Assessments', icon: BarChart3 },
    { to: '/calendar', label: 'Calendar', icon: Calendar },
  ];

  const adminItems = [
    { to: '/admin', label: 'Admin', icon: Settings },
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    // Check if we have admin context from state or sessionStorage
    const hasAdminContext = (location.state as any)?.fromAdmin === true || sessionStorage.getItem('fromAdmin') === 'true';
    
    // Special handling for Admin: highlight if on /admin or if we have admin context
    if (path === '/admin') {
      return location.pathname === '/admin' || hasAdminContext;
    }
    // Don't highlight other nav items when we have admin context
    if (hasAdminContext) {
      return false;
    }
    return location.pathname.startsWith(path);
  };

  const NavItem = ({ to, label, icon: Icon, onClick }: { to: string; label: string; icon: any; onClick?: () => void }) => {
    const active = isActive(to);
    return (
      <Link
        to={to}
        onClick={onClick}
        className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
          active
            ? 'bg-primary-50 text-primary-700'
            : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
        }`}
        title={isCollapsed ? label : undefined}
      >
        <Icon className="w-5 h-5 flex-shrink-0" />
        {!isCollapsed && <span>{label}</span>}
      </Link>
    );
  };

  return (
    <aside
      className={`bg-white border-r border-gray-200 flex flex-col transition-all duration-300 h-full ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
        {!isCollapsed && (
          <Link to="/" className="text-xl font-bold text-primary-600">
            RECRUIT
          </Link>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Study Selector */}
      {!isCollapsed && (
        <div className="px-4 py-4 border-b border-gray-200">
          <StudySelector />
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavItem key={item.to} to={item.to} label={item.label} icon={item.icon} />
        ))}
        
        {(user?.is_superuser || user?.role === 'admin') && (
          <div className="pt-4 mt-4 border-t border-gray-200">
            {adminItems.map((item) => (
              <NavItem key={item.to} to={item.to} label={item.label} icon={item.icon} />
            ))}
          </div>
        )}
      </nav>
    </aside>
  );
};

