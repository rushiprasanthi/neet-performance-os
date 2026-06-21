import { api } from '@/lib/api';

// Redirect legacy imports to the centralized Axios instance
// This guarantees token interceptors and refresh queues are universally applied.
export default api;