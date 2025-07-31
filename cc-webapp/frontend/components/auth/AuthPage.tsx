'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import AdminLoginForm from './AdminLoginForm';

type AuthMode = 'login' | 'signup' | 'admin';

export default function AuthPage() {
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (siteId: string, password: string) => {
    setIsLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          site_id: siteId,
          password: password
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '로그인에 실패했습니다');
      }
      
      const data = await response.json();
      console.log('로그인 성공', data);
      
      // JWT 토큰 저장
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
      }
      
      // 사용자 정보 가져오기
      const userResponse = await fetch(`${apiUrl}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      });
      
      if (userResponse.ok) {
        const userData = await userResponse.json();
        localStorage.setItem('user_info', JSON.stringify(userData));
      }
      
      setSuccess('로그인 성공! 환영합니다!');
      setTimeout(() => {
        router.push('/');
      }, 1500);
    } catch (error: any) {
      setError(error.message || '로그인에 실패했습니다.');
      console.error('로그인 실패', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (siteId: string, nickname: string, phoneNumber: string, password: string, inviteCode: string) => {
    setIsLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          site_id: siteId,
          nickname: nickname,
          phone_number: phoneNumber,
          password: password,
          invite_code: inviteCode
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '회원가입에 실패했습니다');
      }
      
      const data = await response.json();
      console.log('회원가입 성공', data);
      
      // JWT 토큰 저장
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
      }
      
      setSuccess('회원가입이 완료되었습니다! 환영합니다!');
      setTimeout(() => {
        router.push('/');
      }, 1500);
    } catch (error: any) {
      setError(error.message || '회원가입에 실패했습니다.');
      console.error('회원가입 실패', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdminLogin = async (adminId: string, password: string) => {
    setIsLoading(true);
    setError('');
    setSuccess('');
    
    try {
      // 관리자 로그인 로직 (임시)
      if (adminId === 'admin' && password === 'admin123') {
        localStorage.setItem('admin_token', 'admin-jwt-token');
        localStorage.setItem('user_role', 'admin');
        setSuccess('관리자 로그인 성공!');
        setTimeout(() => {
          router.push('/admin');
        }, 1500);
      } else {
        throw new Error('관리자 인증 정보가 올바르지 않습니다.');
      }
    } catch (error: any) {
      setError(error.message || '관리자 로그인에 실패했습니다.');
      console.error('관리자 로그인 실패', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className={`auth-form-wrapper ${authMode === 'admin' ? 'auth-admin' : ''}`}>
        {/* 탭 네비게이션 */}
        <div className="auth-tabs">
          <button 
            className={`auth-tab ${authMode === 'login' ? 'active' : ''}`}
            onClick={() => setAuthMode('login')}
          >
            로그인
          </button>
          <button 
            className={`auth-tab ${authMode === 'signup' ? 'active' : ''}`}
            onClick={() => setAuthMode('signup')}
          >
            회원가입
          </button>
          <button 
            className={`auth-tab ${authMode === 'admin' ? 'active' : ''}`}
            onClick={() => setAuthMode('admin')}
          >
            관리자
          </button>
        </div>

        {/* 에러/성공 메시지 */}
        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success">{success}</div>}

        {/* 로그인 폼 */}
        {authMode === 'login' && (
          <LoginForm 
            onLogin={handleLogin}
            onSwitchToSignup={() => setAuthMode('signup')}
            isLoading={isLoading}
            error={error}
          />
        )}

        {/* 회원가입 폼 */}
        {authMode === 'signup' && (
          <RegisterForm 
            onRegister={handleRegister}
            onSwitchToLogin={() => setAuthMode('login')}
            isLoading={isLoading}
            error={error}
          />
        )}

        {/* 관리자 로그인 폼 */}
        {authMode === 'admin' && (
          <AdminLoginForm 
            onAdminLogin={handleAdminLogin}
            onSwitchToLogin={() => setAuthMode('login')}
            isLoading={isLoading}
            error={error}
          />
        )}
      </div>
    </div>
  );
}
