'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

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
      
      <div style={{ flex: 1 }}></div>
      
      <div className="game-platform-title">Game Platform</div>
      <div className="game-platform-subtitle">차세대 게임 경험의 시작</div>
      
      <div className="login-message">다시 오신 것을 환영합니다</div>
      <div className="login-help">게임에 로그인하여 시작하세요</div>
      
      <form className="auth-form" onSubmit={handleSubmit}>
        {error && <div className="auth-error">{error}</div>}
        
        <div className="form-group">
          <label htmlFor="siteId" className="form-label">
            사이트ID
          </label>
          <div className="email-input-container">
            <User className="email-icon" size={16} />
            <input
              type="text"
              id="siteId"
              className="form-input email-input"
              value={siteId}
              onChange={(e) => setSiteId(e.target.value)}
              placeholder="사이트ID를 입력하세요"
              required
              disabled={isLoading}
              autoComplete="username"
            />
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="password" className="form-label">
            비밀번호
          </label>
          <div className="email-input-container">
            <Lock className="email-icon" size={16} />
            <input
              type={showPassword ? "text" : "password"}
              id="password"
              className="form-input email-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="비밀번호를 입력하세요"
              required
              disabled={isLoading}
              autoComplete="current-password"
            />
          </div>
        </div>
        
        <button
          type="submit"
          className="auth-button"
          disabled={isLoading || !siteId || !password}
        >
          {isLoading ? (
            <>
              <Loader2 size={18} className="animate-spin mr-2" />
              로그인 중...
            </>
          ) : (
            <>
              <LogIn size={18} />
              로그인
            </>
          )}
        </button>
      </form>
      
      <div style={{ flex: 1 }}></div>
      
      <div className="bottom-info">
        안전하고 신뢰할 수 있는 게임 플랫폼
      </div>
    </div>
  );
}
