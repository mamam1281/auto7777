'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

interface LoginFormProps {
  onLogin: (siteId: string, password: string) => void;
  onSwitchToSignup: () => void;
  isLoading: boolean;
  error: string;
}

export default function LoginForm({ 
  onLogin, 
  onSwitchToSignup,
  isLoading, 
  error
}: LoginFormProps) {
  const [siteId, setSiteId] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const searchParams = useSearchParams();
  
  // 테스트 계정 자동 입력
  useEffect(() => {
    const useTestAccount = searchParams?.get('test') === 'true';
    if (useTestAccount) {
      setSiteId('testuser');
      setPassword('testpass123');
    }
  }, [searchParams]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (siteId.trim() && password.trim()) {
      onLogin(siteId.trim(), password.trim());
    }
  };

  return (
    <>
      <div className="auth-header">
        <div className="auth-logo">
          🎰
        </div>
        <h1 className="auth-title">환영합니다!</h1>
        <p className="auth-subtitle">계정에 로그인하여 게임을 시작하세요</p>
      </div>

      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="auth-form-group">
          <label htmlFor="siteId" className="auth-label">
            사이트 ID
          </label>
          <input
            type="text"
            id="siteId"
            className="auth-input"
            placeholder="사이트 ID를 입력하세요"
            value={siteId}
            onChange={(e) => setSiteId(e.target.value)}
            required
            autoComplete="username"
            disabled={isLoading}
          />
        </div>

        <div className="auth-form-group">
          <label htmlFor="password" className="auth-label">
            비밀번호
          </label>
          <input
            type="password"
            id="password"
            className="auth-input"
            placeholder="비밀번호를 입력하세요"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            disabled={isLoading}
          />
        </div>

        <div className="auth-checkbox-group">
          <input
            type="checkbox"
            id="rememberMe"
            className="auth-checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            disabled={isLoading}
          />
          <label htmlFor="rememberMe" className="auth-checkbox-label">
            로그인 상태 유지
          </label>
        </div>

        <button
          type="submit"
          className="auth-button"
          disabled={isLoading || !siteId.trim() || !password.trim()}
        >
          {isLoading && <span className="auth-loading"></span>}
          {isLoading ? '로그인 중...' : '로그인'}
        </button>

        <div className="auth-divider">
          <span>아직 계정이 없으신가요?</span>
        </div>

        <button
          type="button"
          className="auth-button auth-button-secondary"
          onClick={onSwitchToSignup}
          disabled={isLoading}
        >
          회원가입
        </button>
      </form>
    </>
  );
}
