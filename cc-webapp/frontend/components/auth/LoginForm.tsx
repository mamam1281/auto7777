'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface LoginFormProps {
  onSwitchToRegister: () => void;
  onSwitchToAdmin: () => void;
}

export default function LoginForm({ onSwitchToRegister, onSwitchToAdmin }: LoginFormProps) {
  const router = useRouter();
  const [formData, setFormData] = useState({
    nickname: '',
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
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        router.push('/dashboard');
      } else {
        setError(data.detail || '로그인에 실패했습니다.');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('네트워크 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* 🎮 플랫폼 타이틀 */}
      <div className="auth-header">
        <div className="game-platform-logo">🎮</div>
        <div className="game-platform-title">Casino Club</div>
        <div className="game-platform-subtitle">섹시한 핫핑크 다크 테마</div>
      </div>

      <div style={{ flex: 1 }}></div>
      
      <div className="login-message">다시 오신 것을 환영합니다</div>
      <div className="login-help">게임에 로그인하여 시작하세요</div>
      
      <form className="auth-form" onSubmit={handleSubmit}>
        {error && <div className="auth-error">{error}</div>}
        
        <div className="form-group">
          <label htmlFor="nickname" className="form-label">
            닉네임
          </label>
          <input
            type="text"
            id="nickname"
            name="nickname"
            value={formData.nickname}
            onChange={handleChange}
            className="form-input"
            placeholder="닉네임을 입력하세요"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="password" className="form-label">
            비밀번호
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="form-input"
            placeholder="비밀번호를 입력하세요"
            required
            disabled={isLoading}
          />
        </div>

        <button 
          type="submit" 
          className="auth-button primary" 
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="loading-spinner"></span>
              로그인 중...
            </>
          ) : (
            '🔥 로그인'
          )}
        </button>
      </form>

      {/* 🔄 전환 버튼들 */}
      <div className="auth-switches">
        <button 
          type="button" 
          className="auth-link"
          onClick={onSwitchToRegister}
          disabled={isLoading}
        >
          계정이 없으신가요? <span className="link-accent">회원가입</span>
        </button>
        
        <button 
          type="button" 
          className="auth-link admin-link"
          onClick={onSwitchToAdmin}
          disabled={isLoading}
        >
          👑 관리자 로그인
        </button>
      </div>
    </>
  );
}
