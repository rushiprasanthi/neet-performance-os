export interface SubjectResponse {
  id: string;
  name: string;
  code: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SubjectListResponse {
  items: SubjectResponse[];
  total: number;
  skip: number;
  limit: number;
}

export interface SubjectCreate {
  name: string;
  code: string;
  description?: string;
}