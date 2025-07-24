'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { User, KeyRound, Loader2, LogIn } from 'lucide-react';

interface LoginFormProps {
  onLogin?: (nickname: string, password: string) => void;
  onSwitchToSignup?: () => void;
  onSwitchToResetPassword?: () => void;
  isLoading?: boolean;
  error?: string;
  autoFillTestAccount?: boolean;
}

export default function LoginForm({ 
  onLogin, 
  onSwitchToSignup,
  onSwitchToResetPassword,
  isLoading: propIsLoading = false, 
  error: propError = '',
  autoFillTestAccount = false 
}: LoginFormProps) {
  const [nickname, setNickname] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(propIsLoading);
  const [error, setError] = useState(propError);
  const searchParams = useSearchParams();
  const router = useRouter();
  
  // 테스트 계정 자동 입력
  useEffect(() => {
    const useTestAccount = autoFillTestAccount || searchParams?.get('test') === 'true';
    if (useTestAccount) {
      setNickname('test001');
      setPassword('1234');
    }
  }, [autoFillTestAccount, searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (onLogin) {
      onLogin(nickname, password);
    } else {
      setIsLoading(true);
      try {
        // 로그인 성공 시뮬레이션 (실제로는 API 호출)
        await new Promise(resolve => setTimeout(resolve, 1000));
        console.log('로그인 성공', { nickname });
        
        // 로그인 후 메인 페이지로 이동
        router.push('/games');
      } catch (error) {
        setError('로그인에 실패했습니다. 닉네임을 확인해주세요.');
        console.error('로그인 실패', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="auth-content">
      <div className="auth-header-simple">
        <div className="auth-tab active">로그인</div>
        <div 
          className="auth-tab inactive" 
          onClick={onSwitchToSignup}
          style={{ cursor: 'pointer' }}
        >
          회원가입
        </div>
      </div>
      
      <div style={{ flex: 1 }}></div>
      
      <div className="game-platform-title">Game Platform</div>
      <div className="game-platform-subtitle">차세대 게임 경험의 시작</div>
      
      <div className="login-message">다시 오신 것을 환영합니다</div>
      <div className="login-help">게임에 로그인하여 시작하세요</div>
      
      <form className="auth-form" onSubmit={handleSubmit}>
        {error && <div className="auth-error">{error}</div>}
        
        <div className="form-group">
          <label htmlFor="nickname" className="form-label">
            이메일 또는 닉네임
          </label>
          <div className="email-input-container">
            <User className="email-icon" size={16} />
            <input
              type="text"
              id="nickname"
              className="form-input email-input"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              placeholder="닉네임을 입력하세요"
              required
              disabled={isLoading}
            />
          </div>
        </div>
        
        <button
          type="submit"
          className="auth-button"
          disabled={isLoading}
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
