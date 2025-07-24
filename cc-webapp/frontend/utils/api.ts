import axios from 'axios';
import type { 
  User, 
  AdultContentGalleryItem, 
  GameResponse, 
  ContentUnlockResponse, 
  FlashOfferResponseItem,
  LoginRequest,
  RegisterRequest,
  ContentUnlockRequest,
  GamePlayRequest
} from '../types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use((config) => {
  const token = localStorage?.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage?.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (data: LoginRequest) => 
    apiClient.post<{ access_token: string; user: User }>('/auth/login', data),
  
  register: (data: RegisterRequest) => 
    apiClient.post<{ access_token: string; user: User }>('/auth/register', data),
  
  getCurrentUser: () => 
    apiClient.get<User>('/auth/me'),
};

export const gameAPI = {
  getGames: () => 
    apiClient.get<GameResponse[]>('/games/'),
  
  playGame: (data: GamePlayRequest) => 
    apiClient.post('/games/play', data),
};

export const adultContentAPI = {
  getGallery: () => 
    apiClient.get<{ items: AdultContentGalleryItem[] }>('/adult-content/gallery'),
  
  unlockContent: (data: ContentUnlockRequest) => 
    apiClient.post<ContentUnlockResponse>('/adult-content/unlock', data),
  
  getFlashOffers: () => 
    apiClient.get<{ offers: FlashOfferResponseItem[] }>('/adult-content/flash-offers'),
};

export default apiClient;
