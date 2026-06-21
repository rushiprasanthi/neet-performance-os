export interface User {
  id: string;
  email: string;
  status: string;
  email_verified: boolean;
  first_name?: string | null;
  last_name?: string | null;
  avatar_url?: string | null;
  profile?: any;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}