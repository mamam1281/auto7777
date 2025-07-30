'use client';

import { useState, useEffect } from 'react';
import ProfileHeader from './ProfileHeader';
import ProfileStats from './ProfileStats';
import type { User, ProfileContainerProps } from './types';

export default function ProfileContainer({ className = '' }: ProfileContainerProps) {
  // Mock user data
  const [user] = useState<User>({
    id: 1,
    nickname: '모델지민',
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

  // Modal states - DailyCheckInModal 제거됨
  // const [showDailyCheckIn, setShowDailyCheckIn] = useState(false);
  // const [lastCheckIn, setLastCheckIn] = useState<string | null>(null);

  // DailyCheckInModal 관련 코드 제거됨
  // Check if user should see daily check-in modal
  // useEffect(() => {
  //   const storedLastCheckIn = localStorage.getItem('lastCheckIn');
  //   if (storedLastCheckIn) {
  //     setLastCheckIn(storedLastCheckIn);
  //   }
  // }, []);

  // const handleDailyCheckInClaim = (day: number) => {
  //   const today = new Date().toISOString();
  //   localStorage.setItem('lastCheckIn', today);
  //   setLastCheckIn(today);
  //   setShowDailyCheckIn(false);
  //   console.log(`Day ${day} claimed!`);
  // };

  return (
    <div className={`profile-container min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 ${className}`}>
      {/* 400px * 750px 데일리 모달 스타일 컨테이너 */}
      <div className="w-full max-w-[400px] min-h-[750px] mx-auto p-6 space-y-8 
                      overflow-y-auto overscroll-y-contain
                      scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent">

        {/* 메인 컨텐츠 - 데일리 모달과 동일한 간격 */}
        <main className="space-y-8">
          {/* 프로필 헤더 */}
          <section>
            <ProfileHeader user={user} />
          </section>

          {/* 프로필 통계 및 액션 */}
          <section>
            <ProfileStats user={user} />
          </section>

          {/* 데일리 체크인 버튼 - 제거됨 */}
          {/* 
          <section>
            <div className="profile-glass-strong rounded-xl p-6 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/10 pointer-events-none" />
              <div className="relative z-10 text-center">
                <h3 className="text-lg font-bold text-white mb-4">일일 보상</h3>
                <button 
                  onClick={() => setShowDailyCheckIn(true)}
                  className="w-full h-14 bg-gradient-to-r from-purple-600 to-pink-600 
                             text-white font-bold rounded-lg hover:from-purple-500 hover:to-pink-500
                             transform hover:scale-105 active:scale-95 transition-all duration-200
                             shadow-lg hover:shadow-xl flex items-center justify-center gap-2 text-base"
                >
                  🎁 데일리 체크인
                </button>
              </div>
            </div>
          </section>
          */}
        </main>

        {/* 하단 여백 */}
        <div className="h-24" />
      </div>
    </div>
  );
}
