'use client';

import { useState } from 'react';
import { User, Phone, ArrowRight, ArrowLeft, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface RegisterFormProps {
  onRegister?: (nickname: string, phoneNumber: string) => void;
  onSwitchToLogin?: () => void;
  isLoading?: boolean;
  error?: string;
}

export default function RegisterForm({ 
  onRegister, 
  onSwitchToLogin,
  isLoading: propIsLoading = false, 
  error: propError = '' 
}: RegisterFormProps) {
  const [step, setStep] = useState<1 | 2>(1);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [nickname, setNickname] = useState('');
  const [isLoading, setIsLoading] = useState(propIsLoading);
  const [error, setError] = useState(propError);
  const router = useRouter();

  const validatePhoneNumber = (phone: string) => {
    // 한국 전화번호 형식 검증 (010-0000-0000 또는 01000000000)
    const phoneRegex = /^010-?\d{4}-?\d{4}$/;
    return phoneRegex.test(phone.replace(/[^0-9-]/g, ''));
  };

  const handleNextStep = () => {
    if (phoneNumber && validatePhoneNumber(phoneNumber)) {
      setStep(2);
    } else {
      setError('유효한 전화번호를 입력해주세요 (예: 010-1234-5678)');
    }
  };

  const handlePrevStep = () => {
    setStep(1);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (onRegister) {
      onRegister(nickname, phoneNumber);
    } else {
      setIsLoading(true);
      try {
        // 가입 성공 시뮬레이션 (실제로는 API 호출)
        await new Promise(resolve => setTimeout(resolve, 1000));
        console.log('회원가입 성공', { phoneNumber, nickname });
        
        // 회원가입 후 메인 페이지로 이동
        router.push('/games');
      } catch (error) {
        setError('회원가입에 실패했습니다. 다시 시도해주세요.');
        console.error('회원가입 실패', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="auth-content register-content">
      <div className="auth-header-simple">
        <div 
          className="auth-tab inactive" 
          onClick={onSwitchToLogin}
          style={{ cursor: 'pointer' }}
        >
          로그인
        </div>
        <div className="auth-tab active">회원가입</div>
      </div>
      
      <div style={{ flex: 0.5 }}></div>
      
      <div className="game-platform-title">Game Platform</div>
      <div className="game-platform-subtitle">차세대 게임 경험의 시작</div>
      
      {/* 진행 상태 표시 */}
      <div className="progress-container">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: step === 1 ? '50%' : '100%' }}
          ></div>
        </div>
        <div className="progress-step">
          <span className="progress-step-text">
            {step === 1 ? '1/2 단계' : '2/2 단계'}
          </span>
        </div>
      </div>
      
      {step === 1 ? (
        <>
          <div className="signup-title">계정 만들기</div>
          <div className="signup-subtitle">새로운 게임 여정을 시작하세요</div>
          
          <div className="email-icon-container">
            <div className="email-icon">
              <Phone size={24} />
            </div>
          </div>
          
          <div className="simplified-form">
            <div className="form-group">
              <label htmlFor="phoneNumber" className="form-label">전화번호 입력 (사이트 ID)</label>
              <div className="email-input-container">
                <Phone className="email-icon" size={16} />
                <input
                  type="tel"
                  id="phoneNumber"
                  className="form-input email-input"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="010-1234-5678"
                  required
                  disabled={isLoading}
                  autoComplete="tel"
                />
              </div>
              {error && <div className="field-error">{error}</div>}
            </div>
            
            <button
              type="button"
              className="auth-button"
              onClick={handleNextStep}
              disabled={isLoading || !phoneNumber}
            >
              <span>다음</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="signup-title">닉네임 입력</div>
          <div className="signup-subtitle">게임에서 사용할 닉네임을 입력하세요</div>
          
          <form className="auth-form simplified-form" onSubmit={handleSubmit}>
            {error && <div className="auth-error">{error}</div>}
            
            <div className="form-group">
              <label htmlFor="nickname" className="form-label">
                닉네임
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
                  maxLength={50}
                  autoComplete="username"
                />
              </div>
            </div>
            
            <div className="auth-page-buttons">
              <button
                type="button"
                className="auth-button auth-back-button"
                onClick={handlePrevStep}
                disabled={isLoading}
              >
                <ArrowLeft size={16} />
                <span>이전</span>
              </button>
              
              <button
                type="submit"
                className="auth-button auth-next-button"
                disabled={isLoading || !nickname}
              >
                {isLoading ? (
                  <>
                    <Loader2 size={18} className="animate-spin mr-2" />
                    가입 중...
                  </>
                ) : (
                  <>
                    <span>완료</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          </form>
        </>
      )}
      
      <div style={{ flex: 0.5 }}></div>
      
      <div className="bottom-info">
        안전하고 신뢰할 수 있는 게임 플랫폼
      </div>
    </div>
  );
}
