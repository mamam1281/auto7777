'use client';

import { useState, useEffect } from 'react';
import ProfileHeader from './ProfileHeader';
import ProfileStats from './ProfileStats';
import MissionCards from './MissionCards';
import ProfileActions from './ProfileActions';
import { useUser } from '../../hooks/useUser';
import type { User, ProfileContainerProps, Mission } from './types';
import '../../styles/profile-mobile.css';

// 420×750 모바일 최적화 프로필 컨테이너
export default function ProfileContainerMobile(props: ProfileContainerProps) {
  // 🎯 실제 사용자 데이터 사용
  const { user: currentUser, isLoading } = useUser();

  // 프로필 타입에 맞게 데이터 변환
  const user: User = currentUser ? {
    id: parseInt(currentUser.id),
    nickname: currentUser.nickname,
    cyber_token_balance: currentUser.cyber_tokens,
    rank: currentUser.vip_tier as 'VIP' | 'PREMIUM' | 'STANDARD',
    level: currentUser.battlepass_level,
    experienceRequired: (currentUser.battlepass_level + 1) * 100,
    wins: Math.floor(currentUser.cyber_tokens / 50),
    loginStreak: 7, // TODO: API에서 가져오기
    tokens: currentUser.cyber_tokens,
    completedMissions: 23,
    email: 'user@example.com'
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
    tokens: 0,
    completedMissions: 0,
    email: ''
  };

  if (isLoading) {
    return (
      <div className="profile-mobile-layout">
        <div className="w-full flex items-center justify-center min-h-screen">
          <div className="text-white text-xl">프로필 로딩 중...</div>
        </div>
      </div>
    );
  }

  const [missions, setMissions] = useState<Mission[]>([
    {
      id: "1",
      title: "데일리 로그인",
      description: "매일 접속하여 보상 받기",
      progress: 1,
      target: 1,
      reward: { type: "coins", amount: 50 },
      isCompleted: false,
      type: "DAILY"
    },
    {
      id: "2",
      title: "게임 3회 플레이",
      description: "어떤 게임이든 3회 플레이하기",
      progress: 2,
      target: 3,
      reward: { type: "coins", amount: 100 },
      isCompleted: false,
      type: "DAILY"
    }
  ]);

  return (
    <div className="profile-mobile-layout">
      <div className="w-full">
        <div className="profile-mobile-header">
          <ProfileHeader user={user} />
        </div>

        <div className="profile-mobile-stats">
          <ProfileStats user={user} />
        </div>

        <div className="profile-mobile-missions">
          <MissionCards missions={missions} />
        </div>

        <div className="profile-mobile-actions">
          <ProfileActions />
        </div>
      </div>
    </div>
  );
}
