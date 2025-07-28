'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../lib/auth';
import { authApi, LoginRequest, SignupRequest } from '../../lib/api-client';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    site_id: '',
    nickname: '',
    phone_number: '',
    password: '',
    invite_code: '',
  });
  
  const { login } = useAuth();
  const router = useRouter();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      if (isLogin) {
        // 로그인 요청
        const loginData: LoginRequest = {
          site_id: formData.site_id,
          password: formData.password,
        };
        
        const response = await authApi.login(loginData);
        
        // 인증 정보 설정
        login(response.access_token, response.user);
        
        // 관리자라면 관리자 페이지로, 아니면 메인 페이지로
        if (response.user.rank === 'ADMIN' || response.user.rank === 'SUPER_ADMIN') {
          router.push('/admin');
        } else {
          router.push('/');
        }
      } else {
        // 회원가입 요청
        const signupData: SignupRequest = {
          site_id: formData.site_id,
          nickname: formData.nickname,
          phone_number: formData.phone_number,
          password: formData.password,
          invite_code: formData.invite_code,
        };
        
        const response = await authApi.signup(signupData);
        
        // 인증 정보 설정
        login(response.access_token, response.user);
        
        // 메인 페이지로 이동
        router.push('/');
      }
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('알 수 없는 오류가 발생했습니다.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestLogin = async () => {
    setIsLoading(true);
    setError('');

    try {
      // 테스트용 관리자 계정으로 로그인
      const loginData: LoginRequest = {
        site_id: 'admin',
        password: 'admin123',
      };
      
      const response = await authApi.login(loginData);
      login(response.access_token, response.user);
      router.push('/admin');
    } catch (error) {
      if (error instanceof Error) {
        setError(`테스트 로그인 실패: ${error.message}`);
      } else {
        setError('테스트 로그인에 실패했습니다.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="bg-gray-800 p-8 rounded-lg border border-gray-700 w-96">
        <h1 className="text-2xl font-bold text-white mb-6 text-center">
          {isLogin ? '로그인' : '회원가입'}
        </h1>

        {error && (
          <div className="bg-red-600/20 border border-red-600 text-red-400 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-white text-sm font-medium mb-2">
              {isLogin ? '사이트 ID' : '사이트 ID (로그인용)'}
            </label>
            <input
              type="text"
              name="site_id"
              value={formData.site_id}
              onChange={handleInputChange}
              className="w-full bg-gray-700 text-white p-3 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
              placeholder={isLogin ? "사이트 ID를 입력하세요" : "로그인에 사용할 사이트 ID"}
              required
            />
          </div>

          {!isLogin && (
            <>
              <div>
                <label className="block text-white text-sm font-medium mb-2">
                  닉네임
                </label>
                <input
                  type="text"
                  name="nickname"
                  value={formData.nickname}
                  onChange={handleInputChange}
                  className="w-full bg-gray-700 text-white p-3 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                  placeholder="표시될 닉네임"
                  required
                />
              </div>

              <div>
                <label className="block text-white text-sm font-medium mb-2">
                  전화번호
                </label>
                <input
                  type="tel"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleInputChange}
                  className="w-full bg-gray-700 text-white p-3 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                  placeholder="010-1234-5678"
                  required
                />
              </div>
            </>
          )}

          <div>
            <label className="block text-white text-sm font-medium mb-2">
              비밀번호
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className="w-full bg-gray-700 text-white p-3 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
              placeholder="비밀번호 (4자 이상)"
              required
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-white text-sm font-medium mb-2">
                초대 코드
              </label>
              <input
                type="text"
                name="invite_code"
                value={formData.invite_code}
                onChange={handleInputChange}
                className="w-full bg-gray-700 text-white p-3 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                placeholder="초대 코드를 입력하세요"
                required
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-3 px-4 rounded-lg transition-colors"
          >
            {isLoading ? '처리 중...' : (isLogin ? '로그인' : '회원가입')}
          </button>
        </form>

        <div className="mt-4 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-blue-400 hover:text-blue-300 text-sm"
          >
            {isLogin ? '회원가입하기' : '로그인으로 돌아가기'}
          </button>
        </div>

        <div className="mt-6 pt-4 border-t border-gray-700">
          <button
            onClick={handleTestLogin}
            disabled={isLoading}
            className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors text-sm"
          >
            {isLoading ? '로그인 중...' : '테스트 관리자 로그인'}
          </button>
          <p className="text-gray-400 text-xs mt-2 text-center">
            개발용 테스트 계정 (site_id: admin, password: admin123)
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
