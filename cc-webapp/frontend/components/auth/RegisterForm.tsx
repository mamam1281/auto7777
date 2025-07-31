'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '../../hooks/useUser';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
}

export default function RegisterForm({ onSwitchToLogin }: RegisterFormProps) {
  const router = useRouter();
  const { signup, checkInviteCode } = useUser();
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
      // 초대코드 확인
      const isValidCode = await checkInviteCode(formData.invite_code);
      if (!isValidCode) {
        setError('유효하지 않은 초대코드입니다.');
        return;
      }

      // 회원가입 진행
      console.log('🚀 회원가입 요청 시작:', formData);
      await signup(formData);

      console.log('✅ 회원가입 성공! 메인 페이지로 이동');

      // 🏠 메인 페이지(홈 대시보드)로 리다이렉트
      router.push('/');
    } catch (error: any) {
      console.error('❌ 회원가입 실패:', error);

      // 에러 메시지 처리
      let errorMessage = '회원가입에 실패했습니다.';
      if (error.message) {
        if (error.message.includes('Site ID already taken')) {
          errorMessage = '이미 사용 중인 Site ID입니다.';
        } else if (error.message.includes('Nickname already taken')) {
          errorMessage = '이미 사용 중인 닉네임입니다.';
        } else if (error.message.includes('Phone number already taken')) {
          errorMessage = '이미 등록된 전화번호입니다.';
        } else if (error.message.includes('Invalid invite code')) {
          errorMessage = '유효하지 않은 초대코드입니다.';
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
        <div className="auth-subtitle">새 계정 만들기</div>
      </div>

      {/* 📝 회원가입 폼 */}
      <form onSubmit={handleSubmit} className="auth-form">
        {/* 초대코드 입력 */}
        <div className="form-group">
          <label htmlFor="invite_code" className="form-label">초대코드</label>
          <input
            type="text"
            id="invite_code"
            name="invite_code"
            value={formData.invite_code}
            onChange={handleChange}
            className="form-input"
            placeholder="초대코드를 입력하세요"
            required
          />
        </div>

        {/* Site ID 입력 */}
        <div className="form-group">
          <label htmlFor="site_id" className="form-label">Site ID</label>
          <input
            type="text"
            id="site_id"
            name="site_id"
            value={formData.site_id}
            onChange={handleChange}
            className="form-input"
            placeholder="고유한 ID를 입력하세요"
            required
          />
        </div>

        {/* 닉네임 입력 */}
        <div className="form-group">
          <label htmlFor="nickname" className="form-label">닉네임</label>
          <input
            type="text"
            id="nickname"
            name="nickname"
            value={formData.nickname}
            onChange={handleChange}
            className="form-input"
            placeholder="사용할 닉네임을 입력하세요"
            required
          />
        </div>

        {/* 비밀번호 입력 */}
        <div className="form-group">
          <label htmlFor="password" className="form-label">비밀번호</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="form-input"
            placeholder="4자 이상 입력하세요"
            required
            minLength={4}
          />
        </div>

        {/* 전화번호 입력 */}
        <div className="form-group">
          <label htmlFor="phone_number" className="form-label">전화번호</label>
          <input
            type="tel"
            id="phone_number"
            name="phone_number"
            value={formData.phone_number}
            onChange={handleChange}
            className="form-input"
            placeholder="010-1234-5678"
            required
          />
        </div>

        {/* 🚨 오류 메시지 */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {/* 🔄 회원가입 버튼 */}
        <button
          type="submit"
          className="auth-button primary"
          disabled={isLoading}
        >
          {isLoading ? '가입 중...' : '회원가입'}
        </button>
      </form>

      {/* 🔗 로그인으로 전환 */}
      <div className="auth-switch">
        <button
          type="button"
          onClick={onSwitchToLogin}
          className="link-button"
        >
          이미 계정이 있으신가요? <span className="link-accent">로그인</span>
        </button>
      </div>
    </>
  );
}
