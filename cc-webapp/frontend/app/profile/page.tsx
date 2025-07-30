'use client';

import { useState, useEffect } from 'react';
import ProfileContainer from '../../components/profile/ProfileContainer';
import ProfileContainerMobile from '../../components/profile/ProfileContainerMobile';

export default function ProfilePage() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // 모바일 감지 로직
    const checkIfMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    // 초기 체크
    checkIfMobile();

    // 리사이즈 이벤트에 반응
    window.addEventListener('resize', checkIfMobile);

    // 홈 대시보드와 동일한 모델카지노 스타일 적용
    const style = document.createElement('style');
    style.textContent = `
      @keyframes model-casino-bg {
        0%, 100% { 
          background-position: 0% 50%; 
        }
        50% { 
          background-position: 100% 50%; 
        }
      }

      @keyframes premium-pink-glow {
        0%, 100% { 
          text-shadow: 0 0 8px rgba(236, 72, 153, 0.7);
        }
        50% { 
          text-shadow: 0 0 16px rgba(236, 72, 153, 0.9), 0 0 24px rgba(236, 72, 153, 0.5);
        }
      }

      .model-casino-premium-bg {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 25%, #000000 50%, #1a1a1a 75%, #000000 100%) !important;
        background-size: 200% 200% !important;
        animation: model-casino-bg 12s ease-in-out infinite !important;
      }

      .premium-text-glow {
        animation: premium-pink-glow 3s ease-in-out infinite !important;
      }
    `;
    document.head.appendChild(style);

    // 클린업
    return () => {
      window.removeEventListener('resize', checkIfMobile);
      if (style.parentNode) {
        document.head.removeChild(style);
      }
    };
  }, []);

  return (
    <div className="w-full min-h-screen model-casino-premium-bg bg-black relative"
      style={{
        color: '#FFFFFF',
        fontFamily: "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
        overflow: 'hidden'
      }}>

      {/* 모델카지노 스타일 오버레이 */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900/30 via-pink-900/20 to-black/40"></div>
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-pink-400/8 rounded-full blur-3xl"></div>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="relative z-10 bg-black/20 backdrop-blur-sm min-h-full">
        {isMobile ? <ProfileContainerMobile /> : <ProfileContainer />}
      </div>
    </div>
  );
}