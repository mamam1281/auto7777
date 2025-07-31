'use client';

import { useState, useEffect } from 'react';
import ProfileHeader from './ProfileHeader';
import ProfileStats from './ProfileStats';
import MissionCards from './MissionCards';
import ProfileActions from './ProfileActions';
import { useUser } from '../../hooks/useUser';
import type { User, ProfileContainerProps, Mission } from './types';
import '../../styles/profile-mobile.css';

export default function ProfileContainer({ className = '' }: ProfileContainerProps) {

  // 🎯 실제 사용자 데이터 사용
  const { user: currentUser, isLoading } = useUser();
  
  // 🔄 백엔드 프로필 API에서 실제 데이터 가져오기
  const [profileData, setProfileData] = useState<any>(null);
  const [profileLoading, setProfileLoading] = useState(false);

  // 백엔드에서 프로필 데이터 가져오기
  useEffect(() => {
    const fetchProfile = async () => {
      if (!currentUser) return;
      
      console.log('🔍 현재 사용자 정보:', currentUser);
      console.log('🔍 사용자 ID:', currentUser.id, typeof currentUser.id);
      
      // 현재 로그인한 사용자의 실제 ID 사용
      const userId = currentUser.id;
      
      setProfileLoading(true);
      try {
        console.log('🔄 백엔드에서 프로필 데이터 가져오는 중...');
        const response = await fetch(`http://localhost:8000/api/users/${userId}/profile`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const profileData = await response.json();
          console.log('✅ 프로필 데이터 로드 성공:', profileData);
          setProfileData(profileData);
        } else {
          console.error('❌ 프로필 데이터 로드 실패:', response.status);
          const errorText = await response.text();
          console.error('❌ 에러 내용:', errorText);
        }
      } catch (error) {
        console.error('❌ 프로필 API 오류:', error);
      } finally {
        setProfileLoading(false);
      }
    };

    fetchProfile();
  }, [currentUser]);

  // Mock missions data - useState를 최상단으로 이동
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

  // 프로필 타입에 맞게 데이터 변환 - 백엔드 데이터 우선 사용
  const user: User = profileData ? {
    id: profileData.user_id,
    nickname: profileData.nickname,
    cyber_token_balance: profileData.cyber_tokens,
    rank: profileData.rank.toUpperCase() as 'VIP' | 'PREMIUM' | 'STANDARD' | 'ADMIN',
    level: profileData.battlepass_level || 1,
    experience: (profileData.battlepass_level || 1) * 100, // 임시 계산
    experienceRequired: ((profileData.battlepass_level || 1) + 1) * 100,
    wins: Math.floor(profileData.cyber_tokens / 50), // 임시 계산
    loginStreak: 8, // TODO: API에서 가져오기
    completedMissions: 23, // TODO: API에서 가져오기  
    email: 'user@example.com' // TODO: API에서 가져오기
  } : currentUser ? {
    id: parseInt(currentUser.id),
    nickname: currentUser.nickname,
    cyber_token_balance: currentUser.cyber_tokens,
    rank: currentUser.vip_tier as 'VIP' | 'PREMIUM' | 'STANDARD',
    level: currentUser.battlepass_level,
    experience: currentUser.battlepass_level * 100, // 임시 계산
    experienceRequired: (currentUser.battlepass_level + 1) * 100,
    wins: Math.floor(currentUser.cyber_tokens / 50), // 임시 계산
    loginStreak: 8, // TODO: API에서 가져오기
    completedMissions: 23, // TODO: API에서 가져오기  
    email: 'user@example.com' // TODO: API에서 가져오기
  } : {
    id: 0,
    nickname: 'Loading...',
    cyber_token_balance: 0,
    rank: 'STANDARD',
    level: 1,
    experience: 0,
    experienceRequired: 100,
    wins: 0,
    loginStreak: 0,
    completedMissions: 0,
    email: ''
  };

  // 로딩 중이면 로딩 표시 (일반 로딩 또는 프로필 로딩)
  if (isLoading || profileLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
        <div className="text-white text-xl">
          {isLoading ? '사용자 정보 로딩 중...' : '프로필 데이터 로딩 중...'}
        </div>
      </div>
    );
  }

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
    <div className="min-h-screen w-full"
      style={{
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 25%, #0f0f0f 50%, #1a1a1a 75%, #0a0a0a 100%)',
        color: '#ffffff',
        fontFamily: "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif"
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

      {/* 420px 모바일 최적화 컨테이너 */}
      <div className="w-full max-w-sm min-h-screen mx-auto px-4 pt-6 pb-8 relative z-10
                      overflow-y-auto overscroll-y-contain
                      scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent"
        style={{ 
          maxWidth: '420px',
          background: 'rgba(15, 15, 35, 0.3)',
          backdropFilter: 'blur(1px)'
        }}>

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

      {/* 데일리 체크인 모달은 글로벌 컴포넌트로 이동했습니다 */}
    </div>
  );
}
