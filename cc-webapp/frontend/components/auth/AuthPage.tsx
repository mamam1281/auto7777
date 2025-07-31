'use client';

import { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import AdminLoginForm from './AdminLoginForm';

type AuthMode = 'login' | 'register' | 'admin';

export default function AuthPage() {
  const [authMode, setAuthMode] = useState<AuthMode>('login');

  const handleSwitchToRegister = () => {
    setAuthMode('register');
  };

  const handleSwitchToLogin = () => {
    setAuthMode('login');
  };

  const handleSwitchToAdmin = () => {
    setAuthMode('admin');
  };

  return (
    <div className="auth-container">
      {/* 🌌 우주 배경 효과 */}
      <div className="space-background"></div>
      
      {/* 🎮 메인 인증 카드 */}
      <div className="auth-card">
        {authMode === 'login' && (
          <LoginForm 
            onSwitchToRegister={handleSwitchToRegister}
            onSwitchToAdmin={handleSwitchToAdmin}
          />
        )}
        
        {authMode === 'register' && (
          <RegisterForm 
            onSwitchToLogin={handleSwitchToLogin}
          />
        )}
        
        {authMode === 'admin' && (
          <AdminLoginForm 
            onSwitchToLogin={handleSwitchToLogin}
          />
        )}
      </div>
      
      {/* 🔥 핫핑크 글로우 효과 */}
      <div className="hot-pink-glow"></div>
    </div>
  );
}
