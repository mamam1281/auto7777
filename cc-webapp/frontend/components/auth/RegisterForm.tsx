'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
}

export default function RegisterForm({ onSwitchToLogin }: RegisterFormProps) {
  const router = useRouter();
  const [formData, setFormData] = useState({
    invite_code: '',
    site_id: '',
    nickname: '',
    password: '',
    phone_number: ''
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
      // 🔧 간단한 초대코드 확인 (로컬 체크)
      const validInviteCodes = ['6974', '6969', '2560'];
      if (!validInviteCodes.includes(formData.invite_code)) {
        setError('유효하지 않은 초대코드입니다. (6974, 6969, 2560 중 하나를 입력하세요)');
        return;
      }

      // 회원가입 진행
      console.log('🚀 회원가입 요청 시작:', formData);
      const signupResponse = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      console.log('📡 API 응답 상태:', signupResponse.status);
      const data = await signupResponse.json();
      console.log('📦 API 응답 데이터:', data);

      if (signupResponse.ok) {
        // 🔒 토큰과 사용자 정보를 localStorage에 저장
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('userNickname', formData.nickname);
        localStorage.setItem('user', JSON.stringify({
          nickname: formData.nickname,
          invite_code: formData.invite_code,
          site_id: formData.site_id
        }));
        
        console.log('✅ 회원가입 성공! 메인 페이지로 이동:', {
          nickname: formData.nickname,
          token: data.access_token
        });
        
        // 🏠 메인 페이지(홈 대시보드)로 리다이렉트
        router.push('/');
      } else {
        // 🔧 API 오류 응답 처리 개선
        let errorMessage = '회원가입에 실패했습니다.';
        
        if (data.detail) {
          if (Array.isArray(data.detail)) {
            // Pydantic validation 오류 처리
            errorMessage = data.detail.map((err: any) => err.msg).join(', ');
          } else if (typeof data.detail === 'string') {
            errorMessage = data.detail;
          }
        }
        
        setError(errorMessage);
      }
    } catch (error) {
      console.error('Register error:', error);
      setError('네트워크 오류가 발생했습니다. 백엔드 서버를 확인해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* 🎮 플랫폼 타이틀 */}
      <div className="auth-header">
        <div className="game-platform-title">모델카지노</div>
        <div className="game-platform-subtitle">새로운 모험의 시작</div>
      </div>

      <div style={{ flex: 1 }}></div>

      <div className="register-message" style={{ textAlign: 'center' }}> 회원님을 환영합니다</div>
      <div className="register-help" style={{ textAlign: 'center' }}>초대코드로 가입하여 특별한 혜택을 받으세요</div>

      <form className="auth-form register-form" onSubmit={handleSubmit}>
        {error && <div className="auth-error">{error}</div>}

        <div className="form-group">
          <label htmlFor="invite_code" className="form-label">
            초대코드 <span className="required">*</span>
          </label>
          <input
            type="text"
            id="invite_code"
            name="invite_code"
            value={formData.invite_code}
            onChange={handleChange}
            className="form-input invite-input"
            placeholder="초대코드를 입력하세요"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="site_id" className="form-label">
            사이트ID <span className="required">*</span>
          </label>
          <input
            type="text"
            id="site_id"
            name="site_id"
            value={formData.site_id}
            onChange={handleChange}
            className="form-input"
            placeholder="사이트ID를 입력하세요"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="nickname" className="form-label">
            닉네임 <span className="required">*</span>
          </label>
          <input
            type="text"
            id="nickname"
            name="nickname"
            value={formData.nickname}
            onChange={handleChange}
            className="form-input"
            placeholder="게임에서 사용할 닉네임"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="phone_number" className="form-label">
            전화번호 <span className="required">*</span>
          </label>
          <input
            type="tel"
            id="phone_number"
            name="phone_number"
            value={formData.phone_number}
            onChange={handleChange}
            className="form-input"
            placeholder="전화번호를 입력하세요 (예: 010-1234-5678)"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="password" className="form-label">
            비밀번호 <span className="required">*</span>
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="form-input"
            placeholder="안전한 비밀번호를 입력하세요"
            required
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          className="auth-button primary register-button luxury-gradient"
          disabled={isLoading || !formData.invite_code || !formData.site_id || !formData.nickname || !formData.phone_number || !formData.password}
        >
          {isLoading ? (
            <>
              <span className="loading-spinner"></span>
              가입 중...
            </>
          ) : (
            <span className="luxury-text">즐거움의시작 모델카지노</span>
          )}
        </button>
      </form>

      {/* 🔄 전환 버튼들 */}
      <div className="auth-switches">
        <button
          type="button"
          className="auth-link"
          onClick={onSwitchToLogin}
          disabled={isLoading}
        >
          이미 계정이 있으신가요? <span className="link-accent">로그인</span>
        </button>
      </div>
    </>
  );
}
