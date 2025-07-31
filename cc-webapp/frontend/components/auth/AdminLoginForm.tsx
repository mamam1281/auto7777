'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface AdminLoginFormProps {
  onSwitchToLogin: () => void;
}

export default function AdminLoginForm({ onSwitchToLogin }: AdminLoginFormProps) {
  const router = useRouter();
  const [formData, setFormData] = useState({
    admin_code: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (error) setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/admin/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('admin_token', data.access_token);
        localStorage.setItem('admin_user', JSON.stringify(data.user));
        router.push('/admin/dashboard');
      } else {
        setError(data.detail || '관리자 로그인에 실패했습니다.');
      }
    } catch (error) {
      console.error('Admin login error:', error);
      setError('네트워크 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* 👑 관리자 타이틀 */}
      <div className="auth-header admin-header">
        <div className="game-platform-logo admin-logo">👑</div>
        <div className="game-platform-title admin-title">Admin Portal</div>
        <div className="game-platform-subtitle admin-subtitle">관리자 전용 접근</div>
      </div>

      <div style={{ flex: 1 }}></div>
      
      <div className="admin-message">관리자 로그인</div>
      <div className="admin-help">시스템 관리를 위한 보안 로그인</div>
      
      <form className="auth-form admin-form" onSubmit={handleSubmit}>
        {error && <div className="auth-error admin-error">{error}</div>}
        
        <div className="form-group">
          <label htmlFor="admin_code" className="form-label admin-label">
            관리자 코드 <span className="required">*</span>
          </label>
          <input
            type="text"
            id="admin_code"
            name="admin_code"
            value={formData.admin_code}
            onChange={handleChange}
            className="form-input admin-input"
            placeholder="관리자 코드를 입력하세요"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="password" className="form-label admin-label">
            관리자 비밀번호 <span className="required">*</span>
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="form-input admin-input"
            placeholder="관리자 비밀번호를 입력하세요"
            required
            disabled={isLoading}
          />
        </div>

        <button 
          type="submit" 
          className="auth-button primary admin-button" 
          disabled={isLoading || !formData.admin_code || !formData.password}
        >
          {isLoading ? (
            <>
              <span className="loading-spinner"></span>
              로그인 중...
            </>
          ) : (
            '👑 관리자 로그인'
          )}
        </button>
      </form>

      {/* 보안 경고 */}
      <div className="admin-warning">
        <div className="warning-icon">⚠️</div>
        <div className="warning-text">
          관리자 계정은 시스템의 모든 기능에 접근할 수 있습니다. 
          보안을 위해 로그인 시도가 기록됩니다.
        </div>
      </div>

      {/* 🔄 전환 버튼들 */}
      <div className="auth-switches">
        <button 
          type="button" 
          className="auth-link admin-back-link"
          onClick={onSwitchToLogin}
          disabled={isLoading}
        >
          ← 일반 로그인으로 돌아가기
        </button>
      </div>
    </>
  );
}
