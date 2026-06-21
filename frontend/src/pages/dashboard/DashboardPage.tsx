import { useAuthStore } from '@/store/authStore';

export const DashboardPage = () => {
  const { user } = useAuthStore();

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Performance Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Metric Cards - Aligning with Architecture Blueprint F027 */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500">Performance Score</h3>
          <p className="mt-2 text-3xl font-bold text-gray-900">--</p>
          <p className="text-sm text-gray-500 mt-1">Take a test to generate score</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500">Active Recovery Missions</h3>
          <p className="mt-2 text-3xl font-bold text-indigo-600">0</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500">Tests Attempted</h3>
          <p className="mt-2 text-3xl font-bold text-gray-900">0</p>
        </div>
      </div>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <h2 className="text-xl font-medium text-gray-900 mb-2">Welcome, {user?.first_name || 'Student'}!</h2>
        <p className="text-gray-500 max-w-lg mx-auto">
          Your diagnostic intelligence engine is ready. Navigate to the Mock Tests section to begin your first Full NEET Mock and generate your initial Weakness Heatmap.
        </p>
      </div>
    </div>
  );
};