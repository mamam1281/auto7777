'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../lib/auth';

const AdminLoginPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    site_id: '',
    password: '',
  });
  const [error, setError] = useState('');
  
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // 관리자 로그인 전용 엔드포인트 호출
      const response = await fetch(`http://localhost:8000/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '관리자 로그인 실패');
      }

      const data = await response.json();
      
      // 사용자 정보 가져오기
      const userResponse = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${data.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (userResponse.ok) {
        const userData = await userResponse.json();
        
        // 관리자 권한 확인
        if (userData.rank !== 'ADMIN' && userData.rank !== 'VIP') {
          throw new Error('관리자 권한이 없습니다');
        }
        
        login(data.access_token, userData);
        router.push('/admin');
      } else {
        throw new Error('사용자 정보를 가져오는데 실패했습니다');
      }
    } catch (err: any) {
      setError(err.message || '로그인 처리 중 오류가 발생했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="bg-gray-800 p-8 rounded-lg border border-gray-700 w-96">
        <h1 className="text-2xl font-bold text-white mb-6 text-center">
          관리자 로그인
        </h1>

        {error && (
          <div className="bg-red-600 text-white p-3 rounded mb-4 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="admin-site-id" className="block text-gray-300 text-sm mb-2">관리자 ID</label>
            <input
              id="admin-site-id"
              type="text"
              value={formData.site_id}
              onChange={(e) => setFormData({...formData, site_id: e.target.value})}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label htmlFor="admin-password" className="block text-gray-300 text-sm mb-2">비밀번호</label>
            <input
              id="admin-password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white py-3 px-4 rounded transition-colors"
          >
            {isLoading ? '처리 중...' : '관리자 로그인'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <a href="/auth" className="text-blue-400 hover:text-blue-300 text-sm">
            일반 로그인으로 돌아가기
          </a>
        </div>
      </div>
    </div>
  );
};

export default AdminLoginPage;
