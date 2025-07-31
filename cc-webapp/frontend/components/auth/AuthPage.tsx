'use client';

import { useState, useEffect } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

type AuthMode = 'loading' | 'login' | 'register';

export default function AuthPage() {
  const [authMode, setAuthMode] = useState<AuthMode>('loading');

  // 첫 접속시 로딩 → 로그인 → 회원가입 순서
  useEffect(() => {
    const timer = setTimeout(() => {
      setAuthMode('login');
    }, 1500); // 1.5초 로딩

    return () => clearTimeout(timer);
  }, []);

  const handleSwitchToRegister = () => {
    setAuthMode('register');
  };

  const handleSwitchToLogin = () => {
    setAuthMode('login');
  };

  // 로딩 화면
  if (authMode === 'loading') {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="loading-screen">
            <div className="game-platform-title">모델카지노</div>
            <div className="loading-spinner-big"></div>
            <div className="loading-text">로딩 중...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        {authMode === 'login' && (
          <LoginForm
            onSwitchToRegister={handleSwitchToRegister}
          />
        )}

        {authMode === 'register' && (
          <RegisterForm
            onSwitchToLogin={handleSwitchToLogin}
          />
        )}
      </div>
    </div>
  );
}
