'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';

// 프로젝트 표준 컴포넌트들만 사용
import GameCard from '../components/GameCard';
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

    // 프리미엄 그라디언트 애니메이션 스타일 추가
    const style = document.createElement('style');
    style.textContent = `
      @keyframes premium-gradient-shift {
        0%, 100% { 
          background-position: 0% 50%; 
          filter: hue-rotate(0deg);
        }
        25% { 
          background-position: 25% 25%; 
          filter: hue-rotate(10deg);
        }
        50% { 
          background-position: 100% 50%; 
          filter: hue-rotate(20deg);
        }
        75% { 
          background-position: 75% 75%; 
          filter: hue-rotate(10deg);
        }
      }

      .cosmic-premium-bg {
        background-size: 400% 400% !important;
        animation: premium-gradient-shift 12s ease-in-out infinite !important;
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

  // 게임 데이터 - 팝업으로 열기
  const featuredGames = [
    {
      id: 'cosmic-fortune',
      title: '코스믹 포츈',
      rating: 4.9,
      players: '31K명',
      imagePlaceholder: '🎰',
      onClick: () => openGamePopup('slots')
    },
    {
      id: 'royal-roulette',
      title: 'Royal Roulette',
      rating: 4.7,
      players: '18K명',
      imagePlaceholder: '🎰',
      onClick: () => openGamePopup('roulette')
    },
    {
      id: 'rps-battle',
      title: 'RPS Battle',
      rating: 4.5,
      players: '956명',
      imagePlaceholder: '✂️',
      onClick: () => openGamePopup('rps')
    },
    {
      id: 'lucky-gacha',
      title: 'Lucky Gacha',
      rating: 4.9,
      players: '3.1K명',
      imagePlaceholder: '🎁',
      onClick: () => openGamePopup('gacha')
    }
  ];

  // 빠른 시작 액션들 - 일부 팝업으로 열기
  const quickActions = [
    {
      id: 'game-start',
      label: '게임 시작',
      iconPlaceholder: '🎮',
      iconBgColor: '#5B30F6',
      onClick: () => openGamePopup('slots') // 슬롯 게임 팝업으로 시작
    },
    {
      id: 'deposit',
      label: '입금하기',
      iconPlaceholder: '💰',
      iconBgColor: '#10B981',
      onClick: () => router.push('/wallet')
    },
    {
      id: 'promotion',
      label: '프로모션',
      iconPlaceholder: '🎁',
      iconBgColor: '#F59E0B',
      onClick: () => router.push('/promotions')
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
           style={{ backgroundColor: '#1a1a1a' }}>
        <LoadingSpinner size="xl" variant="ring" text="카지노 로딩 중..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full cosmic-premium-bg"
         style={{ 
           background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 25%, #0f0f23 50%, #1a1a2e 75%, #0a0a0a 100%)',
           color: '#ffffff',
           fontFamily: "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
           overflow: 'hidden', // 가로 스크롤 방지
           position: 'relative'
         }}>

      {/* 고급스러운 배경 오버레이 */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `
          radial-gradient(circle at 20% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(79, 70, 229, 0.08) 0%, transparent 50%),
          radial-gradient(circle at 40% 60%, rgba(168, 85, 247, 0.05) 0%, transparent 50%)
        `,
        pointerEvents: 'none'
      }} />

      {/* Main Content - 스크롤 가능한 콘텐츠 */}
      <div className="w-full min-h-full relative z-10" style={{ 
        background: 'rgba(0,0,0,0.02)',
        backdropFilter: 'blur(0.5px)'
      }}> 
        
        <div className="py-2 sm:py-4">
        
        {/* 프리미엄 웰컴 섹션 */}
        <motion.div 
          className="text-center"
          style={{ marginBottom: '24px', marginTop: '16px' }} 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <h1 style={{ 
            fontSize: '56px',
            fontFamily: "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
            fontWeight: '300',
            letterSpacing: '0.02em',
            lineHeight: '1.1',
            background: 'linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 25%, #a5b4fc 50%, #8b5cf6 75%, #7c3aed 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            color: 'transparent',
            marginBottom: '12px',
            textShadow: '0 8px 32px rgba(139, 92, 246, 0.3)'
          }}>
            Welcome to Cosmic Casino
          </h1>
          <p style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: '18px',
            color: 'rgba(255, 255, 255, 0.8)',
            fontWeight: '400',
            letterSpacing: '0.025em',
            marginTop: '8px'
          }}>
            Premium Gaming Experience
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
            color: 'rgba(255, 255, 255, 0.95)',
            fontWeight: '600',
            letterSpacing: '0.02em',
            marginBottom: '24px'
          }}>🎰 Start Your Journey</h2>
          <div className="flex flex-col sm:flex-row flex-wrap justify-center gap-4 w-full max-w-full overflow-hidden">
            <Button
              variant="primary"
              size="lg"
              onClick={() => openGamePopup('slots')} // 팝업으로 게임 시작
            >
              🎮 Play Games
            </Button>
            <Button
              variant="secondary"
              size="lg"
              onClick={() => router.push('/wallet')}
            >
              💰 토큰 충전
            </Button>
            <Button
              variant="accent"
              size="lg"
              onClick={() => openGamePopup('gacha')} // 가챠 팝업으로 열기
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
            color: 'rgba(255, 255, 255, 0.95)',
            fontWeight: '600',
            letterSpacing: '0.02em',
            marginBottom: '16px'
          }}>⚡ Quick Start</h2>
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

        {/* 인기 게임 섹션 - 프로젝트 표준 GameCard 사용 */}
        <motion.section
          style={{ marginBottom: '40px' }} 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.6 }}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 style={{ 
              fontSize: '24px',
              fontFamily: "'Inter', sans-serif",
              color: 'rgba(255, 255, 255, 0.95)',
              fontWeight: '600',
              letterSpacing: '0.02em'
            }}>🔥 Featured Games</h2>
            </div>
          
          <div style={{ marginTop: '24px' }}> 
          <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 w-full max-w-full overflow-hidden" 
               style={{ gridAutoRows: '200px' }}>
            {featuredGames.map((game, index) => (
              <motion.div
                key={game.id}
                className="w-full h-full"
                style={{ height: '200px' }}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
              >
                <GameCard
                  id={game.id}
                  title={game.title}
                  rating={game.rating}
                  players={game.players}
                  imagePlaceholder={game.imagePlaceholder}
                  onClick={game.onClick}
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
