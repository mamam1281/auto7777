'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../lib/auth';

const AuthPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleTestLogin = () => {
    setIsLoading(true);
    
    // 테스트용 관리자 사용자 데이터
    const testAdminUser = {
      id: 1,
      nickname: 'TestAdmin',
      email: 'admin@test.com',
      current_rank: 'ADMIN'
    };
    
    const testToken = 'test-admin-token-123';
    
    // 인증 정보 설정
    login(testToken, testAdminUser);
    
    setTimeout(() => {
      setIsLoading(false);
      router.push('/admin');
    }, 1000);
  };

  const handleTestUserLogin = () => {
    setIsLoading(true);
    
    // 테스트용 일반 사용자 데이터
    const testUser = {
      id: 2,
      nickname: 'TestUser',
      email: 'user@test.com',
      current_rank: 'BASIC'
    };
    
    const testToken = 'test-user-token-456';
    
    // 인증 정보 설정
    login(testToken, testUser);
    
    setTimeout(() => {
      setIsLoading(false);
      router.push('/');
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="bg-gray-800 p-8 rounded-lg border border-gray-700 w-96">
        <h1 className="text-2xl font-bold text-white mb-6 text-center">테스트 로그인</h1>
        
        <div className="space-y-4">
          <button
            onClick={handleTestLogin}
            disabled={isLoading}
            className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white py-3 px-4 rounded-lg transition-colors"
          >
            {isLoading ? '로그인 중...' : '관리자로 로그인'}
          </button>
          
          <button
            onClick={handleTestUserLogin}
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-3 px-4 rounded-lg transition-colors"
          >
            {isLoading ? '로그인 중...' : '일반 사용자로 로그인'}
          </button>
        </div>
        
        <div className="mt-6 text-center text-gray-400 text-sm">
          <p>테스트용 로그인 페이지</p>
          <p>관리자로 로그인하면 관리자 기능에 접근할 수 있습니다.</p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
