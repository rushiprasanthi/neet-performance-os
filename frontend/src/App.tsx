import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LoginPage } from '@/pages/auth/LoginPage';
import { RegisterPage } from '@/pages/auth/RegisterPage'; // <-- Fixed: Added curly braces back
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { MainLayout } from '@/components/Layout/MainLayout';
import { DashboardPage } from '@/pages/dashboard/DashboardPage';
import { SubjectsPage } from '@/pages/content/SubjectsPage';
import { useAuthStore } from '@/store/authStore';
import { api } from '@/lib/api';
import { authApi } from '@/features/auth/api';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

const AppContent = () => {
  const [isInitializing, setIsInitializing] = useState(true);
  const { setTokens, setUser, logout } = useAuthStore();

  useEffect(() => {
    // Session Recovery: Attempt to revive auth state from HTTPOnly cookie on hard refresh
    const hydrateSession = async () => {
      try {
        const { data } = await api.post('/api/v1/auth/refresh');
        setTokens(data.access_token);
        
        // Utilize the typed API method for user fetching
        const user = await authApi.getMe();
        setUser(user);
      } catch (error) {
        // Clean slate if no valid session cookie exists
        logout();
      } finally {
        setIsInitializing(false);
      }
    };

    hydrateSession();
  }, [setTokens, setUser, logout]);

  if (isInitializing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 text-gray-500">
        Initializing application state...
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/content/subjects" element={<SubjectsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Route>
    </Routes>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;