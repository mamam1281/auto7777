'use client';

import { useEffect, useState } from 'react';
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
      <div className="w-full max-w-[420px] mx-auto min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-auto flex items-center justify-center">
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
    <div className="w-full max-w-[420px] mx-auto min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-auto">
      <div className="auth-card" style={{ padding: '20px', boxSizing: 'border-box' }}>
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
