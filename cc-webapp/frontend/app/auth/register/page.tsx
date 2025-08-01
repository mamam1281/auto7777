'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import RegisterForm from '../../../components/auth/RegisterForm';
import '../../../styles/auth.css';
import { isPopupWindow } from '../../../utils/gamePopup';

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isPopup, setIsPopup] = useState(false);
  const [initialized, setInitialized] = useState(false);
  
  // 클라이언트 측에서만 팝업 여부를 확인
  useEffect(() => {
    setIsPopup(isPopupWindow());
    setInitialized(true);
  }, []);

  const handleRegister = async (siteId: string, nickname: string, phoneNumber: string, password: string, inviteCode: string) => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          site_id: siteId,
          nickname, 
          phone_number: phoneNumber,
          password,
          invite_code: inviteCode 
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || '회원가입에 실패했습니다.');
      }
      
      // 회원가입 성공 후 홈으로 리디렉션
      router.push('/');
    } catch (err: any) {
      setError(err.message || '회원가입 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-[420px] mx-auto min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-auto">
      <div className={`auth-container ${initialized ? (isPopup ? 'popup-mode' : '') : ''} ${initialized ? 'auth-initialized' : 'auth-initializing'}`}
           style={{
             width: '100%',
             maxWidth: '420px',
             minHeight: 'auto',
             height: 'auto',
             overflow: 'visible',
             padding: '20px',
             boxSizing: 'border-box'
           }}>
        <RegisterForm 
          onRegister={handleRegister} 
          isLoading={isLoading} 
          error={error} 
          onSwitchToLogin={() => router.push('/auth/login')}
        />
      </div>
    </div>
  );
}
