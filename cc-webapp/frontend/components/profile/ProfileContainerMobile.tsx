'use client';

import { useState, useEffect } from 'react';
import ProfileHeader from './ProfileHeader';
import ProfileStats from './ProfileStats';
import FlashOfferBanner from './FlashOfferBanner';
import MissionCards from './MissionCards';
import ProfileActions from './ProfileActions';
import type { User, ProfileContainerProps, FlashOffer, Mission } from './types';
import '../../styles/profile-mobile.css';

// 420×750 모바일 최적화 프로필 컨테이너
export default function ProfileContainerMobile(props: ProfileContainerProps) {
  const [user, setUser] = useState<User>({
    id: 1,
    nickname: "Player123",
    cyber_token_balance: 15420,
    level: 15,
    experience: 2350,
    experienceRequired: 4000,
    tokens: 145,
    wins: 68,
    loginStreak: 7
  });

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

  const [flashOffer, setFlashOffer] = useState<FlashOffer | null>({
    id: "1",
    title: "스페셜 젬 패키지",
    description: "한정 특가 상품",
    originalPrice: 9900,
    salePrice: 4900,
    discount: 51,
    endTime: new Date(Date.now() + 3600000).toISOString(),
    isActive: true
  });

  const [showLevelModal, setShowLevelModal] = useState(false);

  return (
    <div className="profile-mobile-layout">
      <div className="w-full">
        <div className="profile-mobile-header">
          <ProfileHeader user={user} />
        </div>
        
        <div className="profile-mobile-stats">
          <ProfileStats user={user} />
        </div>
        
        {flashOffer && (
          <div className="profile-mobile-card">
            <FlashOfferBanner 
              offer={flashOffer} 
              onClose={() => setFlashOffer(null)} 
            />
          </div>
        )}
        
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
