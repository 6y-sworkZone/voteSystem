import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface Option {
  id: number;
  text: string;
  vote_count: number;
  percentage: number;
}

export interface Poll {
  id: number;
  title: string;
  description?: string;
  deadline: string;
  created_at: string;
  creator_id: number;
  options: Option[];
  total_votes: number;
  is_expired: boolean;
  has_voted: boolean;
  voted_option_id?: number;
}

export interface PollCreate {
  title: string;
  description?: string;
  deadline: string;
  options: { text: string }[];
}

export const authAPI = {
  register: (data: { username: string; email: string; password: string }) =>
    api.post<User>('/register', data),
  login: (data: { username: string; password: string }) =>
    api.post<{ access_token: string; token_type: string }>('/token', new URLSearchParams(data)),
  getCurrentUser: () => api.get<User>('/users/me'),
};

export const pollAPI = {
  createPoll: (data: PollCreate) => api.post<Poll>('/polls', data),
  getPolls: (sortBy: string = 'created_at', order: string = 'desc') =>
    api.get<Poll[]>('/polls', { params: { sort_by: sortBy, order } }),
  getPoll: (id: number) => api.get<Poll>(`/polls/${id}`),
  vote: (pollId: number, optionId: number) =>
    api.post(`/polls/${pollId}/vote`, { option_id: optionId }),
  deletePoll: (id: number) => api.delete(`/polls/${id}`),
};

export default api;
