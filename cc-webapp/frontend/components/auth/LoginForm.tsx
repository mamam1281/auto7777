'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '../../hooks/useUser';

interface LoginFormProps {
  onSwitchToRegister: () => void;
}

export default function LoginForm({ onSwitchToRegister }: LoginFormProps) {
  const router = useRouter();
  const { login } = useUser();
  const [formData, setFormData] = useState({
    site_id: '',
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
      // useUser hook의 login 메서드 사용
      await login({
        site_id: formData.site_id,
        password: formData.password
      });

      console.log('✅ 로그인 성공! 메인 페이지로 이동');

      // 🏠 메인 페이지(홈 대시보드)로 리다이렉트
      router.push('/');
    } catch (error: any) {
      console.error('❌ 로그인 실패:', error);

      // 에러 메시지 처리
      let errorMessage = '로그인에 실패했습니다.';
      if (error.message) {
        if (error.message.includes('Invalid credentials')) {
          errorMessage = '아이디 또는 비밀번호가 틀렸습니다.';
        } else {
          errorMessage = error.message;
        }
      }

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* 🎮 플랫폼 타이틀 */}
      <div className="auth-header">
        <div className="game-platform-title">모델카지노</div>
      </div>

      <div style={{ flex: 1 }}></div>

      <div className="login-message">다시 오신 것을 환영합니다</div>
      <div className="login-help">게임에 로그인하여 시작하세요</div>

      <form className="auth-form" onSubmit={handleSubmit}>
        {error && <div className="auth-error">{error}</div>}

        <div className="form-group">
          <label htmlFor="site_id" className="form-label">
            사이트 ID
          </label>
          <input
            type="text"
            id="site_id"
            name="site_id"
            value={formData.site_id}
            onChange={handleChange}
            className="form-input"
            placeholder="사이트 ID를 입력하세요 (예: WLTN001)"
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
      </div>
    </>
  );
}
