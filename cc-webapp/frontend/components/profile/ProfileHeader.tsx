'use client';

import { useState } from 'react';
import { Crown, Star, TrendingUp } from 'lucide-react';
import ProfileAvatar from './ProfileAvatar';
import RankBadge from './RankBadge';
import SimpleProgressBar from '../SimpleProgressBar';
import StatusDot from './StatusDot';
import type { ProfileHeaderProps, RANK_COLORS } from './types';

export default function ProfileHeader({ user }: ProfileHeaderProps) {
  const [showOnlineStatus] = useState(true);

  return (
    <div className="rounded-xl py-6 relative overflow-hidden bg-gray-800/95 backdrop-blur-sm border border-gray-600/50 shadow-lg w-full"
         style={{ 
           paddingLeft: '32px', 
           paddingRight: '32px',
           maxWidth: '100% !important',
           width: '100% !important'
         }}>
      {/* Background decoration - 스크린샷과 동일한 어두운 배경 */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-700/30 via-transparent to-gray-900/30 pointer-events-none" />
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-gray-600/20 to-transparent rounded-full filter blur-3xl" />
      
      <div className="relative z-10">
        {/* 실용적인 카드형 레이아웃 - 모든 정보를 한번에 표시 */}
        <div className="grid grid-cols-[auto_1fr_auto] gap-6 items-center">
          {/* 왼쪽: 아바타와 기본 정보 */}
          <div className="flex items-center gap-5">
            <div className="relative">
              <ProfileAvatar 
                user={user}
                size="lg"
                showOnlineStatus={false}
                className="ring-2 ring-purple-400/50 shadow-lg"
              />
              {showOnlineStatus && (
                <div className="absolute -bottom-1 -right-1">
                  <StatusDot status="online" size="md" showPulse={true} />
                </div>
              )}
            </div>
            
            {/* 닉네임과 배지들 - 자동 크기 조정 */}
            <div className="space-y-2">
              <h2 className="text-xl font-bold text-white leading-tight whitespace-nowrap">
                {user.nickname}
              </h2>
              <div className="flex items-center gap-2">
                {/* 프리미엄 배지만 표시 - 12-14px 폰트 크기 */}
                <div className={`inline-flex items-center px-3 py-1.5 border rounded-lg font-semibold 
                               leading-none min-w-fit whitespace-nowrap
                               ${(user.rank as keyof typeof RANK_COLORS) === 'PREMIUM' 
                                 ? 'bg-orange-500/20 border-orange-500/30 text-orange-400' 
                                 : 'bg-gray-500/20 border-gray-500/30 text-gray-400'}`}
                     style={{ fontSize: '13px' }}>
                  {(user.rank as keyof typeof RANK_COLORS) === 'PREMIUM' ? '프리미엄' : '스탠다드'}
                </div>
              </div>
            </div>
          </div>
          
          {/* 중앙: 핵심 스탯 (가로 정렬) - 글자수에 맞는 자동 크기 */}
          <div className="flex items-center gap-2 justify-center">
            {/* 승리 수 */}
            <div className="inline-flex items-center gap-2 bg-amber-500/15 px-3 py-2 rounded-lg border border-amber-400/30
                           min-w-fit whitespace-nowrap">
              <Star size={16} className="fill-current text-amber-400 flex-shrink-0" />
              <div className="text-center">
                <div className="text-sm font-bold text-amber-400 leading-tight">{user.wins || 0}</div>
                <div className="text-xs text-amber-300 leading-tight">승리</div>
              </div>
            </div>
            
            {/* 연속 접속 */}
            <div className="inline-flex items-center gap-2 bg-orange-500/15 px-3 py-2 rounded-lg border border-orange-400/30
                           min-w-fit whitespace-nowrap">
              <TrendingUp size={16} className="text-orange-400 flex-shrink-0" />
              <div className="text-center">
                <div className="text-sm font-bold text-orange-400 leading-tight">{user.loginStreak || 0}</div>
                <div className="text-xs text-orange-300 leading-tight">일연속</div>
              </div>
            </div>
          </div>
          
          {/* 오른쪽: 경험치 진행률만 표시 - 자동 크기 조정 */}
          <div className="flex flex-col items-end gap-1">
            <div className="text-xs text-gray-300 whitespace-nowrap">
              {Math.round(((user.experience || 0) / (user.experienceRequired || 1000)) * 100)}% 완료
            </div>
          </div>
        </div>

        {/* 하단: 경험치 프로그레스바만 간결하게 */}
        <div className="mt-4 pt-3 border-t border-white/10">
          <SimpleProgressBar
            progress={((user.experience || 0) / (user.experienceRequired || 1000)) * 100}
            size="sm"
            showPercentage={false}
            className="h-2"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>{(user.experience || 0).toLocaleString()} XP</span>
            <span>{(user.experienceRequired || 1000).toLocaleString()} XP</span>
          </div>
        </div>
      </div>
    </div>
  );
}
