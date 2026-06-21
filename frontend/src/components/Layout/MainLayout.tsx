import { Outlet, Link, useNavigate } from 'react-router-dom';
import { BookOpen, Home, LogOut, FileText } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { authApi } from '@/features/auth/api';

export const MainLayout = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } finally {
      logout();
      navigate('/login');
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200 flex items-center gap-2 text-indigo-600">
          <BookOpen size={24} />
          <span className="text-xl font-bold">NEET POS</span>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link to="/" className="flex items-center gap-3 px-3 py-2 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
            <Home size={20} />
            <span>Dashboard</span>
          </Link>
          <Link to="/tests" className="flex items-center gap-3 px-3 py-2 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
            <FileText size={20} />
            <span>Mock Tests</span>
          </Link>
          <Link to="/content/subjects" className="flex items-center gap-3 px-3 py-2 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
            <BookOpen size={20} />
            <span>Content Admin</span>
          </Link>
        </nav>
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-3 mb-4 px-3">
            <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold uppercase">
              {/* Added safe chaining to prevent null reference crash */}
              {user?.first_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
            </div>
            <div className="text-sm truncate">
              <p className="font-medium text-gray-900">{user?.first_name} {user?.last_name}</p>
              <p className="text-gray-500 truncate">{user?.email}</p>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
          >
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};