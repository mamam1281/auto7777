'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';

// 프로젝트 표준 컴포넌트들만 사용
import Button from '../components/Button';
import QuickStartItem from '../components/QuickStartItem';
import LoadingSpinner from '../components/LoadingSpinner';
import SplashScreen from '../components/splash/SplashScreen';

// 게임 팝업 유틸리티
import { openGamePopup } from '../utils/gamePopup';

export default function CasinoDashboard() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [showSplash, setShowSplash] = useState(true);
  const [hasSeenSplash, setHasSeenSplash] = useState(false);

  // 스플래시 화면을 표시한 적 있는지 체크
  useEffect(() => {
    const splashSeen = localStorage.getItem('splashSeen');
    if (splashSeen) {
      setHasSeenSplash(true);
    } else {
      // 첫 방문 시에만 스플래시 화면 표시
      localStorage.setItem('splashSeen', 'true');
    }

    // 모델카지노 스타일 - 깔끔한 다크네이비 + 핑크 악센트
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

  // 빠른 시작 액션들 - 모델카지노 컬러 팔레트
  const quickActions = [
    {
      id: 'daily-reward',
      label: '오늘보상받기',
      iconPlaceholder: '🎁',
      iconBgColor: 'bg-gradient-to-r from-pink-500 to-pink-600', // 핑크 그라데이션
      onClick: () => router.push('/wallet') // 월렛 페이지로 안내 (바텀네비 "내역"과 동일)
    },
    {
      id: 'model-site',
      label: '모델사이트',
      iconPlaceholder: '💎',
      iconBgColor: 'bg-gradient-to-r from-purple-600 to-purple-700', // 퍼플 그라데이션
      onClick: () => window.open('https://md-2424.com', '_blank')
    },
    {
      id: 'popular-games',
      label: '방송보러가기',
      iconPlaceholder: '🔥',
      iconBgColor: 'bg-gradient-to-r from-indigo-600 to-indigo-700', // 인디고 그라데이션
      onClick: () => window.open('https://youtube.com', '_blank')// 게임 대시보드 페이지로 연결
    },
    {
      id: 'popular-games2',
      label: '이벤트안내',
      iconPlaceholder: '🎯',
      iconBgColor: 'bg-gradient-to-r from-slate-700 to-slate-800', // 다크 그라데이션
      onClick: () => window.open('/promotions') // 프로필 페이지로 연결
    }
  ];

  // 스플래시 화면 표시
  if (showSplash) {
    return <SplashScreen onComplete={handleSplashComplete} skipAuth={hasSeenSplash} />;
  }

  // 일반 로딩 화면
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: '#000000' }}>
        <LoadingSpinner size="xl" variant="ring" text="카지노 로딩 중..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full model-casino-premium-bg bg-black"
      style={{
        color: '#FFFFFF',
        fontFamily: "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
        overflow: 'hidden',
        position: 'relative'
      }}>

      {/* 모델카지노 스타일 오버레이 */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900/30 via-pink-900/20 to-black/40"></div>
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-pink-400/8 rounded-full blur-3xl"></div>
      </div>

      {/* Main Content - 스크롤 가능한 콘텐츠 */}
      <div className="w-full min-h-full relative z-10 bg-black/20 backdrop-blur-sm">

        <div className="py-2 sm:py-4">

          {/* 프리미엄 웰컴 섹션 */}
          <motion.div
            className="text-center"
            style={{ marginBottom: '24px', marginTop: '16px' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <h1 className="premium-text-glow" style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: '48px',
              fontWeight: 'bold',
              lineHeight: '1.1',
              color: '#FFFFFF',
              marginBottom: '12px'
            }}>
              Welcome to <span style={{ color: '#EC4899' }}>MODELCASINO</span>
            </h1>
            <p style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: '18px',
              color: '#94A3B8',
              fontWeight: '500',
              letterSpacing: '0.025em',
              marginTop: '8px',
              opacity: '0.9'
            }}>
              최고급 모델과 함께하는 특별한 시간
            </p>
          </motion.div>

          {/* 프리미엄 게임 섹션 */}
          <motion.section
            className="text-center py-8"
            style={{ marginBottom: '32px' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            <h2 style={{
              fontSize: '24px',
              fontFamily: "'Inter', sans-serif",
              color: '#EC4899',
              fontWeight: '700',
              letterSpacing: '0.02em',
              marginBottom: '24px',
              textShadow: '0 2px 6px rgba(236, 72, 153, 0.3)'
            }}>🎯 지금 바로 시작하세요</h2>
            <div className="flex flex-col sm:flex-row flex-wrap justify-center gap-4 w-full max-w-full overflow-hidden">
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

          {/* 빠른 시작 액션들 - 프로젝트 표준 컴포넌트 사용 */}
          <motion.section
            style={{ marginBottom: '120px' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            <h2 style={{
              fontSize: '24px',
              fontFamily: "'Inter', sans-serif",
              color: '#EC4899',
              fontWeight: '700',
              letterSpacing: '0.02em',
              marginBottom: '16px',
              textShadow: '0 2px 6px rgba(236, 72, 153, 0.3)'
            }}>⚡ 빠른 접속</h2>
            <div style={{ marginTop: '24px' }}>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-6 w-full max-w-full overflow-hidden"
                style={{ gridAutoRows: '200px' }}>
                {quickActions.map((action, index) => (
                  <motion.div
                    key={action.id}
                    className="w-full h-full"
                    style={{ height: '200px' }}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1, duration: 0.5 }}
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
