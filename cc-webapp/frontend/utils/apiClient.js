import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // 백엔드 API 기본 URL
});

// 요청 인터셉터 - 토큰 자동 추가
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 에러 처리
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료시 로그아웃
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

// API 메소드들
apiClient.checkInviteCode = async (code) => {
  const response = await apiClient.post('/auth/verify-invite', { code });
  return response.data;
};

apiClient.signup = async (userData) => {
  const response = await apiClient.post('/auth/signup', userData);
  return response.data;
};

apiClient.login = async (credentials) => {
  const response = await apiClient.post('/auth/login', credentials);
  return response.data;
};

apiClient.getProfile = async () => {
  const response = await apiClient.get('/auth/me');
  return response.data;
};

export default apiClient;
