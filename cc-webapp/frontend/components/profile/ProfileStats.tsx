'use client';

import { Coins, Flame, Trophy, Settings, Gift, ExternalLink } from 'lucide-react';
import type { ProfileStatsProps } from './types';

/**
 * 400px * 750px에 최적화된 통합 프로필 통계
 * 한국 사용자 경험에 맞춘 단일 컴포넌트
 */
export default function ProfileStats({ user }: ProfileStatsProps) {
  // 액션 핸들러들
  const handleChargeTokens = () => console.log('토큰 충전');
  const handleViewRewards = () => console.log('보상 페이지');
  const handleViewHistory = () => console.log('전적 보기');
  const handleSettings = () => console.log('설정');
  const handleClaimReward = () => console.log('연속 출석 보상 받기');

  return (
    <div className="rounded-xl py-8 relative overflow-hidden bg-gray-800/95 backdrop-blur-sm border border-gray-600/50 shadow-lg w-full"
         style={{ 
           paddingLeft: '32px', 
           paddingRight: '32px',
           maxWidth: '100% !important',
           width: '100% !important'
         }}>
      {/* 통합 색상 스킴 배경 효과 */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-700/30 via-transparent to-gray-900/30 pointer-events-none" />
      
      <div className="relative z-10 space-y-8">
        <div className="grid grid-cols-2 gap-8" role="region" aria-label="계정 통계">
          {/* 토큰 (가장 중요) */}
          <div className="bg-yellow-600/20 border border-yellow-500/30 
                          rounded-xl text-center focus-within:ring-2 focus-within:ring-yellow-400/50
                          shadow-[0_4px_12px_rgba(0,0,0,0.3)] hover:shadow-[0_6px_16px_rgba(0,0,0,0.4)]
                          transform hover:scale-[1.02] transition-all duration-300 ease-out
                          before:content-[''] before:absolute before:inset-0 before:rounded-xl
                          before:bg-gradient-to-br before:from-white/10 before:via-transparent before:to-black/5
                          before:pointer-events-none relative overflow-hidden"
               style={{ padding: '16px' }}
               tabIndex={0}
               role="button"
               aria-label={`보유 토큰 ${(user.cyber_token_balance || 0).toLocaleString()}개`}>
            <div className="flex flex-col items-center justify-center gap-1 relative z-10">
              <Coins className="w-4 h-4 text-yellow-300 drop-shadow-sm" />
              <span className="text-yellow-200 text-center drop-shadow-sm whitespace-nowrap" style={{ fontSize: '12px' }}>보유 토큰</span>
              <div className="text-white font-bold text-center drop-shadow-sm whitespace-nowrap" style={{ fontSize: '12px' }}>
                {(user.cyber_token_balance || 0).toLocaleString()}
              </div>
            </div>
          </div>
          
          {/* 연속 출석 */}
          <div className="bg-orange-600/20 border border-orange-500/30 
                          rounded-xl text-center focus-within:ring-2 focus-within:ring-orange-400/50
                          shadow-[0_4px_12px_rgba(0,0,0,0.3)] hover:shadow-[0_6px_16px_rgba(0,0,0,0.4)]
                          transform hover:scale-[1.02] transition-all duration-300 ease-out
                          before:content-[''] before:absolute before:inset-0 before:rounded-xl
                          before:bg-gradient-to-br before:from-white/10 before:via-transparent before:to-black/5
                          before:pointer-events-none relative overflow-hidden"
               style={{ padding: '16px' }}
               tabIndex={0}
               role="button"
               aria-label={`연속 출석 ${user.loginStreak || 0}일째`}>
            <div className="flex flex-col items-center justify-center gap-1 relative z-10">
              <Flame className="w-4 h-4 text-orange-300 drop-shadow-sm" />
              <span className="text-orange-200 text-center drop-shadow-sm whitespace-nowrap" style={{ fontSize: '12px' }}>연속 출석</span>
              <div className="text-white font-bold text-center drop-shadow-sm whitespace-nowrap" style={{ fontSize: '12px' }}>
                {user.loginStreak || 0}일
              </div>
            </div>
          </div>
          
          {/* 승리/미션 통계 */}
          <div className="bg-green-600/20 border border-green-500/30 
                          rounded-xl text-center focus-within:ring-2 focus-within:ring-green-400/50
                          shadow-[0_4px_12px_rgba(0,0,0,0.3)] hover:shadow-[0_6px_16px_rgba(0,0,0,0.4)]
                          transform hover:scale-[1.02] transition-all duration-300 ease-out
                          before:content-[''] before:absolute before:inset-0 before:rounded-xl
                          before:bg-gradient-to-br before:from-white/10 before:via-transparent before:to-black/5
                          before:pointer-events-none relative overflow-hidden"
               style={{ padding: '16px' }}
               tabIndex={0}
               role="button"
               aria-label={`총 ${user.wins || 0}승 달성`}>
            <div className="flex flex-col items-center justify-center gap-1 relative z-10">
              <Trophy className="w-4 h-4 text-green-300 drop-shadow-sm" />
              <span className="text-green-200 text-center drop-shadow-sm whitespace-nowrap" style={{ fontSize: '12px' }}>승리</span>
              <div className="text-white font-bold text-center drop-shadow-sm whitespace-nowrap" style={{ fontSize: '12px' }}>{user.wins || 0}</div>
            </div>
          </div>
          
          <div className="bg-purple-600/20 border border-purple-500/30 
                          rounded-xl text-center focus-within:ring-2 focus-within:ring-purple-400/50
                          shadow-[0_4px_12px_rgba(0,0,0,0.3)] hover:shadow-[0_6px_16px_rgba(0,0,0,0.4)]
                          transform hover:scale-[1.02] transition-all duration-300 ease-out
                          before:content-[''] before:absolute before:inset-0 before:rounded-xl
                          before:bg-gradient-to-br before:from-white/10 before:via-transparent before:to-black/5
                          before:pointer-events-none relative overflow-hidden"
               style={{ padding: '16px' }}
               tabIndex={0}
               role="button"
               aria-label={`${user.completedMissions || 0}개 미션 완료`}>
            <div className="flex flex-col items-center justify-center gap-1 relative z-10">
              <Gift className="w-4 h-4 text-purple-300 drop-shadow-sm" />
              <span className="text-purple-200 text-center drop-shadow-sm whitespace-nowrap" style={{ fontSize: '12px' }}>미션완료</span>
              <div className="text-white font-bold text-center drop-shadow-sm whitespace-nowrap" style={{ fontSize: '12px' }}>{user.completedMissions || 0}</div>
            </div>
          </div>
        </div>

        {/* 연속 출석 보상 - 통합 색상 스킴 */}
        {(user.loginStreak || 0) >= 7 && (
          <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 border-2 border-purple-500/30 
                          rounded-xl p-6 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
            <div className="relative z-10">
              {(user.loginStreak || 0) % 7 === 0 ? (
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2 mb-4">
                    <span className="text-lg font-bold text-green-300">
                      {user.loginStreak}일 연속 출석 달성! 🎉
                    </span>
                  </div>
                  <button 
                    onClick={handleClaimReward}
                    className="w-full h-14 bg-gradient-to-r from-green-600 to-emerald-600 
                               text-white font-bold rounded-lg hover:from-green-500 hover:to-emerald-500
                               transform hover:scale-105 active:scale-95 transition-all duration-200
                               shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
                  >
                    <Gift className="w-5 h-5" />
                    특별 보상 받기
                  </button>
                </div>
              ) : (
                <div className="text-center">
                  <div className="text-base font-medium text-purple-300 mb-2">
                    연속 출석 {user.loginStreak}일째
                  </div>
                  <div className="text-sm text-purple-200 whitespace-nowrap">
                    {7 - ((user.loginStreak || 0) % 7)}일 더 출석하면 특별 보상!
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 빠른 액션 버튼들 - 통합 색상 스킴 */}
        <div className="space-y-6">
          {/* Primary Actions */}
          <div className="grid grid-cols-2 gap-4">
            <button 
              onClick={handleChargeTokens}
              className="flex items-center justify-center gap-3 h-14 rounded-lg
                         text-white font-bold transform hover:scale-105 active:scale-95 transition-all duration-200
                         shadow-lg hover:shadow-xl text-base"
              style={{ 
                background: 'linear-gradient(to right, #2563eb, #7c3aed)',
                border: '2px solid rgba(96, 165, 250, 0.5)',
                borderRadius: '0.5rem'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #3b82f6, #8b5cf6)';
                e.currentTarget.style.borderColor = 'rgba(96, 165, 250, 0.7)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #2563eb, #7c3aed)';
                e.currentTarget.style.borderColor = 'rgba(96, 165, 250, 0.5)';
              }}
            >
              <Coins size={20} />
              <span>토큰 충전</span>
            </button>
            
            <button 
              onClick={handleViewRewards}
              className="flex items-center justify-center gap-3 h-14 rounded-lg
                         text-white font-bold transform hover:scale-105 active:scale-95 transition-all duration-200
                         shadow-lg hover:shadow-xl text-base"
              style={{ 
                background: 'linear-gradient(to right, #d97706, #ea580c)',
                border: '2px solid rgba(251, 191, 36, 0.5)',
                borderRadius: '0.5rem'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #f59e0b, #f97316)';
                e.currentTarget.style.borderColor = 'rgba(251, 191, 36, 0.7)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #d97706, #ea580c)';
                e.currentTarget.style.borderColor = 'rgba(251, 191, 36, 0.5)';
              }}
            >
              <Gift size={20} />
              <span>보상 받기</span>
            </button>
          </div>
          
          {/* 본사 사이트 바로가기 */}
          <div>
            <button 
              onClick={() => window.open('https://casinoclub.com', '_blank')}
              className="w-full flex items-center justify-center gap-3 h-14 rounded-lg
                         text-white font-bold transform hover:scale-105 active:scale-95 transition-all duration-200
                         shadow-lg hover:shadow-xl text-base"
              style={{ 
                background: 'linear-gradient(to right, #059669, #0d9488)',
                border: '2px solid rgba(52, 211, 153, 0.3)',
                borderRadius: '0.5rem'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #10b981, #14b8a6)';
                e.currentTarget.style.borderColor = 'rgba(52, 211, 153, 0.5)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #059669, #0d9488)';
                e.currentTarget.style.borderColor = 'rgba(52, 211, 153, 0.3)';
              }}
            >
              <ExternalLink size={20} />
              <span>본사 사이트 바로가기</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
