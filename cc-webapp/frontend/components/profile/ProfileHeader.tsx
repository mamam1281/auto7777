'use client';

import type { ProfileHeaderProps, RANK_COLORS } from './types';

export default function ProfileHeader({ user }: ProfileHeaderProps) {

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
        <div className="grid grid-cols-[auto_1fr_auto] gap-4 items-center">
          {/* 왼쪽: 간소화된 프로필 영역 */}
          <div className="flex items-center gap-1">
            <div className="w-12 h-12 rounded-full bg-gray-600 flex items-center justify-center">
              <span className="text-white font-bold text-lg">{user.nickname.charAt(0)}</span>
            </div>
          </div>

          {/* 닉네임과 배지들 - 자동 크기 조정 */}
          <div className="space-y-1">
            <h2 className="text-xl font-bold text-white leading-tight whitespace-nowrap">
              {user.nickname}
            </h2>
            <div className="flex items-center gap-2">
              {/* 프리미엄 배지만 표시 - 12-14px 폰트 크기 */}
              <div className={`inline-flex items-center px-3 py-1.5 font-semibold 
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

        {/* 하단 여백만 유지 */}
        <div className="mt-4" />
      </div>
    </div>
  );
}
