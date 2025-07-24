'use client';

import { useState, useEffect } from 'react';
import ProfileHeader from './ProfileHeader';
import ProfileStats from './ProfileStats';
import DailyCheckInModal from './DailyCheckInModal';
import FlashOfferBanner from './FlashOfferBanner';
import MissionCards from './MissionCards';
import ProfileActions from './ProfileActions';
import type { User, ProfileContainerProps, FlashOffer, Mission } from './types';
import '../../styles/profile-mobile.css';

export default function ProfileContainer({ className = '' }: ProfileContainerProps) {
  // Mock user data
  const [user] = useState<User>({
    id: 1,
    nickname: 'GameMaster',
    cyber_token_balance: 1500,
    rank: 'PREMIUM',
    level: 15,
    experience: 750,
    experienceRequired: 1000,
    wins: 42,
    loginStreak: 8,
    completedMissions: 23,
    email: 'user@example.com'
  });

  // Mock flash offer data
  const [flashOffer] = useState<FlashOffer>({
    id: 'flash-001',
    title: '💎 특별 토큰 패키지',
    description: '500% 보너스 + 무료 스핀',
    discount: 75,
    originalPrice: 19.99,
    salePrice: 4.99,
    endTime: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2시간 후 만료
    isActive: true,
    highlight: '최대 할인'
  });

  // Mock missions data
  const [missions] = useState<Mission[]>([
    {
      id: 'daily-1',
      title: '슬롯 게임 5회 플레이',
      description: '어떤 슬롯 게임이든 5회 플레이하세요',
      type: 'DAILY',
      progress: 3,
      target: 5,
      reward: { type: 'TOKEN', amount: 100 },
      isCompleted: false,
      timeLeft: '8시간 후 초기화'
    },
    {
      id: 'weekly-1',
      title: '주간 승리 목표',
      description: '이번 주에 10번 승리하세요',
      type: 'WEEKLY',
      progress: 7,
      target: 10,
      reward: { type: 'TOKEN', amount: 500 },
      isCompleted: false,
      timeLeft: '3일 남음'
    },
    {
      id: 'special-1',
      title: '럭키 잭팟 이벤트',
      description: '잭팟 게임에서 큰 상금을 획득하세요',
      type: 'SPECIAL',
      progress: 0,
      target: 1,
      reward: { type: 'SPECIAL', amount: 1000 },
      isCompleted: false,
      timeLeft: '이벤트 종료까지 5일'
    }
  ]);

  // Modal states
  // 기본값 false, 방문(마운트) 시에만 true로 설정
  const [showDailyCheckIn, setShowDailyCheckIn] = useState(false);
  const [showFlashOffer, setShowFlashOffer] = useState(true);
  const [lastCheckIn, setLastCheckIn] = useState<string | null>(null);

  // Check if user should see daily check-in modal
  // 방문(마운트) 시에만 모달이 뜨도록 useEffect 사용
  useEffect(() => {
    setShowDailyCheckIn(true);
  }, []);

  const handleDailyCheckInClaim = (day: number) => {
    const today = new Date().toISOString();
    localStorage.setItem('lastCheckIn', today);
    setLastCheckIn(today);
    setShowDailyCheckIn(false);
    console.log(`Day ${day} claimed!`);
  };

  const handleLogout = () => {
    console.log('Logging out...');
    // Handle logout logic - 제거됨
  };

  const handleMissionClick = (mission: Mission) => {
    console.log('Mission clicked:', mission.title);
    // Handle mission interaction
  };

  const handleVisitSite = () => {
    console.log('Visiting main site...');
    window.open('https://casinoclub.com', '_blank');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* 420px 모바일 최적화 컨테이너 */}
      <div className="w-full max-w-sm min-h-screen mx-auto px-4 pt-6 pb-8 
                      overflow-y-auto overscroll-y-contain
                      scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent"
           style={{ maxWidth: '420px' }}>
        
        {/* Flash Offer Banner - 최우선 노출 */}
        {showFlashOffer && (
          <section className="mb-6">
            <FlashOfferBanner 
              offer={flashOffer}
              onClose={() => setShowFlashOffer(false)}
              onVisitSite={handleVisitSite}
            />
          </section>
        )}

        {/* 메인 컨텐츠 - 더 넓은 간격 */}
        <main className="space-y-8">
          {/* 프로필 헤더 */}
          <section>
            <ProfileHeader user={user} />
          </section>

          {/* 프로필 통계 및 빠른 액션 */}
          <section>
            <ProfileStats user={user} />
          </section>

          {/* 데일리 체크인 - 실용앱 수준 개선 */}
          <section>
            <div className="rounded-xl py-8 relative overflow-hidden bg-gray-800/95 backdrop-blur-sm border border-gray-600/50 shadow-lg w-full"
                 style={{ 
                   paddingLeft: '32px', 
                   paddingRight: '32px',
                   maxWidth: '100% !important',
                   width: '100% !important'
                 }}>
              <div className="absolute inset-0 bg-gradient-to-br from-gray-700/30 via-transparent to-gray-900/30 pointer-events-none" />
              <div className="relative z-10 space-y-4">
                {/* 헤더 섹션 */}
                <div className="text-center space-y-3">
                  <div className="w-16 h-16 min-w-[4rem] min-h-[4rem] rounded-full flex items-center justify-center mx-auto shadow-lg flex-shrink-0 aspect-square"
                       style={{ 
                         background: 'linear-gradient(to right, #374151, #4b5563)',
                         border: '2px solid rgba(156, 163, 175, 0.3)'
                       }}>
                    <span className="text-3xl">🎁</span>
                  </div>
                  <h3 className="text-xl font-bold text-white">일일 보상</h3>
                  <p className="text-sm text-gray-300 whitespace-nowrap">매일 접속하고 특별한 보상을 받아보세요!</p>
                </div>
                
                {/* 체크인 버튼 */}
                <button 
                  onClick={() => setShowDailyCheckIn(true)}
                  className="w-full h-16 rounded-xl text-white font-bold transform hover:scale-[1.02] active:scale-[0.98] 
                             transition-all duration-300 shadow-lg hover:shadow-xl flex items-center justify-center gap-3 
                             text-lg relative overflow-hidden"
                  style={{ 
                    background: 'linear-gradient(to right, #4b5563, #6b7280)',
                    border: '2px solid rgba(156, 163, 175, 0.4)',
                    borderRadius: '0.75rem'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(to right, #6b7280, #9ca3af)';
                    e.currentTarget.style.borderColor = 'rgba(156, 163, 175, 0.6)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(to right, #4b5563, #6b7280)';
                    e.currentTarget.style.borderColor = 'rgba(156, 163, 175, 0.4)';
                  }}
                >
                  <div className="flex items-center justify-center gap-3">
                    <div className="w-8 h-8 min-w-[2rem] min-h-[2rem] bg-white/20 rounded-full flex items-center justify-center border border-white/30 flex-shrink-0 aspect-square">
                      <span className="text-white font-bold text-base">✓</span>
                    </div>
                    <span className="whitespace-nowrap">데일리 체크인</span>
                  </div>
                </button>
              </div>
            </div>
          </section>

          {/* 미션 카드 섹션 */}
          <section>
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-white px-4">오늘의 미션</h3>
              <MissionCards 
                missions={missions}
                onMissionClick={handleMissionClick}
                onVisitSite={handleVisitSite}
              />
            </div>
          </section>

          {/* 프로필 액션 버튼들 */}
          <section>
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-white px-4">빠른 액션</h3>
              <ProfileActions />
            </div>
          </section>
        </main>

        {/* 하단 여백 - 스크롤 공간 확보 */}
        <div className="h-8" />
      </div>

      {/* 데일리 체크인 모달 */}
      <DailyCheckInModal
        isOpen={showDailyCheckIn}
        onClose={() => setShowDailyCheckIn(false)}
        onClaim={handleDailyCheckInClaim}
        currentStreak={user.loginStreak || 0}
        lastCheckIn={lastCheckIn}
        todayReward={50}
      />
    </div>
  );
}
