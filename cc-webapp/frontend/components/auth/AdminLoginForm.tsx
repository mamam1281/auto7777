'use client';

import { useState } from 'react';

interface AdminLoginFormProps {
  onAdminLogin: (adminId: string, password: string) => void;
  onSwitchToLogin: () => void;
  isLoading: boolean;
  error: string;
}

export default function AdminLoginForm({ onAdminLogin, onSwitchToLogin, isLoading, error }: AdminLoginFormProps) {
  const [adminId, setAdminId] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (adminId.trim() && password.trim()) {
      onAdminLogin(adminId.trim(), password.trim());
    }
  };

  return (
    <>
      <div className="auth-header">
        <div className="auth-logo">
          🔐
        </div>
        <h1 className="auth-title">관리자 로그인</h1>
        <p className="auth-subtitle">시스템 관리자 전용 접속</p>
      </div>

      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="auth-form-group">
          <label htmlFor="adminId" className="auth-label">
            관리자 ID
          </label>
          <input
            type="text"
            id="adminId"
            className="auth-input"
            placeholder="관리자 ID를 입력하세요"
            value={adminId}
            onChange={(e) => setAdminId(e.target.value)}
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
          className="auth-button auth-button-secondary"
          disabled={isLoading || !adminId.trim() || !password.trim()}
        >
          {isLoading && <span className="auth-loading"></span>}
          {isLoading ? '로그인 중...' : '관리자 로그인'}
        </button>

        <div className="auth-divider">
          <span>또는</span>
        </div>

        <button
          type="button"
          className="auth-button"
          onClick={onSwitchToLogin}
          disabled={isLoading}
        >
          일반 사용자 로그인
        </button>

        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
          <small style={{ color: 'rgba(246, 229, 246, 0.6)', fontSize: '0.75rem' }}>
            ⚠️ 관리자만 접근 가능합니다<br />
            임시 계정: admin / admin123
          </small>
        </div>
      </form>
    </>
  );
}
