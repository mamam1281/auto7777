'use client';

import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

// 프로젝트 표준 컴포넌트들만 사용
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';
import QuickStartItem from '../components/QuickStartItem';
import SplashScreen from '../components/splash/SplashScreen';

// 게임 팝업 유틸리티

// 사용자 인증 hook
import { useUser } from '../hooks/useUser';

export default function CasinoDashboard() {
  const router = useRouter();
  const { user, isLoading: userLoading } = useUser();
  const [isLoading, setIsLoading] = useState(true);
  const [showSplash, setShowSplash] = useState(true);
  const [hasSeenSplash, setHasSeenSplash] = useState(false);

  // 로그인 상태 확인 - 안전한 방식으로 리다이렉트
  useEffect(() => {
    // 사용자 로딩이 완료되고 로그인되지 않은 경우 리다이렉트
    if (!userLoading && !user) {
      // setTimeout을 사용하여 렌더링 사이클 이후에 실행
      const timer = setTimeout(() => {
        router.replace('/auth');
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [user, userLoading, router]);

  // 스플래시 화면을 표시한 적 있는지 체크
  useEffect(() => {
    const splashSeen = localStorage.getItem('splashSeen');
    if (splashSeen) {
      setHasSeenSplash(true);
    } else {
      // 첫 방문 시에만 스플래시 화면 표시
      localStorage.setItem('splashSeen', 'true');
    }

    // 프리미엄 그라디언트 애니메이션 스타일 추가
    const style = document.createElement('style');
    style.textContent = `
      @keyframes premium-gradient-shift {
        0%, 100% { 
          background-position: 0% 50%; 
          filter: hue-rotate(0deg) saturate(1.2);
        }
        25% { 
          background-position: 25% 25%; 
          filter: hue-rotate(15deg) saturate(1.3);
        }
        50% { 
          background-position: 100% 50%; 
          filter: hue-rotate(30deg) saturate(1.4);
        }
        75% { 
          background-position: 75% 75%; 
          filter: hue-rotate(15deg) saturate(1.3);
        }
      }

      .cosmic-premium-bg {
        background-size: 400% 400% !important;
        animation: premium-gradient-shift 10s ease-in-out infinite !important;
      }
    `;
    document.head.appendChild(style);

    return () => {
      if (style.parentNode) {
        document.head.removeChild(style);
      }
    };
  }, []);

  // 스플래시 완료 후 콜백
  const handleSplashComplete = () => {
    setShowSplash(false);
    setIsLoading(false);
  };

  // 빠른 시작 액션들 - 일부 팝업으로 열기
  const quickActions = [
    {
      id: 'daily-reward',
      label: '오늘보상받기',
      iconPlaceholder: '🎁',
      iconBgColor: '#f1279dff',
      onClick: () => router.push('/wallet') // 월렛 페이지로 안내 (바텀네비 "내역"과 동일)
    },
    {
      id: 'model-site',
      label: '모델사이트',
      iconPlaceholder: '💎',
      iconBgColor: '#ffd30eff',
      onClick: () => window.open('https://md-2424.com', '_blank')
    },
    {
      id: 'popular-games',
      label: '방송보러가기',
      iconPlaceholder: '🔥',
      iconBgColor: '#eb2768ff',
      onClick: () => window.open('https://youtube.com', '_blank')// 게임 대시보드 페이지로 연결
    },
    {
      id: 'popular-games2',
      label: '이벤트안내',
      iconPlaceholder: '🎯',
      iconBgColor: '#02ccf0ff',
      onClick: () => window.open('/promotions') // 프로필 페이지로 연결
    }
  ];

  // 스플래시 화면 표시 - 로그인된 사용자만
  if (showSplash && user && !userLoading) {
    return <SplashScreen onComplete={handleSplashComplete} />;
  }

  // 사용자 로딩 중이거나 로그인되지 않은 경우 - 로그인 페이지로 즉시 리다이렉트
  if (userLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center"
        style={{ background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 25%, #0f0f0f 50%, #1a1a1a 75%, #0a0a0a 100%)' }}>
        <LoadingSpinner size="xl" variant="ring" text="사용자 정보 확인 중..." />
      </div>
    );
  }

  // 로그인되지 않은 경우 로딩 화면 표시
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center"
        style={{ background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 25%, #0f0f0f 50%, #1a1a1a 75%, #0a0a0a 100%)' }}>
        <LoadingSpinner size="xl" variant="ring" text="로그인 페이지로 이동 중..." />
      </div>
    );
  }

  // 일반 로딩 화면
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center"
        style={{ background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 25%, #0f0f0f 50%, #1a1a1a 75%, #0a0a0a 100%)' }}>
        <LoadingSpinner size="xl" variant="ring" text="카지노 로딩 중..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full cosmic-premium-bg"
      style={{
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 25%, #0f0f0f 50%, #1a1a1a 75%, #0a0a0a 100%)',
        color: '#ffffff',
        fontFamily: "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
        overflow: 'hidden',
        position: 'relative'
      }}>

      {/* 부드러운 다크 배경 오버레이 */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `
          radial-gradient(circle at 20% 20%, rgba(50, 50, 50, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(30, 30, 30, 0.08) 0%, transparent 50%),
          radial-gradient(circle at 40% 60%, rgba(40, 40, 40, 0.06) 0%, transparent 50%)
        `,
        pointerEvents: 'none'
      }} />

      {/* Main Content - 스크롤 가능한 콘텐츠 */}
      <div className="w-full min-h-full relative z-10" style={{
        background: 'rgba(15, 15, 35, 0.3)',
        backdropFilter: 'blur(1px)'
      }}>

        <div className="py-2 sm:py-4">

          {/* 프리미엄 웰컴 섹션 */}
          <motion.header
            className="text-center"
            style={{ marginBottom: '30px', marginTop: '20px' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            role="banner"
          >
            <h1 style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: '56px', // 42px → 56px (더 크게)
              fontWeight: 'bold',
              lineHeight: '1.1',
              background: 'linear-gradient(135deg, var(--color-primary-pink) 0%, #ffffff 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              color: 'transparent',
              marginBottom: '20px',
              textShadow: '0 2px 8px rgba(0, 0, 0, 0.3)' // 글로우 → 부드러운 쉐도우
            }}>
              모델카지노
            </h1>
            <p style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: '16px', // 18px → 16px (비율 개선)
              color: 'rgba(255, 255, 255, 0.95)', // 대비 개선
              fontWeight: '500',
              letterSpacing: '0.025em',
              marginTop: '16px',
              textShadow: '0 1px 4px rgba(0, 0, 0, 0.2)' // 글로우 → 부드러운 쉐도우
            }}>
              최고급 모델과 함께하는 특별한 시간
            </p>
          </motion.header>

          {/* 프리미엄 게임 섹션 */}
          <motion.section
            className="text-center py-18"
            style={{ marginBottom: '42px' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            aria-labelledby="game-section-title"
          >
            <h2
              id="game-section-title"
              style={{
                fontSize: '28px', // 24px → 28px (섹션 제목 강화)
                fontFamily: "'Inter', sans-serif",
                color: '#ffffff',
                fontWeight: '700',
                letterSpacing: '0.02em',
                marginBottom: '32px',
                textShadow: '0 2px 8px rgba(0, 0, 0, 0.3)' // 글로우 → 부드러운 쉐도우
              }}>🎯 지금 바로 시작하세요</h2>
            <div className="flex flex-col sm:flex-row flex-wrap justify-center gap-1 w-full max-w-full overflow-hidden">
              <Button
                variant="primary"
                size="lg"
                onClick={() => router.push('/games')} // 게임 대시보드로 연결
              >
                🎮 게임시작하기
              </Button>
              <Button
                variant="secondary"
                size="lg"
                onClick={() => window.open('https://md-2424.com', '_blank')}
              >
                💎 모델사이트방문
              </Button>
              <Button
                variant="accent"
                size="lg"
                onClick={() => router.push('/wallet')} // 월렛 페이지로 연결
              >
                🎁 보너스 받기
              </Button>
            </div>
          </motion.section>

          {/* 빠른 시작 액션들 - 접근성 개선 */}
          <motion.section
            style={{ marginBottom: '120px' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            aria-labelledby="quick-access-title"
            role="region"
          >
            <h2
              id="quick-access-title"
              style={{
                fontSize: '28px', // 24px → 28px (섹션 제목 일관성)
                fontFamily: "'Inter', sans-serif",
                color: '#ffffff',
                fontWeight: '700',
                letterSpacing: '0.03em',
                marginBottom: '18px',
                textShadow: '0 2px 8px rgba(0, 0, 0, 0.3)' // 글로우 → 부드러운 쉐도우
              }}>
              <span aria-hidden="true">⚡</span> 빠른 접속
            </h2>

            {/* 스크린리더를 위한 섹션 설명 */}
            <p className="sr-only">
              다음 4개의 빠른 접속 버튼을 사용하여 주요 기능에 바로 접근할 수 있습니다.
              탭 키로 이동하고 엔터나 스페이스 키로 선택할 수 있습니다.
            </p>

            <div style={{ marginTop: '28px' }}>
              <div
                className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-3 w-full max-w-full overflow-hidden"
                style={{ gridAutoRows: '200px' }}
                role="grid"
                aria-label="빠른 접속 메뉴"
              >
                {quickActions.map((action, index) => (
                  <motion.div
                    key={action.id}
                    className="w-full h-full"
                    style={{ height: '200px' }}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1, duration: 0.5 }}
                    role="gridcell"
                  >
                    <QuickStartItem
                      id={action.id}
                      label={action.label}
                      iconPlaceholder={action.iconPlaceholder}
                      iconBgColor={action.iconBgColor}
                      onClick={action.onClick}
                    />
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.section>

        </div>
      </div>

    </div>
  );
}
