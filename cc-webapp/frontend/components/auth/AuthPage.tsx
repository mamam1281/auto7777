'use client';

import { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import PasswordResetForm from './PasswordResetForm';

type AuthMode = 'login' | 'signup' | 'reset-password';

export default function AuthPage() {
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSwitchMode = (mode: AuthMode) => {
    setError('');
    setAuthMode(mode);
  };

  const handleLogin = async (nickname: string, password: string) => {
    setIsLoading(true);
    setError('');
    
    try {
      // 실제로는 API 호출
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('로그인 성공', { nickname });
      // 로그인 처리
    } catch (err) {
      console.error('로그인 실패', err);
      setError('로그인에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (nickname: string, email: string) => {
    setIsLoading(true);
    setError('');
    
    try {
      // 실제로는 API 호출
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('회원가입 성공', { nickname, email });
      // 회원가입 처리
    } catch (err) {
      console.error('회원가입 실패', err);
      setError('회원가입에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (email: string) => {
    setIsLoading(true);
    setError('');
    
    try {
      // 실제로는 API 호출
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('비밀번호 재설정 요청 성공', { email });
      // 비밀번호 재설정 처리
    } catch (err) {
      console.error('비밀번호 재설정 요청 실패', err);
      setError('비밀번호 재설정 요청에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container popup-mode">
      {authMode === 'login' && (
        <LoginForm 
          onLogin={handleLogin}
          isLoading={isLoading}
          error={error}
          onSwitchToSignup={() => handleSwitchMode('signup')}
          onSwitchToResetPassword={() => handleSwitchMode('reset-password')}
        />
      )}
      
      {authMode === 'signup' && (
        <RegisterForm
          onRegister={handleRegister}
          isLoading={isLoading}
          error={error}
          onSwitchToLogin={() => handleSwitchMode('login')}
        />
      )}
      
      {authMode === 'reset-password' && (
        <PasswordResetForm
          onResetPassword={handleResetPassword}
          isLoading={isLoading}
          error={error}
          onSwitchToLogin={() => handleSwitchMode('login')}
        />
      )}
    </div>
  );
}
