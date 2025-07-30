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
    <div className="rounded-xl py-6 relative overflow-hidden bg-black/60 backdrop-blur-sm border border-pink-500/30 shadow-xl w-full"
      style={{
        paddingLeft: '32px',
        paddingRight: '32px',
        maxWidth: '100% !important',
        width: '100% !important',
        background: 'linear-gradient(135deg, rgba(0,0,0,0.8) 0%, rgba(26,26,26,0.6) 50%, rgba(0,0,0,0.8) 100%)',
        borderColor: 'rgba(236, 72, 153, 0.3)',
        boxShadow: '0 8px 32px rgba(236, 72, 153, 0.15)'
      }}>
      {/* Background decoration - 핑크 그라데이션 */}
      <div className="absolute inset-0 bg-gradient-to-br from-pink-900/20 via-transparent to-pink-800/15 pointer-events-none" />
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-pink-500/20 to-transparent rounded-full filter blur-3xl" />
      <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-pink-400/15 to-transparent rounded-full filter blur-2xl" />

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
                {/* 프리미엄 배지만 표시 - 핑크 테마로 변경 */}
                <div className={`inline-flex items-center px-3 py-1.5 border rounded-lg font-semibold 
                               leading-none min-w-fit whitespace-nowrap
                               ${(user.rank as keyof typeof RANK_COLORS) === 'PREMIUM'
                    ? 'bg-pink-500/20 border-pink-500/30 text-pink-400'
                    : 'bg-slate-500/20 border-slate-500/30 text-slate-400'}`}
                  style={{ fontSize: '13px' }}>
                  {(user.rank as keyof typeof RANK_COLORS) === 'PREMIUM' ? '프리미엄' : '스탠다드'}
                </div>
              </div>
            </div>
          </div>

          {/* 중앙: 핵심 스탯 (가로 정렬) - 핑크 테마로 변경 */}
          <div className="flex items-center gap-2 justify-center">
            {/* 승리 수 */}
            <div className="inline-flex items-center gap-2 bg-pink-500/15 px-3 py-2 rounded-lg border border-pink-400/30
                           min-w-fit whitespace-nowrap">
              <Star size={16} className="fill-current text-pink-400 flex-shrink-0" />
              <div className="text-center">
                <div className="text-sm font-bold text-pink-400 leading-tight">{user.wins || 0}</div>
                <div className="text-xs text-pink-300 leading-tight">승리</div>
              </div>
            </div>

            {/* 연속 접속 */}
            <div className="inline-flex items-center gap-2 bg-purple-500/15 px-3 py-2 rounded-lg border border-purple-400/30
                           min-w-fit whitespace-nowrap">
              <TrendingUp size={16} className="text-purple-400 flex-shrink-0" />
              <div className="text-center">
                <div className="text-sm font-bold text-purple-400 leading-tight">{user.loginStreak || 0}</div>
                <div className="text-xs text-purple-300 leading-tight">일연속</div>
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
